from nicegui import ui
import plotly.graph_objects as go
from modules.globalSettings import globalSettings
from ui.pages.components.dataHandler import DataHandler
from ui.pages.components.visualisation import RiskTrendVisualisation
from modules.calculations import calculateSharpeRatio, calculateVolatility, calculateTotalReturn
from modules.database.database import cursor, connection
import pickle

# data container for easy serialisation to cache page to save data locally when changing pages
class ChartsPageCache:
    def __init__(self, ticker, timeframe, title, chart_mode, data, currency, metrics):
        self.ticker = ticker
        self.timeframe = timeframe
        self.title = title
        self.chart_mode = chart_mode
        self.data = data 
        self.currency = currency
        self.metrics = metrics 

# global css for charts page
ui.add_css('''
    .input-field .q-field__native, .input-field .q-item__label {
        color: var(--custom-input-color) !important;
    }
    
    .input-field .q-field__label, 
    .input-field .q-field__native::placeholder {
        color: var(--custom-placeholder-color) !important;
    }

    .input-field .q-field__control:before {
        border-color: var(--custom-input-color) !important;
        opacity: 0.5; 
    }

    .input-field .q-field__control:hover:before {
        border-color: var(--custom-input-color) !important;
        opacity: 1;
    }

    .q-manual-focusable--focused > .q-focus-helper,
    .q-item--active, 
    .q-item.q-item--clickable:hover {
        background: var(--custom-accent-soft) !important;
        color: var(--custom-input-color) !important;
        opacity: 1 !important;
    }

    .q-item.q-item--active .q-item__section {
        color: var(--custom-input-color) !important;
    }
''', shared=True)

# charts page class
class ChartsPage:
    # constructor/initialiser
    def __init__(self):
        self.__settings = globalSettings
        self.__ticker_input = None 
        self.__title_input = None
        self.__timeframe_dropdown = None
        self.__chart_container = None 
        self.__metrics_container = None
        
        # initialises default state variables
        self._current_processed_data = None
        self._current_currency = "USD"
        self.__chart_mode = 'Line'
        self._current_metrics = {}
        
        # load state (overwrites defaults if successful)
        self.__load_state()

    # method for loading state from cache
    def __load_state(self):

        # set defaults first (prevents AttributeError if DB lookup fails)
        self.__saved_ticker = 'AAPL'
        self.__saved_timeframe = '1y'
        self.__saved_title = ''
        self.__has_saved_state = False

        try:
            # check if table exists to avoid SQL errors on first run
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ChartsPageCacheTable'")
            if not cursor.fetchone():
                # table doesn't exist, stick with defaults
                return 

            # load state from cache
            cursor.execute("SELECT data FROM ChartsPageCacheTable WHERE id = 1")

            # get row of charts page data
            row = cursor.fetchone()
            
            if row:
                # load charts page data from cache
                cached_obj : ChartsPageCache = pickle.loads(row[0])
                
                # restore state variables
                self.__saved_ticker = cached_obj.ticker
                self.__saved_timeframe = cached_obj.timeframe
                self.__saved_title = cached_obj.title
                self.__chart_mode = cached_obj.chart_mode
                self._current_processed_data = cached_obj.data
                self._current_currency = cached_obj.currency
                self._current_metrics = cached_obj.metrics
                
                self.__has_saved_state = True
                
        except Exception as e:
            print(f"Error loading chart state: {e}")
            # defaults are already set above, so safe here

    def __save_state(self):
        try:
            # create the data container
            cache_obj = ChartsPageCache(
                ticker=self.__ticker_input.value,
                timeframe=self.__timeframe_dropdown.value,
                title=self.__title_input.value,
                chart_mode=self.__chart_mode,
                data=self._current_processed_data,
                currency=self._current_currency,
                metrics=self._current_metrics
            )

            # serialise data container
            binary_data = pickle.dumps(cache_obj)

            # ensure table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ChartsPageCacheTable (
                    id INTEGER PRIMARY KEY CHECK (id = 1), 
                    data BLOB
                )
            """)

            # upsert logic (insert or replace)
            cursor.execute("""
                INSERT OR REPLACE INTO ChartsPageCacheTable (id, data) 
                VALUES (1, ?)
            """, (binary_data,))

            connection.commit()
            
        except Exception as e:
            ui.notify(f"Failed to save state: {str(e)}", color='negative')

    # method for toggling the chart type
    def __toggle_chart_type(self):
        self.__chart_mode = 'Candlestick' if self.__chart_mode == 'Line' else 'Line'
        
        # update button icon with safety check
        if hasattr(self, '_ChartsPage__toggle_btn'):
            self.__toggle_btn.props(f'icon={"candlestick_chart" if self.__chart_mode == "Candlestick" else "show_chart"}')
        
        # update chart if data is available
        if self._current_processed_data is not None:
            self.__generate_chart(use_cached=True)
            self.__save_state()

    # method for rendering the page
    def render(self):
        # get the settings from singleton object
        theme = self.__settings.theme

        # consistent variables for CSS
        input_style = (
            f'--custom-input-color: {theme.text_primary}; '
            f'--custom-placeholder-color: {theme.text_placeholder}; '
            f'--custom-accent-soft: {theme.sb_active_bg}; '
            f'--q-primary: {theme.accent};'
        )
        
        dropdown_popup_style = (
            f'background-color: {theme.surface} !important; '
            f'color: {theme.text_primary} !important;'
        )
        

        btn_style = f'background-color: {theme.sb_active_bg} !important; color: {theme.sb_active_fg} !important;'

        # render the page
        with ui.element('div').classes('w-full h-full flex flex-col p-8 gap-6'):
            
            # title text
            ui.label('Chart Analysis').style(f'color: {theme.text_primary}; font-size: 200%; font-weight: bold')

            # row of inputs
            with ui.row().classes('w-full items-end gap-4'):
                
                # ticker input box
                self.__ticker_input = ui.input(label='Ticker Symbol', value=self.__saved_ticker) \
                    .classes('w-32 input-field') \
                    .props('outlined dense uppercase') \
                    .style(input_style)
                
                # timeframe dropdown
                timeframe_options = {
                    '1mo': '1 Month', 
                    '6mo': '6 Months', '1y': 'Year to Date', 'max': 'Max'
                }
                self.__timeframe_dropdown = ui.select(
                    label='Timeframe', 
                    options=timeframe_options, 
                    value=self.__saved_timeframe
                ).classes('w-40 input-field').style(input_style).props(
                    f'outlined dense '
                    f'popup-content-class="input-field" '
                    f'popup-content-style="{dropdown_popup_style}" '
                    f'input-style="color: {theme.text_primary}"'
                )

                # optional title input box
                self.__title_input = ui.input(label='Custom Title (Optional)', value=self.__saved_title) \
                    .classes('w-64 input-field') \
                    .props('outlined dense') \
                    .style(input_style)
                
                # row of buttons
                with ui.row().classes('gap-2'):

                    # generate chart button
                    ui.button('Generate Chart', on_click=lambda: self.__generate_chart(use_cached=False)) \
                        .style(btn_style).classes('shadow-sm font-bold').props('flat unelevated')
                    
                    # add to home button
                    ui.button('Add to Home', on_click=lambda: ui.notify('Widget Configuration Saved', color='positive')) \
                        .style(btn_style).classes('shadow-sm font-bold').props('flat unelevated')
                    
                    # toggle chart type button  
                    icon_name = 'candlestick_chart' if self.__chart_mode == "Candlestick" else "show_chart"
                    self.__toggle_btn = ui.button(icon=icon_name, on_click=self.__toggle_chart_type) \
                        .style(btn_style).props('flat unelevated')
                    
                    # clear chart button
                    ui.button('Clear', on_click=self.__clear_chart) \
                        .style(btn_style).classes('shadow-sm font-bold').props('flat unelevated icon=delete')

            # chart container
            self.__chart_container = ui.element('div').classes('w-full flex-grow rounded-xl shadow-sm border border-gray-100/10 p-4 relative') \
                .style(f'background-color: {theme.surface}')
            
            # metrics container
            self.__metrics_container = ui.row().classes('w-full justify-center p-4 mt-2')
            
            with self.__chart_container:
                # render chart
                if self.__has_saved_state and self._current_processed_data is not None:
                    self.__generate_chart(use_cached=True)
                else:
                    self.__render_empty_chart()

    # method for clearing the chart and deleting from DB
    def __clear_chart(self):
        try:
            # delete from db
            cursor.execute("DELETE FROM ChartsPageCacheTable WHERE id = 1")
            connection.commit()
            
            # reset internal state
            self._current_processed_data = None
            self._current_metrics = {}
            # reset to default
            self.__saved_ticker = 'AAPL' 
            self.__saved_timeframe = '1y'
            self.__saved_title = ''
            self.__has_saved_state = False
            
            # reset inputs
            if self.__ticker_input:
                self.__ticker_input.value = self.__saved_ticker
            if self.__title_input:
                self.__title_input.value = self.__saved_title
            if self.__timeframe_dropdown:
                self.__timeframe_dropdown.value = self.__saved_timeframe
                
            # clear/ reset UI
            self.__metrics_container.clear()
            self.__render_empty_chart()
            
            # notify user
            ui.notify('Chart cleared and saved state deleted.', color='positive')
            
        # handle errors gracefully
        except Exception as e:
            ui.notify(f"Error clearing chart: {str(e)}", color='negative')
            print(f"Error clearing chart: {e}")

    # method for rendering an empty chart (default state)
    def __render_empty_chart(self):
        theme = self.__settings.theme
        layout = go.Layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=theme.text_secondary),
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False),
            annotations=[dict(
                text="Configure parameters and press Generate",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=18, color=theme.text_placeholder)
            )]
        )
        fig = go.Figure(layout=layout)
        self.__chart_container.clear()
        with self.__chart_container:
            ui.plotly(fig).classes('w-full h-full')

    # method for generating a chart
    def __generate_chart(self, use_cached=False):
        ticker = self.__ticker_input.value
        timeframe = self.__timeframe_dropdown.value
        
        # validate input
        if not ticker:
            ui.notify('Please enter a ticker symbol.', type='warning')
            return

        try:
            # check if we can use cached data
            if use_cached and self._current_processed_data is not None:
                processed_data = self._current_processed_data
                currency = self._current_currency
                if self._current_metrics:
                    sharpe_val = self._current_metrics['sharpe']
                    vol_val = self._current_metrics['vol']
                    ret_val = self._current_metrics['ret']
                else:
                    sharpe_val = calculateSharpeRatio(processed_data)
                    vol_val = calculateVolatility(processed_data)
                    ret_val = calculateTotalReturn(processed_data)
            else:
                handler = DataHandler()
                handler.ticker_symbol = ticker
                handler.period = timeframe
                handler.fetch_market_data()
                processed_data = handler.prepare_risk_data()
                
                self._current_processed_data = processed_data
                self._current_currency = handler.currency
                currency = handler.currency
                
                sharpe_val = calculateSharpeRatio(processed_data)
                vol_val = calculateVolatility(processed_data)
                ret_val = calculateTotalReturn(processed_data)
                
                self._current_metrics = {
                    'sharpe': sharpe_val,
                    'vol': vol_val,
                    'ret': ret_val
                }
            
            # create visualisation object
            viz = RiskTrendVisualisation(
                title_input=self.__title_input.value or f"{ticker.upper()} Trend",
                data_input=processed_data,
                currency_input=currency
            )
            
            # generate chart
            fig = viz.generate_chart(chart_mode=self.__chart_mode)
            
            # update layout
            fig.update_layout(
                xaxis=dict(
                    title="Date",
                    showgrid=True,
                    showticklabels=True,
                    gridcolor='rgba(128,128,128,0.1)'
                ),
                yaxis=dict(
                    title=f"Price ({currency})",
                    showgrid=True,
                    showticklabels=True,
                    gridcolor='rgba(128,128,128,0.1)'
                ),
                hovermode="x unified"
            )

            # update hover templates
            for trace in fig.data:
                date_fmt = "%{x|%d %b %Y}"
                if trace.type == 'candlestick':
                    trace.hovertemplate = (
                        f"<b>Day={date_fmt}</b><br>"
                        "Open=%{open:.2f}<br>"
                        "High=%{high:.2f}<br>"
                        "Low=%{low:.2f}<br>"
                        "Close=%{close:.2f}<extra></extra>"
                    )
                else:
                    trace.hovertemplate = (
                        f"<b>Price=%{{y:.2f}}</b><br>"
                        f"Day={date_fmt}<extra></extra>"
                    )

            # update UI
            self.__chart_container.clear()
            with self.__chart_container:
                ui.plotly(fig).classes('w-full h-full')

            # update metrics
            self.__metrics_container.clear()
            with self.__metrics_container.classes('w-full grid grid-cols-1 md:grid-cols-3 gap-4'):
                
                sharpe_status = "High Performance" if sharpe_val > 1 else "Sub-optimal"
                self.createMetricCard('Sharpe Ratio', f'{sharpe_val:.2f}', sharpe_status, 
                                     'positive' if sharpe_val > 1 else 'warning')
                
                vol_status = "High Risk" if vol_val > 0.35 else "Stable"
                self.createMetricCard('Annual Volatility', f'{vol_val:.2%}', vol_status,
                                     'warning' if vol_val > 0.35 else 'positive')
                
                ret_status = "Profitable" if ret_val > 0 else "Loss"
                self.createMetricCard('Total Return', f'{ret_val:.2f}%', ret_status,
                                     'positive' if ret_val > 0 else 'negative')
            
            # save state in cache
            self.__save_state()

        # handle errors properly
        except Exception as e:
            ui.notify(f"Error: {str(e)}", type='negative')
            print(e)
        
    # method for creating metric cards at bottom of page
    def createMetricCard(self, title_text, value_text, status_label, badge_color):
        theme = self.__settings.theme
        with ui.card().classes('items-center p-6 bg-transparent border border-gray-100/10 shadow-none'):
            ui.label(title_text).style(f'color: {theme.text_secondary}; font-size: 0.9rem')
            ui.label(value_text).style(f'color: {theme.text_primary}; font-size: 2.8rem; font-weight: bold')
            ui.badge(status_label, color=badge_color).props('outline')
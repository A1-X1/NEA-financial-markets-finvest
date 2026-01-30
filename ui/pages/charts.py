from nicegui import ui
import plotly.graph_objects as go
from modules.globalSettings import globalSettings
from ui.pages.components.dataHandler import DataHandler
from ui.pages.components.visualisation import RiskTrendVisualisation
from modules.calculations import calculateSharpeRatio, calculateVolatility, calculateTotalReturn
from modules.database.database import cursor, connection
import pickle

# --- DATA CONTAINER FOR PICKLING ---
class ChartsPageCache:
    """Simple container to store the state of the Charts Page."""
    def __init__(self, ticker, timeframe, title, chart_mode, data, currency, metrics):
        self.ticker = ticker
        self.timeframe = timeframe
        self.title = title
        self.chart_mode = chart_mode
        self.data = data 
        self.currency = currency
        self.metrics = metrics 

# --- GLOBAL CSS ---
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

class ChartsPage:
    def __init__(self):
        self.__settings = globalSettings
        self.__ticker_input = None 
        self.__title_input = None
        self.__timeframe_dropdown = None
        self.__chart_container = None 
        self.__metrics_container = None
        
        # Initialize default state variables
        self._current_processed_data = None
        self._current_currency = "USD"
        self.__chart_mode = 'Line'
        self._current_metrics = {}
        
        # Load state (overwrites defaults if successful)
        self.__load_state()

    def __load_state(self):
        """Loads the pickled state from SQLite if it exists."""
        # 1. SET DEFAULTS FIRST (Prevents AttributeError if DB fails)
        self.__saved_ticker = 'AAPL'
        self.__saved_timeframe = '1y'
        self.__saved_title = ''
        self.__has_saved_state = False

        try:
            # Check if table exists to avoid loud SQL errors on first run
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ChartsPageCacheTable'")
            if not cursor.fetchone():
                return # Table doesn't exist, stick with defaults

            cursor.execute("SELECT data FROM ChartsPageCacheTable WHERE id = 1")
            row = cursor.fetchone()
            
            if row:
                cached_obj : ChartsPageCache = pickle.loads(row[0])
                
                # Restore state variables
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
            # Defaults are already set above, so we are safe here.

    def __save_state(self):
        """Saves the current inputs and data to SQLite using pickle."""
        try:
            # Create the data container
            cache_obj = ChartsPageCache(
                ticker=self.__ticker_input.value,
                timeframe=self.__timeframe_dropdown.value,
                title=self.__title_input.value,
                chart_mode=self.__chart_mode,
                data=self._current_processed_data,
                currency=self._current_currency,
                metrics=self._current_metrics
            )
            
            binary_data = pickle.dumps(cache_obj)

            # Ensure table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ChartsPageCacheTable (
                    id INTEGER PRIMARY KEY CHECK (id = 1), 
                    data BLOB
                )
            """)

            # Upsert logic (Insert or Replace)
            cursor.execute("""
                INSERT OR REPLACE INTO ChartsPageCacheTable (id, data) 
                VALUES (1, ?)
            """, (binary_data,))

            connection.commit()
            
        except Exception as e:
            ui.notify(f"Failed to save state: {str(e)}", color='negative')

    def __toggle_chart_type(self):
        self.__chart_mode = 'Candlestick' if self.__chart_mode == 'Line' else 'Line'
        
        # Update button icon
        if hasattr(self, '_ChartsPage__toggle_btn'): # Safety check
            self.__toggle_btn.props(f'icon={"candlestick_chart" if self.__chart_mode == "Candlestick" else "show_chart"}')
        
        if self._current_processed_data is not None:
            self.__generate_chart(use_cached=True)
            self.__save_state()

    def render(self):
        theme = self.__settings.theme

        # Consistent Variables for CSS
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

        with ui.element('div').classes('w-full h-full flex flex-col p-8 gap-6'):
            
            ui.label('Chart Analysis').style(f'color: {theme.text_primary}; font-size: 200%; font-weight: bold')

            with ui.row().classes('w-full items-end gap-4'):
                
                # Ticker Input
                self.__ticker_input = ui.input(label='Ticker Symbol', value=self.__saved_ticker) \
                    .classes('w-32 input-field') \
                    .props('outlined dense uppercase') \
                    .style(input_style)
                
                # Timeframe Dropdown 
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

                # Optional Title Input
                self.__title_input = ui.input(label='Custom Title (Optional)', value=self.__saved_title) \
                    .classes('w-64 input-field') \
                    .props('outlined dense') \
                    .style(input_style)
                
                with ui.row().classes('gap-2'):
                    ui.button('Generate Chart', on_click=lambda: self.__generate_chart(use_cached=False)) \
                        .style(btn_style).classes('shadow-sm font-bold').props('flat unelevated')
                    
                    ui.button('Add to Home', on_click=lambda: ui.notify('Widget Configuration Saved', color='positive')) \
                        .style(btn_style).classes('shadow-sm font-bold').props('flat unelevated')
                    
                    icon_name = 'candlestick_chart' if self.__chart_mode == "Candlestick" else "show_chart"
                    self.__toggle_btn = ui.button(icon=icon_name, on_click=self.__toggle_chart_type) \
                        .style(btn_style).props('flat unelevated')
                    
                    ui.button('Clear', on_click=self.__clear_chart) \
                        .style(btn_style).classes('shadow-sm font-bold').props('flat unelevated icon=delete')

            self.__chart_container = ui.element('div').classes('w-full flex-grow rounded-xl shadow-sm border border-gray-100/10 p-4 relative') \
                .style(f'background-color: {theme.surface}')
            
            self.__metrics_container = ui.row().classes('w-full justify-center p-4 mt-2')
            
            with self.__chart_container:
                if self.__has_saved_state and self._current_processed_data is not None:
                    self.__generate_chart(use_cached=True)
                else:
                    self.__render_empty_chart()

    def __clear_chart(self):
        """Clears the chart, resets state, and deletes record from DB."""
        try:
            # 1. Delete from DB
            cursor.execute("DELETE FROM ChartsPageCacheTable WHERE id = 1")
            connection.commit()
            
            # 2. Reset Internal State
            self._current_processed_data = None
            self._current_metrics = {}
            self.__saved_ticker = 'AAPL' # Reset to default or empty
            self.__saved_timeframe = '1y'
            self.__saved_title = ''
            self.__has_saved_state = False
            
            # 3. Reset Inputs
            if self.__ticker_input:
                self.__ticker_input.value = self.__saved_ticker
            if self.__title_input:
                self.__title_input.value = self.__saved_title
            if self.__timeframe_dropdown:
                self.__timeframe_dropdown.value = self.__saved_timeframe
                
            # 4. Clear/Reset UI
            self.__metrics_container.clear()
            self.__render_empty_chart()
            
            ui.notify('Chart cleared and saved state deleted.', color='positive')
            
        except Exception as e:
            ui.notify(f"Error clearing chart: {str(e)}", color='negative')
            print(f"Error clearing chart: {e}")

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

    def __generate_chart(self, use_cached=False):
        ticker = self.__ticker_input.value
        timeframe = self.__timeframe_dropdown.value
        
        if not ticker:
            ui.notify('Please enter a ticker symbol.', type='warning')
            return

        try:
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
            
            viz = RiskTrendVisualisation(
                title_input=self.__title_input.value or f"{ticker.upper()} Trend",
                data_input=processed_data,
                currency_input=currency
            )
            
            fig = viz.generate_chart(chart_mode=self.__chart_mode)

            theme = self.__settings.theme
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

            self.__chart_container.clear()
            with self.__chart_container:
                ui.plotly(fig).classes('w-full h-full')

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
            
            self.__save_state()

        except Exception as e:
            ui.notify(f"Error: {str(e)}", type='negative')
            print(e)
        
    def createMetricCard(self, title_text, value_text, status_label, badge_color):
        theme = self.__settings.theme
        with ui.card().classes('items-center p-6 bg-transparent border border-gray-100/10 shadow-none'):
            ui.label(title_text).style(f'color: {theme.text_secondary}; font-size: 0.9rem')
            ui.label(value_text).style(f'color: {theme.text_primary}; font-size: 2.8rem; font-weight: bold')
            ui.badge(status_label, color=badge_color).props('outline')
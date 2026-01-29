from nicegui import ui
import plotly.graph_objects as go
from modules.globalSettings import globalSettings
from ui.pages.components.dataHandler import DataHandler
from ui.pages.components.visualisation import RiskTrendVisualisation
from modules.calculations import calculateSharpeRatio, calculateVolatility, calculateTotalReturn


# GLOBAL CSS 
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

    /* 1. HOVER HIGHLIGHT: Customizes the background and text color when hovering over items */
    .q-manual-focusable--focused > .q-focus-helper,
    .q-item--active, 
    .q-item.q-item--clickable:hover {
        background: var(--custom-accent-soft) !important;
        color: var(--custom-input-color) !important;
        opacity: 1 !important;
    }

    /* 2. SELECTION OVERRIDE: Ensures the checkmark or active item uses the correct text color */
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
        # Initialize storage for cached data
        self._current_processed_data = None
        self._current_currency = "USD"

    def __toggle_chart_type(self):
        # 1. Toggle the state
        self.__chart_mode = 'Candlestick' if self.__chart_mode == 'Line' else 'Line'
        
        # 2. Update button icon/label for visual feedback
        self.__toggle_btn.props(f'icon={"candlestick_chart" if self.__chart_mode == "Candlestick" else "show_chart"}')
        
        # 3. Re-run generation logic if data exists
        if self._current_processed_data is not None:
            self.__generate_chart(use_cached=True)

    def render(self):
        theme = self.__settings.theme

        self.__chart_mode = 'Line' # Initial state
        
        # Consistent Variables for CSS
        input_style = (
            f'--custom-input-color: {theme.text_primary}; '
            f'--custom-placeholder-color: {theme.text_placeholder}; '
            f'--custom-accent-soft: {theme.sb_active_bg}; ' # Using sidebutton active bg for hover
            f'--q-primary: {theme.accent};'
        )

        # Dropdown Specific Styles
        dropdown_popup_style = (
            f'background-color: {theme.surface} !important; '
            f'color: {theme.text_primary} !important;'
        )
        
        btn_style = f'background-color: {theme.sb_active_bg} !important; color: {theme.sb_active_fg} !important;'

        with ui.element('div').classes('w-full h-full flex flex-col p-8 gap-6'):
            
            ui.label('Chart Analysis').style(f'color: {theme.text_primary}; font-size: 200%; font-weight: bold')

            with ui.row().classes('w-full items-end gap-4'):
                
                # Ticker Input
                self.__ticker_input = ui.input(label='Ticker Symbol', value='AAPL') \
                    .classes('w-32 input-field') \
                    .props('outlined dense uppercase') \
                    .style(input_style)
                
                # Timeframe Dropdown 
                timeframe_options = {
                    '1mo': '1 Month', 
                    '6mo': '6 Months', '1y': 'Year to Date', 'max': 'Max'
                }
                # apply 'input-field' class to the dropdown so it picks up the global CSS
                self.__timeframe_dropdown = ui.select(
                    label='Timeframe', 
                    options=timeframe_options, 
                    value='1y'
                ).classes('w-40 input-field').style(input_style).props(
                    f'outlined dense '
                    f'popup-content-class="input-field" '
                    f'popup-content-style="{dropdown_popup_style}" '
                    f'input-style="color: {theme.text_primary}"'
                )

                # Optional Title Input
                self.__title_input = ui.input(label='Custom Title (Optional)') \
                    .classes('w-64 input-field') \
                    .props('outlined dense') \
                    .style(input_style)
                
                with ui.row().classes('gap-2'):
                    ui.button('Generate Chart', on_click=lambda: self.__generate_chart(use_cached=False)) \
                        .style(btn_style).classes('shadow-sm font-bold').props('flat unelevated')
                    
                    ui.button('Add to Home', on_click=lambda: ui.notify('Widget Configuration Saved', color='positive')) \
                        .style(btn_style).classes('shadow-sm font-bold').props('flat unelevated')
                    
                    self.__toggle_btn = ui.button(icon='show_chart', on_click=self.__toggle_chart_type) \
                        .style(btn_style).props('flat unelevated')

            self.__chart_container = ui.element('div').classes('w-full flex-grow rounded-xl shadow-sm border border-gray-100/10 p-4 relative') \
                .style(f'background-color: {theme.surface}')
            
            # --- Metrics Area ---
            # This container sits directly below the chart
            self.__metrics_container = ui.row().classes('w-full justify-center p-4 mt-2')
            
            with self.__chart_container:
                self.__render_empty_chart()

    def __render_empty_chart(self):
        """Renders the placeholder before data is loaded."""
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
            # 1. Logic to handle caching vs fetching new data
            if use_cached and self._current_processed_data is not None:
                processed_data = self._current_processed_data
                currency = self._current_currency
            else:
                handler = DataHandler()
                handler.ticker_symbol = ticker
                handler.period = timeframe
                handler.fetch_market_data()
                processed_data = handler.prepare_risk_data()
                
                # Cache the data
                self._current_processed_data = processed_data
                self._current_currency = handler.currency
                currency = handler.currency
            
            # 2. Calculate Metrics
            sharpe_val = calculateSharpeRatio(processed_data)
            vol_val = calculateVolatility(processed_data)
            ret_val = calculateTotalReturn(processed_data)

            # 3. Create Visualisation
            viz = RiskTrendVisualisation(
                title_input=self.__title_input.value or f"{ticker.upper()} Trend",
                data_input=processed_data,
                currency_input=currency
            )
            
            # Generate the base figure
            fig = viz.generate_chart(chart_mode=self.__chart_mode)

            # ---------------------------------------------------------
            # CUSTOM OVERRIDES (Fixing Axes and Tooltips)
            # ---------------------------------------------------------
            theme = self.__settings.theme
            
            # A. Fix Axes Labels (Ensure they are visible)
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
                hovermode="x unified" # Shows tooltip for all traces at this X-coordinate
            )

            # B. Fix Tooltips (Formatted as requested)
            for trace in fig.data:
                # Common date format for X axis
                date_fmt = "%{x|%d %b %Y}" # e.g., 01 Jan 2023
                
                if trace.type == 'candlestick':
                    # Candlestick hover template
                    trace.hovertemplate = (
                        f"<b>Day={date_fmt}</b><br>"
                        "Open=%{open:.2f}<br>"
                        "High=%{high:.2f}<br>"
                        "Low=%{low:.2f}<br>"
                        "Close=%{close:.2f}<extra></extra>"
                    )
                else:
                    # Line chart hover template (Price={value})
                    trace.hovertemplate = (
                        f"<b>Price=%{{y:.2f}}</b><br>"
                        f"Day={date_fmt}<extra></extra>"
                    )

            # ---------------------------------------------------------

            self.__chart_container.clear()
            with self.__chart_container:
                ui.plotly(fig).classes('w-full h-full')

            # Update Main UI Metrics Container
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

        except Exception as e:
            ui.notify(f"Error: {str(e)}", type='negative')
        
    def createMetricCard(self, title_text, value_text, status_label, badge_color):
        """Helper to create interpreted metric cards for the NEA stakeholder."""
        theme = self.__settings.theme
        with ui.card().classes('items-center p-6 bg-transparent border border-gray-100/10 shadow-none'):
            ui.label(title_text).style(f'color: {theme.text_secondary}; font-size: 0.9rem')
            ui.label(value_text).style(f'color: {theme.text_primary}; font-size: 2.8rem; font-weight: bold')
            ui.badge(status_label, color=badge_color).props('outline')
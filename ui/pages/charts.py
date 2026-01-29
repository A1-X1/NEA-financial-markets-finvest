from nicegui import ui
import plotly.graph_objects as go
from modules.globalSettings import globalSettings
from ui.pages.components.dataHandler import DataHandler
from ui.pages.components.visualisation import RiskTrendVisualisation

# FIX PRICE CONVERSIONS

# --- GLOBAL CSS (Advanced Customization for OCR NEA) ---
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

    def render(self):
        theme = self.__settings.theme
        
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
                    '1d': '1 Day', '5d': '5 Days', '1mo': '1 Month', 
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
                    ui.button('Generate Chart', on_click=self.__generate_chart) \
                        .style(btn_style).classes('shadow-sm font-bold').props('flat unelevated')
                    
                    ui.button('Add to Home', on_click=lambda: ui.notify('Widget Configuration Saved', color='positive')) \
                        .style(btn_style).classes('shadow-sm font-bold').props('flat unelevated')

            self.__chart_container = ui.element('div').classes('w-full flex-grow rounded-xl shadow-sm border border-gray-100/10 p-4 relative') \
                .style(f'background-color: {theme.surface}')
            
            with self.__chart_container:
                self.__render_empty_chart()

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

    def __generate_chart(self):
        ticker = self.__ticker_input.value
        custom_title = self.__title_input.value
        timeframe = self.__timeframe_dropdown.value
        
        if not ticker:
            ui.notify('Please enter a ticker symbol.', type='warning')
            return

        ui.notify(f'Loading {ticker}...', color='positive', timeout=1000)

        try:
            handler = DataHandler()
            handler.ticker_symbol = ticker
            handler.period = timeframe
            print(f'TimeFrame: {handler.period}')
            handler.fetch_market_data()
            
            processed_data = handler.prepare_risk_data()
            currency = handler.currency

            final_title = custom_title if custom_title and len(custom_title.strip()) >= 3 \
                         else f"{ticker.upper()} Price Trend"

            viz = RiskTrendVisualisation(
                title_input=final_title,
                data_input=processed_data,
                currency_input=currency
            )
            fig = viz.generate_chart()

            self.__chart_container.clear()
            with self.__chart_container:
                ui.plotly(fig).classes('w-full h-full')

        except Exception as e:
            ui.notify(f"Error: {str(e)}", type='negative')
            self.__render_empty_chart()
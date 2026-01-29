from nicegui import ui
import plotly.graph_objects as go
from modules.globalSettings import globalSettings
from ui.pages.components.dataHandler import DataHandler
from ui.pages.components.visualisation import RiskTrendVisualisation

# --- 1. GLOBAL CSS UPDATED (AO3: UI Polish) ---
ui.add_css('''
    .input-field .q-field__native {
        color: var(--custom-input-color) !important;
    }
    
    /* Targets the label/placeholder text color */
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
''', shared=True)

class ChartsPage:
    def __init__(self):
        self.__settings = globalSettings
        self.__ticker_input = None 
        self.__chart_container = None 

    def render(self):
        theme = self.__settings.theme
        
        # Define button styles
        btn_style = f'background-color: {theme.sb_active_bg} !important; color: {theme.sb_active_fg} !important;'
        btn_classes = f'shadow-sm font-bold'
        btn_props = f'flat unelevated'

        # --- DYNAMIC INPUT STYLING ---
        # We now map text_placeholder to our new CSS variable
        input_style = (
            f'--custom-input-color: {theme.text_primary}; '
            f'--custom-placeholder-color: {theme.text_placeholder}; '
            f'--q-primary: {theme.accent};' # The border turns to accent color on focus
        )

        with ui.element('div').classes('w-full h-full flex flex-col p-8 gap-6'):
            
            ui.label('Market Analysis').style(f'color: {theme.text_primary}; font-size: 200%; font-weight: bold')

            with ui.row().classes('w-full items-end gap-4'):
                
                # The label here will now use theme.text_placeholder
                self.__ticker_input = ui.input(label='Ticker Symbol', value='AAPL') \
                    .classes('w-48 input-field') \
                    .props('outlined dense') \
                    .style(input_style)
                
                ui.button('Generate Chart', on_click=self.__generate_chart) \
                    .style(btn_style).classes(btn_classes) \
                    .props(btn_props)
                
                ui.button('Add to Home', on_click=lambda: ui.notify('Feature coming soon...', color='grey')) \
                    .style(btn_style).classes(btn_classes) \
                    .props(btn_props)

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
                text="Enter a Ticker and press Generate",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20, color=theme.text_placeholder)
            )]
        )
        fig = go.Figure(layout=layout)
        self.__chart_container.clear()
        with self.__chart_container:
            ui.plotly(fig).classes('w-full h-full')

    def __generate_chart(self):
        ticker = self.__ticker_input.value
        if not ticker:
            ui.notify('Please enter a ticker symbol.', type='warning')
            return

        ui.notify(f'Fetching data for {ticker}...', color='positive', timeout=1000)

        try:
            handler = DataHandler()
            handler.ticker_symbol = ticker
            handler.period = '1y'
            handler.fetch_market_data()
            
            processed_data = handler.prepare_risk_data()
            currency = handler.currency

            viz = RiskTrendVisualisation(
                title_input=f"{ticker.upper()} Price Trend",
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
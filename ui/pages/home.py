from nicegui import ui
from modules.globalSettings import GlobalSettings, globalSettings
from ui.pages.components.homeWidget import HomeWidget, MarketChartWidget
from ui.pages.components.newHomeWidget import NewHomeWidget
import plotly.graph_objects as go
from currency_codes import Currency

class HomePage:
    def __init__(self):
        self.__settings = globalSettings

    def render(self):
        colours = self.__settings.theme
        
        # 1. OUTER CONTAINER: Centers content on screen and adds top margin
        with ui.element('div').classes('w-full flex flex-col items-center mt-8 pb-10'):
            
            # 2. INNER CONTAINER: Limits width to 1280px (max-w-7xl) and takes 90% of mobile screens
            with ui.element('div').classes('w-[90%] max-w-7xl flex flex-col gap-8'):
                
                # --- HEADER ROW (Title + Currency Badge) ---
                with ui.row().classes('w-full justify-between items-center'):
                    ui.label('Dashboard').style(f'color: {colours.text_primary}; font-size: 200%; font-weight: bold')
                    
                    # Small badge for currency
                    with ui.element('div').classes('px-4 py-2 rounded-full shadow-sm flex items-center gap-2') \
                            .style(f'background-color: {colours.surface}'):
                        ui.icon('monetization_on').style(f'color: {colours.accent}')
                        ui.label(f'{self.__settings.currencySymbol}{self.__settings.currency.code}').style(f'color: {colours.text_primary}; font-weight: 600')

                # --- GRID LAYOUT ---
                # grid-cols-1: Mobile (1 column)
                # md:grid-cols-2: Tablet (2 columns)
                # lg:grid-cols-3: Desktop (3 columns)
                with ui.element('div').classes('w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'):

                    # --- WIDGET 1: RISK METRIC ---
                    widget1 = HomeWidget("Risk Metric")
                    with widget1.content:
                        # Create Chart
                        fig = go.Figure(go.Scatter(
                            x=[1, 2, 3, 4], 
                            y=[1, 2, 3, 2.5],
                            mode='lines+markers',
                            line=dict(color=colours.accent, width=3)
                        ))
                        
                        # Style Chart to match Theme (Transparent background)
                        fig.update_layout(
                            margin=dict(l=20, r=20, t=10, b=20),
                            paper_bgcolor='rgba(0,0,0,0)', # Transparent
                            plot_bgcolor='rgba(0,0,0,0)',  # Transparent
                            xaxis=dict(showgrid=False, showticklabels=False),
                            yaxis=dict(showgrid=True, gridcolor=colours.sb_inactive_fg, showticklabels=True),
                            font=dict(color=colours.text_secondary)
                        )
                        
                        # Render Chart (h-full makes it fill the widget body)
                        ui.plotly(fig).classes('w-full h-full')

                    # --- WIDGET 2: EXAMPLE ---
                    widget2 = HomeWidget("Portfolio Value")
                    with widget2.content:
                        with ui.column().classes('gap-0'):
                            ui.label("$24,500.00").classes('text-3xl font-bold').style(f'color: {colours.text_primary}')
                            ui.label("+ 12.5%").classes('text-sm font-medium').style(f'color: {colours.positive}')

                    # --- WIDGET 3: EXAMPLE ---
                    widget3 = HomeWidget("Recent News")
                    with widget3.content:
                        ui.label("Market volatility expected to decrease...").classes('text-sm italic').style(f'color: {colours.text_secondary}')

                    MarketChartWidget(title="Apple Stock Trend", ticker="AAPL")

                    NewHomeWidget(on_click=lambda: None)

                    
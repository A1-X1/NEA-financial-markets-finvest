from nicegui import ui
from modules.globalSettings import GlobalSettings, globalSettings
from ui.pages.components.homeWidget import HomeWidget, MarketChartWidget
from ui.pages.components.newHomeWidget import NewHomeWidget
import plotly.graph_objects as go
from currency_codes import Currency

class HomePage:
    # constructor/initialiser
    def __init__(self):
        self.__settings = globalSettings

    # method for rendering the home page
    def render(self):
        colours = self.__settings.theme
        
        # outer container centers content on screen and adds top margin
        with ui.element('div').classes('w-full flex flex-col items-center mt-8 pb-10'):
            
            # inner container limits width to 1280px
            with ui.element('div').classes('w-[90%] max-w-7xl flex flex-col gap-8'):
                
                # header row title + currency badge
                with ui.row().classes('w-full justify-between items-center'):
                    ui.label('Dashboard').style(f'color: {colours.text_primary}; font-size: 200%; font-weight: bold')
                    
                    # small badge for currency
                    with ui.element('div').classes('px-4 py-2 rounded-full shadow-sm flex items-center gap-2') \
                            .style(f'background-color: {colours.surface}'):
                        ui.icon('monetization_on').style(f'color: {colours.accent}')
                        ui.label(f'{self.__settings.currencySymbol}{self.__settings.currency.code}').style(f'color: {colours.text_primary}; font-weight: 600')

                # grid layout
                with ui.element('div').classes('w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'):

                    # risk metric widget
                    widget1 = HomeWidget("Risk Metric")
                    with widget1.content:
                        # create chart
                        fig = go.Figure(go.Scatter(
                            x=[1, 2, 3, 4], 
                            y=[1, 2, 3, 2.5],
                            mode='lines+markers',
                            line=dict(color=colours.accent, width=3)
                        ))
                        
                        # style chart to match theme (transparent background)
                        fig.update_layout(
                            margin=dict(l=20, r=20, t=10, b=20),
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)', 
                            xaxis=dict(showgrid=False, showticklabels=False),
                            yaxis=dict(showgrid=True, gridcolor=colours.sb_inactive_fg, showticklabels=True),
                            font=dict(color=colours.text_secondary)
                        )
                        
                        # render chart (h-full makes it fill the widget body)
                        ui.plotly(fig).classes('w-full h-full')

                    # example widget
                    widget2 = HomeWidget("Portfolio Value")
                    with widget2.content:
                        with ui.column().classes('gap-0'):
                            ui.label("$24,500.00").classes('text-3xl font-bold').style(f'color: {colours.text_primary}')
                            ui.label("+ 12.5%").classes('text-sm font-medium').style(f'color: {colours.positive}')

                    # example widget
                    widget3 = HomeWidget("Recent News")
                    with widget3.content:
                        ui.label("Market volatility expected to decrease...").classes('text-sm italic').style(f'color: {colours.text_secondary}')

                    # market chart widget  
                    MarketChartWidget(title="Apple Stock Trend", ticker="AAPL")

                    # new home widget for adding widgets
                    NewHomeWidget()

                    
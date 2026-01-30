from nicegui import ui
from modules.globalSettings import globalSettings
from ui.pages.components.dataHandler import DataHandler
from ui.pages.components.visualisation import RiskTrendVisualisation


class HomeWidget(ui.element):
    # initialises the widget
    def __init__(self, title: str):
        # initialise parent as a div
        super().__init__('div') 
        
        # gets the theme from singleton instance of globalSettings
        theme = globalSettings.theme

        # applies styling through tailwind classes and theme
        self.classes('w-full h-[300px] flex flex-col p-4 gap-4 rounded-xl shadow-sm border border-gray-100/10')
        self.classes(f'bg-[{theme.surface}] text-[{theme.text_primary}]')

        # creates the title and more icon
        with self:
            with ui.row().classes('w-full items-center justify-between'):
                ui.label(title).classes('text-lg font-bold tracking-wide')
                ui.icon('more_horiz').classes(f'text-[{theme.text_secondary}] cursor-pointer')

            self.__content_container = ui.element('div').classes('w-full flex-grow relative')
            with self.__content_container:
                pass 

    @property
    def content(self):
        return self.__content_container
    
# creates a child class of HomeWidget
class MarketChartWidget(HomeWidget):
    def __init__(self, title: str, ticker: str):
        super().__init__(title)
        
        # stores the ticker symbol and data handler
        self.__ticker = ticker
        self.__handler = DataHandler()
        self.__handler.ticker_symbol = self.__ticker

        # creates the chart container and refreshes the data
        with self.content:
            self.__chart_container = ui.element('div').classes('w-full h-full flex items-center justify-center')
            self.refresh_data()

    # refreshes the data
    def refresh_data(self):
        try:
            # fetch data
            self.__handler.fetch_market_data()
            processed_data = self.__handler.prepare_risk_data()
            
            # get currency
            market_currency = self.__handler.currency

            # create visualisation (pass currency)
            viz = RiskTrendVisualisation(
                title_input=f"{self.__ticker} Trend",
                data_input=processed_data,
                currency_input=market_currency
            )
            fig = viz.generate_chart()

            # render
            with self.__chart_container:
                self.__chart_container.clear()
                ui.plotly(fig).classes('w-full h-full')
                
        # error handling
        except Exception as e:
            with self.__chart_container:
                self.__chart_container.clear()
                ui.label(f"{self.__ticker} Error: {str(e)}").classes('text-red-400 text-xs text-center p-4')
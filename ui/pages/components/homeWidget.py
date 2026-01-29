from nicegui import ui
from modules.globalSettings import globalSettings
from ui.pages.components.dataHandler import DataHandler
from ui.pages.components.visualisation import RiskTrendVisualisation


class HomeWidget(ui.element):
    def __init__(self, title: str):
        super().__init__('div') 
        
        theme = globalSettings.theme

        self.classes('w-full h-[300px] flex flex-col p-4 gap-4 rounded-xl shadow-sm border border-gray-100/10')
        self.classes(f'bg-[{theme.surface}] text-[{theme.text_primary}]')

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
    

class MarketChartWidget(HomeWidget):
    def __init__(self, title: str, ticker: str):
        super().__init__(title)
        
        self.__ticker = ticker
        self.__handler = DataHandler()
        self.__handler.ticker_symbol = self.__ticker

        with self.content:
            self.__chart_container = ui.element('div').classes('w-full h-full flex items-center justify-center')
            self.refresh_data()

    def refresh_data(self):
        try:
            # 1. Fetch Data
            self.__handler.fetch_market_data()
            processed_data = self.__handler.prepare_risk_data()
            
            # 2. Get Currency
            market_currency = self.__handler.currency

            # 3. Create Visualisation (Pass Currency)
            viz = RiskTrendVisualisation(
                title_input=f"{self.__ticker} Trend",
                data_input=processed_data,
                currency_input=market_currency
            )
            fig = viz.generate_chart()

            # 4. Render
            with self.__chart_container:
                self.__chart_container.clear()
                ui.plotly(fig).classes('w-full h-full')
                
        except Exception as e:
            with self.__chart_container:
                self.__chart_container.clear()
                ui.label(f"{self.__ticker} Error: {str(e)}").classes('text-red-400 text-xs text-center p-4')
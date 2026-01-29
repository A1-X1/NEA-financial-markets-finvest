from nicegui import ui
from modules.globalSettings import globalSettings
from ui.pages.components.dataHandler import DataHandler
from ui.pages.components.visualisation import RiskTrendVisualisation
from modules.calculations import calculateSharpeRatio

class HomeWidget(ui.element):
    def __init__(self, title: str):
        super().__init__('div') 
        theme = globalSettings.theme
        self.classes('w-full h-[320px] flex flex-col p-4 gap-2 rounded-xl shadow-sm border border-gray-100/10')
        self.style(f'background-color: {theme.surface}; color: {theme.text_primary}')

        with self:
            with ui.row().classes('w-full items-center justify-between'):
                ui.label(title).classes('text-md font-bold tracking-wide')
                ui.icon('more_horiz').classes(f'text-[{theme.text_secondary}] cursor-pointer')

            self.__content_container = ui.element('div').classes('w-full flex-grow relative')
            # Container for the compressed metrics
            self.metrics_bar = ui.row().classes('w-full justify-between items-center px-2 py-1 border-t border-gray-100/10')

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
        theme = globalSettings.theme
        try:
            self.__handler.fetch_market_data()
            processed_data = self.__handler.prepare_risk_data()
            
            # 1. Calculate Sharpe
            sharpe_val = calculateSharpeRatio(processed_data)

            viz = RiskTrendVisualisation(
                title_input="", # Minimal title for widget
                data_input=processed_data,
                currency_input=self.__handler.currency
            )
            fig = viz.generate_chart()

            # 2. Update Chart
            self.__chart_container.clear()
            with self.__chart_container:
                ui.plotly(fig).classes('w-full h-full')

            # 3. Update Compressed Metric Bar
            self.metrics_bar.clear()
            with self.metrics_bar:
                ui.label('Sharpe Ratio').classes('text-[10px] uppercase tracking-wider opacity-70')
                # Color coding the text based on value for quick reading
                s_color = theme.accent if sharpe_val > 1 else theme.text_primary
                ui.label(str(sharpe_val)).style(f'color: {s_color}; font-weight: bold; font-size: 0.9rem')
                
        except Exception as e:
            with self.__chart_container:
                self.__chart_container.clear()
                ui.label(f"Error").classes('text-red-400 text-xs')
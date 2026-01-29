from nicegui import ui
from modules.globalSettings import globalSettings
from ui.pages.components.dataHandler import DataHandler
from ui.pages.components.visualisation import RiskTrendVisualisation


class HomeWidget(ui.element):
    def __init__(self, title: str):
        super().__init__('div') 
        
        # Get current theme settings
        theme = globalSettings.theme

        # Style the main container (The Widget Card)
        self.classes('w-full h-[300px] flex flex-col p-4 gap-4 rounded-xl shadow-sm border border-gray-100/10')
        
        # Apply Theme Colors using Tailwind arbitrary values
        self.classes(f'bg-[{theme.surface}] text-[{theme.text_primary}]')

        with self:
            # header
            with ui.row().classes('w-full items-center justify-between'):
                # Title with primary text color
                ui.label(title).classes('text-lg font-bold tracking-wide')
                
                ui.icon('more_horiz').classes(f'text-[{theme.text_secondary}] cursor-pointer')

            # flex-grow: Takes up all remaining vertical space
            self.__content_container = ui.element('div').classes('w-full flex-grow relative')
            
            # Optional: Add a subtle placeholder text or loading state if empty
            with self.__content_container:
                pass 

    @property
    def content(self):
        """Returns the inner container to add content to."""
        return self.__content_container
    

class MarketChartWidget(HomeWidget):
    def __init__(self, title: str, ticker: str):
        super().__init__(title)
        
        self.__ticker = ticker
        self.__handler = DataHandler()
        # Validation is handled by the DataHandler setter
        self.__handler.ticker_symbol = self.__ticker

        with self.content:
            # Container for the Plotly chart
            self.__chart_container = ui.element('div').classes('w-full h-full flex items-center justify-center')
            self.refresh_data()

    def refresh_data(self):
        """
        Coordinates between the Logic (DataHandler) and UI (Visualisation).
        """
        try:
            # Logic Layer
            self.__handler.fetch_market_data()
            processed_data = self.__handler.prepare_risk_data()

            # Visualization Layer
            # FIX: Used 'title_input' and 'data_input' to match the Visualisation dataclass fields
            viz = RiskTrendVisualisation(
                title_input=f"{self.__ticker} Price Trend",
                data_input=processed_data
            )
            fig = viz.generate_chart()

            # UI Layer
            with self.__chart_container:
                self.__chart_container.clear()
                ui.plotly(fig).classes('w-full h-full')
                
        except Exception as e:
            with self.__chart_container:
                self.__chart_container.clear()
                # Print error to UI for easier debugging
                ui.label(f"{self.__ticker} Error: {str(e)}").classes('text-red-400 text-xs text-center p-4')
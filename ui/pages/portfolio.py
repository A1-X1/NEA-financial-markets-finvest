from nicegui import ui
from modules.globalSettings import GlobalSettings, globalSettings

class PortfolioPage:
    def __init__(self):
        self.__settings = globalSettings

    def render(self):
        colours = self.__settings.theme
        
        ui.label('Portfolio Page').style(f'color: {colours.text_primary}; font-size: 200%')
        
            
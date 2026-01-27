from nicegui import ui
from modules.globalSettings import GlobalSettings, globalSettings
from ui.pages.components.homeWidget import HomeWidget

class HomePage:
    def __init__(self):
        self.__settings = globalSettings

    def render(self):
        colours = self.__settings.theme
        
        ui.label('Welcome to your Financial Dashboard').style(f'color: {colours.text_primary}; font-size: 200%')
        
        with ui.card().style(f'background-color: {colours.surface}'):
            # Accessing properties through the getter methods
            ui.label(f'Active Currency: {self.__settings.currency}').style(f'color: {colours.text_primary}')

        HomeWidget()

        

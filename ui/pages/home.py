from nicegui import ui
from modules.settings import GlobalSettings

class HomePage:
    def __init__(self, settings: GlobalSettings):
        self.__settings = settings

    def render(self):
        colours = self.__settings.theme
        
        ui.label('Welcome to your Financial Dashboard').style(f'color: {colours.text_primary}; font-size: 200%')
        
        with ui.card().style(f'background-color: {colours.surface}'):
            # Accessing properties through the getter methods
            ui.label(f'Active Currency: {self.__settings.currency}').style(f'color: {colours.text_primary}')
            
from nicegui import ui
from modules.globalSettings import globalSettings
from modules.colourScheme import ColourScheme
from dataclasses import dataclass


@dataclass
class HomeWidget(ui.element):
    def __init__(self):
        # 2. Initialize the parent element with the HTML tag you want (e.g., 'div')
        super().__init__('div') 

        settings = globalSettings
        colourScheme: ColourScheme = settings.theme

        # 3. Use 'with self' to place content INSIDE this widget
        with self:
            # You can apply styles to the container here
            self.__container = ui.element('div').classes(f'bg-blue-100').style(f' width: 100%; height: 20%;')
            
            with self.__container:
                ui.label("Risk Metric").style(f'color: {settings.theme.text_primary}')

    @property
    def container(self):
        return self.__container
from nicegui import ui
from typing import Callable
from dataclasses import dataclass
from modules.globalSettings import globalSettings, GlobalSettings

@dataclass
class SettingsTile(ui.row):
    
    def __init__(self, label: str, icon: str, icon_bg_colour: str, icon_colour: str, initial_value: bool, on_change: Callable):
        super().__init__()
        self.__label = label
        self.__icon = icon
        self.__icon_bg_colour = icon_bg_colour
        self.__icon_colour = icon_colour
        
        # self.classes('w-full items-center justify-between py-2 px-4 bg-transparent')
        self.classes('w-[400px] justify-between py-2 px-0 bg-transparent')
        
        with self:
            with ui.row().classes('items-center gap-4'):
                # explicitly creating the container
                self.__icon_container = ui.element('div').style(
                    f'background-color: {self.__icon_bg_colour}; '
                    'width: 32px; height: 32px; '
                    'border-radius: 7px; '
                    'display: flex; align-items: center; justify-content: center;'
                )
                
                with self.__icon_container:
                    # creating the icon and sets its color
                    ui.icon(self.__icon, color=self.__icon_colour).classes('text-lg')

                # creating the label of the settings tile
                ui.label(self.__label).classes('text-md font-medium').style(f'color: {globalSettings.theme.text_primary}')

            # creating the switch of the settings tile
            self.switch = ui.switch(value=initial_value, on_change=on_change).props('keep-color color=green dense').style(f'margin-top: 6px;')

    # getters and setters
    @property
    def icon_bg_color(self) -> str:
        return self.__icon_bg_color

    @icon_bg_color.setter
    def icon_bg_color(self, value: str):
        self.__icon_bg_color = value

    @property
    def icon_color(self) -> str:
        return self.__icon_color

    @icon_color.setter
    def icon_color(self, value: str):
        self.__icon_color = value
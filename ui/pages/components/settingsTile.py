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
                    # Setting the icon color via .style() ensures it overrides container defaults
                    ui.icon(self.__icon, color=self.__icon_colour).classes('text-lg')

                
                ui.label(self.__label).classes('text-md font-medium').style(f'color: {globalSettings.theme.text_primary}')

            # the switch component itself
            self.switch = ui.switch(value=initial_value, on_change=on_change).props('keep-color color=green dense').style(f'margin-top: 6px;')

    # getters and setters
    @property
    def icon_bg_colour(self) -> str:
        return self.__icon_bg_colour

    @icon_bg_colour.setter
    def icon_bg_colour(self, value: str):
        self.__icon_bg_colour = value

    @property
    def icon_colour(self) -> str:
        return self.__icon_colour

    @icon_colour.setter
    def icon_colour(self, value: str):
        self.__icon_colour = value
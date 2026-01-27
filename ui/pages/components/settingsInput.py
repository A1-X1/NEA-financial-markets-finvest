from nicegui import ui
from typing import Callable
from dataclasses import dataclass
from modules.globalSettings import globalSettings

ui.add_css(f'''
    /* 1. The text color inside the input */
    .input-field .q-field__native {{
        color: {globalSettings.theme.text_primary} !important;
    }}
    
    /* 2. The Inactive Border color (pseudo-element :before) */
    .input-field .q-field__control:before {{
        border-color: {globalSettings.theme.text_primary} !important;
        opacity: 0.5; /* Optional: make it slightly subtle like standard inactive borders */
    }}

    /* 3. The Hover Border color (optional, ensures it stays your color on hover) */
    .input-field .q-field__control:hover:before {{
        border-color: {globalSettings.theme.text_primary} !important;
        opacity: 1;
    }}
''', shared=True)

print(globalSettings.theme.text_primary)

@dataclass
class SettingsInput(ui.row):
    def __init__(self, label: str, icon: str, icon_bg_color: str, icon_color: str, initial_value: str, on_save: Callable):
        super().__init__()
        self.__label = label
        self.__icon = icon
        self.__icon_bg_color = icon_bg_color
        self.__icon_color = icon_color
        self.__on_save = on_save
        
        self.classes('w-[400px] py-2 px-0 bg-transparent items-center justify-between')
        
        with self:
            with ui.row().classes('items-center gap-4'):
                self.__icon_container = ui.element('div').style(
                    f'background-color: {self.__icon_bg_color}; '
                    'width: 32px; height: 32px; '
                    'border-radius: 7px; '
                    'display: flex; align-items: center; justify-content: center;'
                )
                
                with self.__icon_container:
                    ui.icon(self.__icon).style(f'color: {self.__icon_color}').classes('text-lg')

                ui.label(self.__label).classes('text-md font-medium').style(f'color: {globalSettings.theme.text_primary}')

            with ui.row().classes('items-center gap-2'):
                self.__input_field = ui.input(value=initial_value).props('outlined dense').style(
                f'width: 150px; '
                f'color: {globalSettings.theme.text_primary}; '           # Sets the text color inside
                f'--q-primary: {globalSettings.theme.text_primary}; '     # Sets the Quasar primary (active border)
                f'border-color: {globalSettings.theme.text_primary};'     # Sets the base border color
            ).classes('input-field')
                # Save button uses the buttonBackground and buttonForeground from the spec
                self.__save_button = ui.button('Save', on_click=lambda: self.__on_save(self.__input_field.value)).style(
                    f'background-color: {globalSettings.theme.button_background}; '
                    f'color: {globalSettings.theme.button_foreground};'
                    
                ).props(f':ripple="false" unelevated')

    @property
    def current_value(self) -> str:
        return self.__input_field.value

    @current_value.setter
    def current_value(self, value: str):
        # make sure not null
        if value is not None:
            self.__input_field.value = str(value)

    @property
    def label(self) -> str:
        return self.__label

    @label.setter
    def label(self, value: str):
        if not value.strip():
            raise ValueError("Label cannot be empty")
        self.__label = value

    @property
    def icon_bg_color(self) -> str:
        return self.__icon_bg_color

    @icon_bg_color.setter
    def icon_bg_color(self, value: str):
        # Validation: Hex code check could be added here
        self.__icon_bg_color = value
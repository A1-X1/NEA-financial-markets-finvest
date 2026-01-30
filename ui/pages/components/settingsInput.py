from nicegui import ui
from typing import Callable
from dataclasses import dataclass
from modules.globalSettings import globalSettings
from currency_codes import get_currency_by_code, Currency, CurrencyNotFoundError
from currency_symbols import CurrencySymbols
import re

# adds custom CSS to the page
ui.add_css('''
    .input-field .q-field__native {
        color: var(--custom-input-color) !important;
    }
    
    .input-field .q-field__control:before {
        border-color: var(--custom-input-color) !important;
        opacity: 0.5; 
    }

    .input-field .q-field__control:hover:before {
        border-color: var(--custom-input-color) !important;
        opacity: 1;
    }
''', shared=True)

@dataclass
class SettingsInput(ui.row):

    def __init__(self, label: str, icon: str, icon_bg_colour: str, icon_colour: str, initial_value: str, on_save: Callable):
        super().__init__()
        self.__label = label
        self.__icon = icon
        self.__icon_bg_colour = icon_bg_colour
        self.__icon_colour = icon_colour
        self.__on_save = on_save
        
        self.classes('w-[400px] py-2 px-0 bg-transparent items-center justify-between')

        # gets the current text color from the theme
        current_text_colour = globalSettings.theme.text_primary
        
        # creates the icon container and adds the icon and label to it
        with self:
            with ui.row().classes('items-center gap-4'):
                self.__icon_container = ui.element('div').style(
                    f'background-color: {self.__icon_bg_colour}; '
                    'width: 32px; height: 32px; '
                    'border-radius: 7px; '
                    'display: flex; align-items: center; justify-content: center;'
                )
                
                with self.__icon_container:
                    ui.icon(self.__icon).style(f'color: {self.__icon_colour}').classes('text-lg')

                ui.label(self.__label).classes('text-md font-medium').style(f'color: {current_text_colour}')

            with ui.row().classes('items-center gap-2'):
                self.__input_field = ui.input(value=initial_value, on_change=self.__force_uppercase).props('outlined dense').style(
                f'width: 150px; '

                # sets the text color inside
                f'color: {current_text_colour}; '           

                # sets the Quasar primary (active border)
                f'--q-primary: {current_text_colour}; '   

                # sets the custom input colour from before
                f'--custom-input-color: {current_text_colour}; '

                # sets the base border color
                f'border-color: {current_text_colour};'     
            ).classes('input-field')
                
                self.__save_button = ui.button('Save', on_click=self.__handle_manual_save).style(
                    f'background-color: {globalSettings.theme.button_background} !important ; '
                    f'color: {globalSettings.theme.button_foreground} !important;'
                    
                ).props(f':ripple="false" unelevated')

    def __force_uppercase(self):
        if self.__input_field.value:
            self.__input_field.value = self.__input_field.value.upper()

    def __show_validation_error(self, message : str):
        ui.notify(
            f'Validation Error: {message}',
            position='top',
            type='negative',
            icon='priority_high',
            close_button=True
        )

    def __show_validation_error_nonexistant_currency(self):
        ui.notify(
            f'Validation Error: {self.__input_field.value} is not a valid currency code.',
            position='top',
            type='negative',
            icon='priority_high',
            close_button=True
        )

    def __handle_manual_save(self):
        currencyInput = self.__input_field.value

        if (len(currencyInput) == 0):
            self.__show_validation_error('Field cannot be empty.')
            return
        
        if not re.match(r'^[A-Za-z]+$', currencyInput):
            self.__show_validation_error('Use currency codes, not symbols.')
            return
        
        if (len(currencyInput) != 3):
            self.__show_validation_error('Currency code must be exactly 3 characters.')
            return
        
        try:
            get_currency_by_code(currencyInput)
        except CurrencyNotFoundError:
            self.__show_validation_error_nonexistant_currency()
            return
        except Exception as e:
            print(e)
            return
        
        self.__on_save(currencyInput)


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
    def icon_bg_colour(self) -> str:
        return self.__icon_bg_colour

    @icon_bg_colour.setter
    def icon_bg_colour(self, value: str):
        self.__icon_bg_colour = value
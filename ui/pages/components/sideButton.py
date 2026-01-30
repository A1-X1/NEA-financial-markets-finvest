from nicegui import ui
from modules.globalSettings import GlobalSettings, globalSettings
from typing import Callable

class SideButton(ui.button):
    
    def __init__(self, buttonLabel : str, icon: str, callbackFunction : Callable, isActive: bool = False):
        self.__isActive = isActive,
        self.__buttonLabel = buttonLabel
        self.__icon_name = icon
        self.__external_callback = callbackFunction

        # initialize the button parent class attributes
        super().__init__(color=None, on_click=self.__handle_click)

        self.applyStyles()

        with self:
            with ui.row().classes('items-center justify-start gap-4 w-full no-wrap px-4'):
                ui.icon(icon).classes('text-2xl')
                # the label will be hidden by the drawer's mini state logic if I add later
                ui.label(buttonLabel).classes('truncate')

    def __handle_click(self) -> None:
        # trigger internal logic
        self.toggle()
        self.applyStyles()
        
        # trigger the external page load logic
        if self.__external_callback:
            self.__external_callback()

    # the colour getting applied
    def applyStyles(self):
        Theme = globalSettings.theme

        self.classes('w-full rounded-8 no-shadow cursor-pointer')
        self.props(f':ripple="false" flat unelevated ')

        foreground_colour = Theme.sb_active_fg if (self.__isActive == True) else Theme.sb_inactive_fg
        background_colour = Theme.sb_active_bg if (self.__isActive == True) else Theme.sb_inactive_bg

        self.style(f'width: 85%; color: {foreground_colour} ; background: {background_colour};')

    def toggle(self) -> None: 
        self.__isActive = not self.__isActive 
        self.applyStyles()

    def toggle_active(self, state: bool) -> None:
        # changes the internal state and triggers a style refresh
        self.__isActive = state
        self.applyStyles()
    
from nicegui import ui
from modules.globalSettings import GlobalSettings
from modules.colourScheme import Theme
from typing import Callable

class SideButton(ui.button):

    def __init__(self, buttonLabel : str, icon: str, callbackFunction : Callable, isActive: bool = False):
        self.__isActive = isActive,
        self.__buttonLabel = buttonLabel
        self.__icon_name = icon
        self.__external_callback = callbackFunction

        super().__init__(color=None, on_click=self.__handle_click)

        self.update()
        self.applyStyles()

        with self:
            with ui.row().classes('items-center justify-start gap-4 w-full no-wrap px-4'):
                ui.icon(icon).classes('text-2xl')
                # The label will be hidden by the drawer's 'mini' state logic
                ui.label(buttonLabel).classes('truncate')

    def __handle_click(self) -> None:
        # Trigger internal logic
        self.toggle()
        self.applyStyles()
        
        # Trigger the external page load logic
        if self.__external_callback:
            self.__external_callback()

    # the colour isnt getting applied
    def applyStyles(self):
        self.classes('w-full rounded-8 no-shadow cursor-pointer')
        self.props(f':ripple="false" flat unelevated ')

        foreground_colour = Theme.sb_active_fg if (self.__isActive == True) else Theme.sb_inactive_fg
        background_colour = Theme.sb_active_bg if (self.__isActive == True) else Theme.sb_inactive_bg

        self.style(f'width: 85%; color: {foreground_colour} ; background: {background_colour};')

    
    def toggle(self) -> None: 
        """Toggle the button state.""" 
        self.__isActive = not self.__isActive 
        self.update()

    def toggle_active(self, state: bool) -> None:
        # Changes the internal state and triggers a style refresh
        self.__isActive = state
        self.applyStyles()

    def update(self) -> None:
        super().update()

    
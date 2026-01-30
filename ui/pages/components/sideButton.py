from nicegui import ui
from modules.globalSettings import GlobalSettings, globalSettings
from typing import Callable

# side button class inherits from ui.button
class SideButton(ui.button):
    
    # initialise attributes and calls constructor of parent class
    def __init__(self, buttonLabel : str, icon: str, callbackFunction : Callable, isActive: bool = False):
        self.__isActive = isActive,
        self.__buttonLabel = buttonLabel
        self.__icon_name = icon
        self.__external_callback = callbackFunction

        super().__init__(color=None, on_click=self.__handle_click)

        # applies styles to the button based on the theme and state
        self.applyStyles()

        # adds the icon and label to the button
        with self:
            with ui.row().classes('items-center justify-start gap-4 w-full no-wrap px-4'):
                ui.icon(icon).classes('text-2xl')
                # The label will be hidden by the drawer's 'mini' state logic
                ui.label(buttonLabel).classes('truncate')

    # handles the click event
    def __handle_click(self) -> None:
        
        # toggles the button state
        self.toggle()
        self.applyStyles()
        
        # calls the external callback function if it exists
        if self.__external_callback:
            self.__external_callback()

    # applies styles to the button based on the theme and state
    def applyStyles(self):
        Theme = globalSettings.theme

        self.classes('w-full rounded-8 no-shadow cursor-pointer')
        self.props(f':ripple="false" flat unelevated ')

        foreground_colour = Theme.sb_active_fg if (self.__isActive == True) else Theme.sb_inactive_fg
        background_colour = Theme.sb_active_bg if (self.__isActive == True) else Theme.sb_inactive_bg

        self.style(f'width: 85%; color: {foreground_colour} ; background: {background_colour};')

    # toggles the button state
    def toggle(self) -> None: 
        self.__isActive = not self.__isActive 
        self.applyStyles()

    def toggle_active(self, state: bool) -> None:
        self.__isActive = state
        self.applyStyles()


    
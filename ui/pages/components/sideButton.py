from nicegui import ui
from modules.settings import GlobalSettings
from modules.colourScheme import Theme
from typing import Callable

class SideButton(ui.button):

    def __init__(self, buttonLabel : str, callbackFunction : Callable, isActive: bool = False):
        self.__isActive = isActive,
        self.__buttonLabel = buttonLabel

        super().__init__(color=None)

        self.on('click', self.toggle)
        self.update()
        self.applyStyles()

        with self:
            with ui.row().classes('items-center gap-3'):
                self.__buttonLabel = ui.label(self.__buttonLabel)

    # the colour isnt getting applied
    def applyStyles(self):
        self.props(f':ripple="false"')
        print(f'width: 250px; color: {Theme.button_foreground} ; background: {Theme.button_background};')
        self.style(f'width: 250px; color: {Theme.button_foreground} ; background: {Theme.button_background};')

    
    def toggle(self) -> None: 
        """Toggle the button state.""" 
        self.__isActive = not self.__isActive 
        self.update()

    def update(self) -> None:
        super().update()

    
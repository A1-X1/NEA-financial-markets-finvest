from nicegui import ui
from modules.settings import GlobalSettings
from modules.colourScheme import ColourScheme

class SideButton(ui.button):

    def __init__(self, buttonLabel : str, isActive: bool = False):
        self.__isActive = isActive,
        self.__buttonLabel = buttonLabel
        super().__init__()
        self.on('click', self.toggle)
        self.update()
        self.applyStyles()

        with self:
            with ui.row().classes('items-center gap-3'):
                self.__buttonLabel = ui.label(self.__buttonLabel)

    def applyStyles(self):
        self.props(f'ripple="false"')
        self.style(f'width: 250px; color: {ColourScheme.button_foreground}; background-color: {ColourScheme.button_background};')


    
    def toggle(self) -> None: 
        """Toggle the button state.""" 
        self.__isActive = not self.__isActive 
        self.update()

    def update(self) -> None:
        with self.props.suspend_updates():
            self.props(f'color={"green" if self.__isActive else "red"}')
        super().update()

    
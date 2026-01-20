from nicegui import ui
from modules.settings import GlobalSettings

class SideButton(ui.button):

    def __init__(self, buttonLabel : str, isActive: bool = False,):
        self.__isActive = isActive,
        super().__init__()
        self.on('click', self.toggle)
        self.update()
        self.props(f'ripple="false"')

    
    def toggle(self) -> None: 
        """Toggle the button state.""" 
        self.__isActive = not self.__isActive 
        self.update()

    def update(self) -> None:
        with self.props.suspend_updates():
            self.props(f'color={"green" if self.__isActive else "red"}')
        super().update()
    

    # def render(self):
    #     active_palette = self.__app_settings.theme
        
    #     # Applying conditional styling based on the button's selection state
    #     background_style = active_palette.sb_active_bg if self.__is_currently_active else active_palette.sb_inactive_bg
    #     foreground_style = active_palette.sb_active_fg if self.__is_currently_active else active_palette.sb_inactive_fg
    #     font_weight_style = 'font-weight: 600' if self.__is_currently_active else 'font-weight: 400'

    #     # Using the NiceGUI button component as a base for the custom widget
    #     custom_button = ui.button(on_click=self.__click_handler, color=background_style).props('ripple=false').style(
    #         f'background-color: {background_style}; '
    #         f'color: {foreground_style}; '
    #         f'width: 100%; '
    #         f'justify-content: start; '
    #         f'text-transform: none; '
    #         f'border-radius: 8px;'
    #         f'flex-direction: column;'
    #         f'align-items: center;'
    #     ).classes('py-2 px-4 mb-1 shadow-none')

    #     with custom_button:
    #         with ui.row().classes('items-center gap-3'):
    #             ui.icon(self.__vector_icon).style(f'color: {foreground_style}')
    #             ui.label(self.__button_label).style(font_weight_style)
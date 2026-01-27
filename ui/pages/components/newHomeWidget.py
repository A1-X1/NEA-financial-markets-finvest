from nicegui import ui
from typing import Callable
from modules.globalSettings import globalSettings

class NewHomeWidget(ui.element):
    def __init__(self, on_click: Callable):
        # Initialise as a div
        super().__init__('div')
        
        theme = globalSettings.theme

        # Styling
        self.classes('w-full h-full min-h-[300px] flex items-center justify-center rounded-xl border-2 border-dashed cursor-pointer transition-all duration-300')

        self.style(f'border-color: {theme.text_placeholder}; background-color: transparent;')
        
        # Hover Effect
        self.classes('hover:bg-gray-50/50 opacity-50 hover:opacity-100')

        # Register the Click Event
        self.on('click', on_click)

        with self:
            # Draws the circle around the plus sign
            with ui.element('div').classes('rounded-full w-16 h-16 flex items-center justify-center border') \
                 .style(f'border-color: {theme.text_placeholder};'):
                
                ui.icon('add').classes('text-4xl add-icon').style(f'color: {theme.text_placeholder}; font-weight: 700 !important;')
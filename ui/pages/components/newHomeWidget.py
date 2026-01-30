from nicegui import ui
from typing import Callable
from modules.globalSettings import globalSettings

# Adds custom CSS to the page
ui.add_css('''
    .add-icon {
        font-weight: 700 !important;
    }
''', shared=True)

class NewHomeWidget(ui.element):
    def __init__(self, on_click: Callable):
        # initialise as a div
        super().__init__('div')
        
        # gets the theme from singleton instance of globalSettings
        theme = globalSettings.theme

        # applies styling
        self.classes('w-full h-full min-h-[300px] flex items-center justify-center rounded-xl border-2 border-dashed cursor-pointer transition-all duration-300')

        self.style(f'border-color: {theme.text_placeholder}; background-color: transparent;')
        
        # hover effect
        self.classes('hover:bg-gray-50/50 opacity-50 hover:opacity-100')

        # registers the click event
        self.on('click', on_click)

        # draws the plus sign
        with self:
            with ui.element('div').classes('rounded-full w-16 h-16 flex items-center justify-center border') \
                 .style(f'border-color: {theme.text_placeholder};'):
                
                ui.icon('add').classes('text-4xl add-icon').style(f'color: {theme.text_placeholder}; font-weight: 700 !important;')
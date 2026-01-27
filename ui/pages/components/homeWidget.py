from nicegui import ui
from modules.globalSettings import globalSettings


class HomeWidget(ui.element):
    def __init__(self, title: str):
        super().__init__('div') 
        
        # Get current theme settings
        theme = globalSettings.theme

        # Style the main container (The Widget Card)
        self.classes('w-full h-[300px] flex flex-col p-4 gap-4 rounded-xl shadow-sm border border-gray-100/10')
        
        # Apply Theme Colors using Tailwind arbitrary values
        self.classes(f'bg-[{theme.surface}] text-[{theme.text_primary}]')

        with self:
            # header
            with ui.row().classes('w-full items-center justify-between'):
                # Title with primary text color
                ui.label(title).classes('text-lg font-bold tracking-wide')
                
                # ui.icon('more_horiz').classes(f'text-[{theme.text_secondary}] cursor-pointer')

            # flex-grow: Takes up all remaining vertical space
            self.__content_container = ui.element('div').classes('w-full flex-grow relative')
            
            # Optional: Add a subtle placeholder text or loading state if empty
            with self.__content_container:
                pass 

    @property
    def content(self):
        """Returns the inner container to add content to."""
        return self.__content_container
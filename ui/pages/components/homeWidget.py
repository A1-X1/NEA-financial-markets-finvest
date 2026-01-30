from nicegui import ui
from modules.globalSettings import globalSettings


class HomeWidget(ui.element):
    # constructor
    def __init__(self, title: str):
        super().__init__('div') 
        
        # get current theme settings
        theme = globalSettings.theme

        # style the main container (the widget card)
        self.classes('w-full h-[300px] flex flex-col p-4 gap-4 rounded-xl shadow-sm border border-gray-100/10')
        
        # apply theme colors using tailwind values
        self.classes(f'bg-[{theme.surface}] text-[{theme.text_primary}]')

        with self:
            # header
            with ui.row().classes('w-full items-center justify-between'):
                # title with primary text color
                ui.label(title).classes('text-lg font-bold tracking-wide')
                

            # takes up all remaining vertical space for container
            self.__content_container = ui.element('div').classes('w-full flex-grow relative')

    @property
    def content(self):
        # returns the inner container to add content to
        return self.__content_container
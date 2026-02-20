from nicegui import ui
from modules.globalSettings import globalSettings

# custom css for the add icon weight
ui.add_css('''\n    .add-icon {\n        font-weight: 700 !important;\n    }\n    .add-widget-menu .q-list {\n        padding: 4px 0;\n    }\n''', shared=True)

class NewHomeWidget(ui.element):
    def __init__(self):
        # initialise as a div
        super().__init__('div')
        
        # gets the theme from singleton instance of globalSettings
        theme = globalSettings.theme

        # applies styling
        self.classes('w-full h-full min-h-[300px] flex items-center justify-center rounded-xl border-2 border-dashed cursor-pointer transition-all duration-300')
        self.style(f'border-color: {theme.text_placeholder}; background-color: transparent;')
        self.classes('hover:bg-gray-50/50 opacity-50 hover:opacity-100')

        with self:
            with ui.element('div').classes('relative flex flex-col items-center gap-3'):
                
                # draws the plus sign circle
                btn_wrapper = ui.element('div').classes('rounded-full w-16 h-16 flex items-center justify-center border') \
                    .style(f'border-color: {theme.text_placeholder};')
                with btn_wrapper:
                    ui.icon('add').classes('text-4xl add-icon').style(f'color: {theme.text_placeholder}; font-weight: 700 !important;')
                
                ui.label('Add Widget').classes('text-xs').style(f'color: {theme.text_placeholder}')

                # menu anchored to the widget — opens on click via the outer div
                with ui.menu().classes('add-widget-menu').style(
                    f'background-color: {theme.surface}; border: 1px solid {theme.accent}33; '
                    f'border-radius: 12px; min-width: 180px; box-shadow: 0 8px 24px rgba(0,0,0,0.15);'
                ) as menu:
                    ui.label('Add widget from').classes('text-xs px-4 pt-3 pb-1 font-semibold') \
                        .style(f'color: {theme.text_secondary}; text-transform: uppercase; letter-spacing: 0.05em;')
                    
                    # each page option navigates to that page
                    for label, icon_name, route in [
                        ('Charts', 'assessment', '/charts'),
                        ('Simulation', 'repeat', '/simulation'),
                        ('Portfolio', 'pie_chart', '/portfolio'),
                    ]:
                        with ui.menu_item(on_click=lambda r=route: ui.navigate.to(r)) \
                                .classes('gap-3 px-4 py-2 rounded-lg mx-1 my-0.5') \
                                .style(f'color: {theme.text_primary};'):
                            ui.icon(icon_name).style(f'color: {theme.accent}; font-size: 1.2rem;')
                            ui.label(label)

        # clicking the outer widget opens the menu
        self.on('click', lambda: menu.open())
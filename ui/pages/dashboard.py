from nicegui import ui
from modules.globalSettings import globalSettings
from ui.pages.components.sideButton import SideButton

class DashboardLayout:
    def __init__(self):
        self.__settings = globalSettings
        

    def render(self, active_route: str):
        colours = self.__settings.theme
        weight = self.__settings.fontWeight

        ui.query('body').style(f'background-color: {colours.background}; font-weight: {self.__settings.fontWeight}')
        ui.add_head_html(f'''
            <style>

                *:not(h1):not(h2):not(h3):not(h4):not(h5):not(h6):not(.ignore-bold) {{ 
                    font-weight: {weight} !important; 
                }}
                
                .q-item__label, .q-btn__content, .nicegui-label {{
                    font-weight: {weight} !important;
                }}
                
                /* Ensure background colors still update via query */

                body {{ background-color: {colours.background} !important; }}
                .my-sidebar {{ background-color: {colours.surface} !important; }}
            </style>
        ''')

        # Render Sidebar
        sidebar_style = f'background-color: {colours.surface}; padding: 0; padding-bottom: 20px;'
        
        with ui.left_drawer().style(sidebar_style).classes('flex flex-col items-center gap-0'):
            
            # App Title
            ui.label('FINVEST').style(f'color: {colours.text_primary}; font-size: 24px; font-weight: bold; margin-bottom: 20px;').classes('p-5 flex items-center justify-center w-full ignore-bold')

            # Navigation Logic
            SideButton(
                buttonLabel='Home', 
                icon='home', 
                callbackFunction=lambda: ui.navigate.to('/')
            ).toggle_active(active_route == 'home')

            SideButton(
                buttonLabel='Charts', 
                icon='assessment', 
                callbackFunction=lambda: ui.navigate.to('/charts')
            ).toggle_active(active_route == 'charts')

            SideButton(
                buttonLabel='Simulation', 
                icon='repeat', 
                callbackFunction=lambda: ui.navigate.to('/simulation')
            ).toggle_active(active_route == 'simulation')
            
            SideButton(
                buttonLabel='Portfolio', 
                icon='pie_chart', 
                callbackFunction=lambda: ui.navigate.to('/portfolio')
            ).toggle_active(active_route == 'portfolio')

            SideButton(
                buttonLabel='News', 
                icon='newspaper', 
                callbackFunction=lambda: ui.navigate.to('/news')
            ).toggle_active(active_route == 'news')

            ui.space()

            SideButton(
                buttonLabel='Settings', 
                icon='settings', 
                callbackFunction=lambda: ui.navigate.to('/settings')
            ).toggle_active(active_route == 'settings')


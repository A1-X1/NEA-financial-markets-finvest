from nicegui import ui
from modules.globalSettings import globalSettings
from ui.pages.components.sideButton import SideButton

class DashboardLayout:
    """
    Refactored to support NiceGUI Routing.
    This class now renders the 'Shell' (Sidebar & Styling) around the active page content.
    """
    def __init__(self):
        self.__settings = globalSettings
        

    def render(self, active_route: str):
        colours = self.__settings.theme

        # 1. Apply Global Styles
        ui.query('body').style(f'background-color: {colours.background}; font-weight: {self.__settings.fontWeight}')

        # 2. Render Sidebar
        # FIXED: Removed '...' and ensured valid CSS styling
        sidebar_style = f'background-color: {colours.surface}; padding: 0; padding-bottom: 20px;'
        
        with ui.left_drawer().style(sidebar_style).classes('flex flex-col items-center gap-0'):
            
            # App Title
            ui.label('FINVEST').style(f'color: {colours.text_primary}; font-size: 24px; font-weight: bold; margin-bottom: 20px;').classes('p-5 flex items-center justify-center w-full')

            # 3. Define Navigation Logic
            # We recreate the buttons here, checking against 'active_route'
            
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


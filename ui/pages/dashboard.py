from nicegui import ui
from modules.settings import GlobalSettings

class DashboardLayout:
    def __init__(self, settings: GlobalSettings):
        self.__settings = settings
        self.__content_area = None

    def build_ui(self):
        # 1. Setup the Theme/Background
        ui.query('body').style('background-color: #0A2F21')
        
        # 2. Setup the Sidebar (Persistent)
        with ui.left_drawer().style('background-color: #7C8D88'):
            ui.label('FINVEST').style('color: #F8F8FA; font-weight: bold')
            # Navigation buttons will call the manager to switch content
            ui.button('Home', on_click=self.load_home_page)

        # 3. Setup the Main Content Area (The "Slot")
        self.__content_area = ui.column().classes('w-full p-4')

    def load_home_page(self):
        from ui.pages.home import HomePage
        self.__content_area.clear()
        with self.__content_area:
            home = HomePage(self.__settings)
            home.render()
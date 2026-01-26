from nicegui import ui
from modules.settings import GlobalSettings
from ui.pages.components.sideButton import SideButton
from ui.pages import *

class DashboardLayout:
    def __init__(self, settings: GlobalSettings):
        self.__settings = settings
        self.__content_area = None

    def load_home_page(self):
        # Ensure this matches your actual file name: homepage.py
        from ui.pages.home import HomePage
        self.__content_area.clear()
        with self.__content_area:
            home = HomePage(self.__settings)
            home.render()

    def build_ui(self):
        # Access the encapsulated colour object
        colours = self.__settings.theme
        
        # 1. Setup the Theme/Background using the managed palette
        ui.query('body').style(f'background-color: {colours.background}')
        
        # 2. Setup the Sidebar (Persistent)
        with ui.left_drawer().style(f'background-color: {colours.surface}; flex-wrap: wrap; align-content: center;'):
            ui.label('FINVEST').style(f'color: {colours.text_primary}; font-weight: bold')

            SideButton(buttonLabel='Home', callbackFunction=self.load_home_page())
            SideButton(buttonLabel='Home', callbackFunction=self.load_home_page())
            SideButton(buttonLabel='Home', callbackFunction=self.load_home_page())

        # 3. Setup the Main Content Area (The "Slot")
        self.__content_area = ui.column().classes('w-full p-4')

    
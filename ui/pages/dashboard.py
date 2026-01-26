from nicegui import ui
from modules.settings import GlobalSettings
from ui.pages.components.sideButton import SideButton
from ui.pages.home import HomePage
from typing import List

class DashboardLayout:
    def __init__(self, settings: GlobalSettings):
        self.__settings = settings
        self.__content_area = None
        self.__nav_buttons : list[SideButton] = [] # List to track button instances
    
    def __update_active_button(self, clicked_button: SideButton):
        # This method iterates through all tracked buttons, setting the 
        # clicked one to active and all others to inactive.
        for button in self.__nav_buttons:
            button.toggle_active(button == clicked_button)

    def load_home_page(self, nav_button : SideButton = None):

        # If no button is passed, default to first 
        target_button = nav_button if nav_button else self.__nav_buttons[0]

        self.__update_active_button(target_button)
        self.__content_area.clear()
        with self.__content_area:
            home = HomePage(self.__settings)
            home.render()

    def build_ui(self):
        # Access the colour object
        colours = self.__settings.theme

        # Clears the list each refresh to stop lack of sync
        self.__nav_buttons.clear()
        
        # Setup the Theme using the palette
        ui.query('body').style(f'background-color: {colours.background}')
        
        # Setup the Sidebar 
        with ui.left_drawer().style(f'background-color: {colours.surface}; flex-wrap: wrap; align-content: center; padding: 0;').classes(f'gap-0'):
            ui.label('FINVEST').style(f'color: {colours.text_primary}; font-size: 24px; font-weight: bold; margin-bottom: 20px;').classes(f'p-5 flex items-center justify-center w-full')

            homeBtn = SideButton(buttonLabel='Home', icon='home', callbackFunction= lambda : self.load_home_page(homeBtn))
            riskBtn = SideButton(buttonLabel='Risk Analysis', icon='assessment', callbackFunction= lambda : self.load_home_page(riskBtn))
            portfolioBtn = SideButton(buttonLabel='Portfolio', icon='pie_chart', callbackFunction= lambda : self.load_home_page(portfolioBtn))

            self.__nav_buttons.extend([homeBtn, riskBtn, portfolioBtn])

        # Setup the Main Content Area
        self.__content_area = ui.column().classes('w-full p-4')

        # SET DEFAULT VIEW
        # explicitly call load_home_page with homeBtn to trigger the 
        # __update_active_button logic immediately on load.
        if self.__nav_buttons:
            self.load_home_page(self.__nav_buttons[0])

    
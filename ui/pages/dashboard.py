from nicegui import ui
from modules.globalSettings import GlobalSettings, globalSettings
from ui.pages.components.sideButton import SideButton
from ui.pages.home import HomePage
from ui.pages.settings import SettingsPage
from typing import List

class DashboardLayout:
    def __init__(self):
        self.__settings = globalSettings
        self.__content_area = None
        self.__nav_buttons : list[SideButton] = [] # List to track button instances
    
    # This method iterates through all tracked buttons, setting the 
    # clicked one to active and all others to inactive.
    def __update_active_button(self, clicked_button: SideButton):
        for button in self.__nav_buttons:
            button.toggle_active(button == clicked_button)

    def load_home_page(self, nav_button : SideButton = None):
        # If no button is passed, default to first 
        target_button = nav_button if nav_button else self.__nav_buttons[0]

        self.__update_active_button(target_button)
        self.__content_area.clear()
        with self.__content_area:
            home = HomePage()
            home.render()

    def load_settings_page(self, nav_button : SideButton = None):
        # If no button is passed, default to first 
        target_button = nav_button if nav_button else self.__nav_buttons[0]

        self.__update_active_button(target_button)
        self.__content_area.clear()
        with self.__content_area:
            home = SettingsPage()
            home.render()

    def build_ui(self):
        # Access the colour object
        colours = self.__settings.theme

        # Clears the list each refresh to stop lack of sync
        self.__nav_buttons.clear()
        
        # Setup the Theme using the palette
        ui.query('body').style(f'background-color: {colours.background}')
        
        # Setup the Sidebar 
        with ui.left_drawer().style(f'background-color: {colours.surface}; flex-wrap: wrap; align-content: center; padding: 0; padding-bottom: 20px;').classes(f'flex flex-col items-center gap-0'):
            ui.label('FINVEST').style(f'color: {colours.text_primary}; font-size: 24px; font-weight: bold; margin-bottom: 20px;').classes(f'p-5 flex items-center justify-center w-full')

            homeBtn = SideButton(buttonLabel='Home', icon='home', callbackFunction= lambda : self.load_home_page(homeBtn))
            chartsBtn = SideButton(buttonLabel='Charts', icon='assessment', callbackFunction= lambda : self.load_home_page(chartsBtn))
            simulationBtn = SideButton(buttonLabel='Simulation', icon='repeat', callbackFunction= lambda : self.load_home_page(simulationBtn))
            portfolioBtn = SideButton(buttonLabel='Portfolio', icon='pie_chart', callbackFunction= lambda : self.load_home_page(portfolioBtn))
            newsBtn = SideButton(buttonLabel='News', icon='newspaper', callbackFunction= lambda : self.load_home_page(newsBtn))

            ui.space()

            settingsBtn = SideButton(buttonLabel='Settings', icon='settings', callbackFunction= lambda : self.load_settings_page(settingsBtn))


            self.__nav_buttons.extend([homeBtn, chartsBtn, simulationBtn, portfolioBtn, newsBtn, settingsBtn])

        # Setup the Main Content Area
        self.__content_area = ui.column().classes('w-full p-4')

        # SET DEFAULT VIEW
        # explicitly call load_home_page with homeBtn to trigger the 
        # __update_active_button logic immediately on load.
        if self.__nav_buttons:
            self.load_home_page(self.__nav_buttons[0])

    
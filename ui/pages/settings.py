from nicegui import ui
from modules.globalSettings import GlobalSettings
from ui.pages.components.settingsTile import SettingsTile

class SettingsPage:
    def __init__(self, settings: GlobalSettings):
        self.__settings = settings

    def placeholder():
        pass

    def render(self):
        colours = self.__settings.theme
        
        ui.label('Settings').style(f'color: {colours.text_primary}; font-size: 200%')

        SettingsTile("Dark mode", "dark_mode", "#5d47ff", "white", False, lambda: self.placeholder() )
        
        
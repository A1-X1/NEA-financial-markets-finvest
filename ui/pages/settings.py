from nicegui import ui
from modules.globalSettings import GlobalSettings, globalSettings
from modules.colourScheme import Theme, DarkTheme
from ui.pages.components.settingsTile import SettingsTile
from modules.database.database import cursor, connection
import pickle

class SettingsPage:
    def __init__(self):
        self.__settings = globalSettings

    def placeholder():
        pass

    def updateSettingsAndStore(self):
        settings = globalSettings
        settings.currentPage = "settings"

        if (settings.darkMode == True):
            settings.theme = Theme
            settings.darkMode = False
        else:
            settings.theme = DarkTheme
            settings.darkMode = True

        binaryData = pickle.dumps(settings)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS GlobalSettingsTable (
                id INTEGER PRIMARY KEY CHECK (id = 1), 
                data BLOB
            )
        """)

        cursor.execute("""
            INSERT OR REPLACE INTO GlobalSettingsTable (id, data) 
            VALUES (1, ?)
        """, (binaryData,))

        connection.commit()

        print("Updated Settings Table")

        # 3. UI CALLBACK: Force Refresh
        ui.notify("Theme Updated!")
        ui.run_javascript('window.location.reload()')

    def render(self):
        colours = self.__settings.theme
        
        ui.label('Settings').style(f'color: {colours.text_primary}; font-size: 200%')

        SettingsTile("Dark mode", "dark_mode", "#5d47ff", "white", False, lambda: self.updateSettingsAndStore() )
        
        
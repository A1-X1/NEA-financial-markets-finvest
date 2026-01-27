from nicegui import ui
from modules.globalSettings import GlobalSettings, globalSettings
from ui.pages.components.settingsTile import SettingsTile
from modules.database.database import cursor, connection
import pickle

class SettingsPage:
    def __init__(self):
        self.__settings = globalSettings

    def placeholder():
        pass

    def updateSettingsAndStore(self, settings : GlobalSettings):


        binaryData = pickle.dumps(settings)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS GlobalSettingsTable (
                id INTEGER PRIMARY KEY CHECK (id = 1), 
                data BLOB
            )
        """)

        cursor.execute("""
            INSERT OR REPLACE INTO GlobalSettings (id, data) 
            VALUES (1, ?)
        """, (binaryData,))

        connection.commit()

    def render(self):
        colours = self.__settings.theme
        
        ui.label('Settings').style(f'color: {colours.text_primary}; font-size: 200%')

        SettingsTile("Dark mode", "dark_mode", "#5d47ff", "white", False, lambda: self.placeholder() )
        
        
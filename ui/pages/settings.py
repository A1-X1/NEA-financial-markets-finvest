from nicegui import ui
from modules.globalSettings import GlobalSettings, globalSettings
from modules.colourScheme import Theme, DarkTheme
from ui.pages.components.settingsTile import SettingsTile
from ui.pages.components.settingsInput import SettingsInput
from modules.database.database import cursor, connection
import pickle

class SettingsPage:
    def __init__(self):
        self.__settings = globalSettings
        self.__currencyInput : SettingsInput = None

    def placeholder():
        pass

    def storeNewSettings(self, newSettings : GlobalSettings):

        binaryData = pickle.dumps(newSettings)
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

    def toggleDarkMode(self):
        settings = globalSettings

        if (settings.darkMode == True):
            settings.theme = Theme
            settings.darkMode = False
        else:
            settings.theme = DarkTheme
            settings.darkMode = True

        self.storeNewSettings(settings)

        # UI CALLBACK: Force Refresh
        ui.run_javascript('window.location.reload()')

    def toggleAccessibilityMode(self):
        settings = globalSettings

        if (settings.accessibilityMode == True):
            settings.fontWeight = 500
            settings.accessibilityMode = False
        else:
            settings.fontWeight = 700
            settings.accessibilityMode = True

        self.storeNewSettings(settings)

        # UI CALLBACK: Force Refresh
        ui.run_javascript('window.location.reload()')

    def updateCurrency(self):
        settings = globalSettings
        newCurrency = self.__currencyInput.current_value

        if (newCurrency == None):
            return
        else:
            settings.currency = newCurrency

        self.storeNewSettings(settings)

        # UI CALLBACK: Force Refresh
        ui.run_javascript('window.location.reload()')

    def render(self):
        colours = self.__settings.theme
        
        ui.label('Settings').style(f'color: {colours.text_primary}; font-size: 200%')

        SettingsTile("Dark mode", "dark_mode", "#5d47ff", "white", self.__settings.darkMode, lambda: self.toggleDarkMode())
        SettingsTile("Accessibility mode", "visibility", "#cf9800", "white", self.__settings.accessibilityMode, lambda: self.toggleAccessibilityMode())
        self.__currencyInput = SettingsInput("Currency", "monetization_on", "#08a112", "white", self.__settings.currency, lambda: self.updateCurrency())
        
        
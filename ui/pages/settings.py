from nicegui import ui
from modules.globalSettings import GlobalSettings, globalSettings
from modules.colourScheme import Theme, DarkTheme
from ui.pages.components.settingsTile import SettingsTile
from ui.pages.components.settingsInput import SettingsInput
from modules.database.database import cursor, connection
import pickle
from currency_codes import get_currency_by_code, Currency
from currency_symbols import CurrencySymbols

class SettingsPage:
    def __init__(self):
        self.__settings = globalSettings
        self.__currencyInput : SettingsInput = None

    # method for storing new settings
    def storeNewSettings(self, newSettings : GlobalSettings):

        # serialise the settings object
        binaryData = pickle.dumps(newSettings)

        # create table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS GlobalSettingsTable (
                id INTEGER PRIMARY KEY CHECK (id = 1), 
                data BLOB
            )
        """)

        # insert or replace the settings object
        cursor.execute("""
            INSERT OR REPLACE INTO GlobalSettingsTable (id, data) 
            VALUES (1, ?)
        """, (binaryData,))

        # commit the transaction
        connection.commit()

    # method for toggling dark mode
    def toggleDarkMode(self):
        settings = globalSettings

        # toggle dark mode (boolean inversion logi)
        if (settings.darkMode == True):
            settings.theme = Theme
            settings.darkMode = False
        else:
            settings.theme = DarkTheme
            settings.darkMode = True

        self.storeNewSettings(settings)

        # ui callback force refresh
        ui.run_javascript('window.location.reload()')

    # method for toggling accessibility mode
    def toggleAccessibilityMode(self):
        settings = globalSettings

        # toggle accessibility mode (boolean inversion logic)
        if (settings.accessibilityMode == True):
            settings.fontWeight = 500
            settings.accessibilityMode = False
        else:
            settings.fontWeight = 700
            settings.accessibilityMode = True

        self.storeNewSettings(settings)

        # ui callback: force refresh
        ui.run_javascript('window.location.reload()')

    # method for updating currency
    def updateCurrency(self, currency : str):
        settings = globalSettings
        
        # get currency object from code
        newCurrency = get_currency_by_code(currency)

        # if currency is invalid, exit method
        if (newCurrency == None):
            return
        else:
            settings.currency = newCurrency
            settings.currencySymbol = CurrencySymbols.get_symbol(currency)

        self.storeNewSettings(settings)

        # ui callback force refresh
        ui.run_javascript('window.location.reload()')

    # method for rendering the settings page
    def render(self):
        colours = self.__settings.theme
        
        ui.label('Settings').style(f'color: {colours.text_primary}; font-size: 200%')

        SettingsTile("Dark mode", "dark_mode", "#5d47ff", "white", self.__settings.darkMode, lambda: self.toggleDarkMode())
        SettingsTile("Accessibility mode", "visibility", "#cf9800", "white", self.__settings.accessibilityMode, lambda: self.toggleAccessibilityMode())
        self.__currencyInput = SettingsInput("Currency", "monetization_on", "#08a112", "white", self.__settings.currency.code, lambda newCurrency : self.updateCurrency(newCurrency))
        
        
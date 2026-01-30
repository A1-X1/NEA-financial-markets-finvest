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

    # stores the new settings in the database creates table if it doesn't exist
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

        # commit the changes
        connection.commit()

    # toggles dark mode and stores the new settings
    def toggleDarkMode(self):
        settings = globalSettings

        # toggle the dark mode (boolean inversion logic)
        if (settings.darkMode == True):
            settings.theme = Theme
            settings.darkMode = False
        else:
            settings.theme = DarkTheme
            settings.darkMode = True

        self.storeNewSettings(settings)

        # ui callback to force refresh
        ui.run_javascript('window.location.reload()')

    # toggles accessibility mode and stores the new settings
    def toggleAccessibilityMode(self):
        settings = globalSettings

        # toggle the accessibility mode (boolean inversion logic)
        if (settings.accessibilityMode == True):
            settings.fontWeight = 500
            settings.accessibilityMode = False
        else:
            settings.fontWeight = 700
            settings.accessibilityMode = True

        self.storeNewSettings(settings)

        # ui callback to force refresh
        ui.run_javascript('window.location.reload()')

    # updates the currency and stores the new settings
    def updateCurrency(self, currency : str):
        settings = globalSettings
        
        # get the currency object
        newCurrency = get_currency_by_code(currency)

        # if the currency doesn't exist, exit the function
        if (newCurrency == None):
            return
        else:
            settings.currency = newCurrency
            settings.currencySymbol = CurrencySymbols.get_symbol(currency)

        # store the new settings
        self.storeNewSettings(settings)

        # ui callback to force refresh
        ui.run_javascript('window.location.reload()')

    # renders the settings page
    def render(self):
        colours = self.__settings.theme
        
        ui.label('Settings').style(f'color: {colours.text_primary}; font-size: 200%')

        # render the settings tiles with relevant callbacks
        SettingsTile("Dark mode", "dark_mode", "#5d47ff", "white", self.__settings.darkMode, lambda: self.toggleDarkMode())
        SettingsTile("Accessibility mode", "visibility", "#cf9800", "white", self.__settings.accessibilityMode, lambda: self.toggleAccessibilityMode())
        self.__currencyInput = SettingsInput("Currency", "monetization_on", "#08a112", "white", self.__settings.currency.code, lambda newCurrency : self.updateCurrency(newCurrency))
        
        
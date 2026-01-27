from dataclasses import dataclass
import pickle
from modules.colourScheme import ColourScheme, Theme
from modules.database.database import cursor, connection

@dataclass
class GlobalSettings:
    def __init__(self):
        # Default Forest Green palette from Section 2 of the Spec
        self.__theme : ColourScheme = Theme
        self.__currency : str = "USD" 
        self.__currentPage : str = None
        self.__fontWeight : int = 400
        
        # Switches for settings page
        self.__darkMode : bool = False
        self.__accessibilityMode : bool = False

    @property
    def fontWeight(self) -> int:
        return self.__fontWeight
    
    @fontWeight.setter
    def fontWeight(self, value : int):
        self.__fontWeight = value

    @property
    def accessibilityMode(self) -> bool:
        return self.__accessibilityMode
    
    @accessibilityMode.setter
    def accessibilityMode(self, value : bool):
        self.__accessibilityMode = value

    @property
    def currentPage(self) -> str:
        return self.__currentPage
    
    @currentPage.setter
    def currentPage(self, value : str):
        self.__currentPage = value

    @property
    def theme(self) -> ColourScheme:
        return self.__theme

    @theme.setter
    def theme(self, value: ColourScheme):
        if isinstance(value, ColourScheme):
            self.__theme = value
        else:
            # Type checking ensures the UI doesn't break at runtime
            raise TypeError("Theme must be an instance of ColourScheme")
        
    @property
    def darkMode(self) -> bool:
        return self.__darkMode
    
    @darkMode.setter
    def darkMode(self, value : bool):
        self.__darkMode = value

    @property
    def currency(self) -> str:
        return self.__currency

    @currency.setter
    def currency(self, value: str):
        self.__currency = value

    def load_from_db(self):
        try:
            cursor.execute("SELECT data FROM GlobalSettingsTable WHERE id = 1")
            row = cursor.fetchone()
            if row:
                # Reconstruct the singleton state from the BLOB
                saved_settings : GlobalSettings = pickle.loads(row[0])
                instance : GlobalSettings = self() # Get the singleton instance
                instance.theme = saved_settings.theme
                instance.darkMode = saved_settings.darkMode
                instance.currency = saved_settings.currency
                print("Settings loaded successfully from Database.")
        except Exception as e:
            print(f"Error loading settings: {e}")

globalSettings = GlobalSettings()
from dataclasses import dataclass
import pickle
from modules.colourScheme import ColourScheme, Theme
from modules.database.database import cursor, connection
from currency_codes import Currency, CurrencyNotFoundError, get_currency_by_code

@dataclass
class GlobalSettings:
    __instance = None
        
    def __new__(cls):

        # if no instance exists, create one and initialize attributes ensuring only one instance is ever created
        if cls.__instance is None:
            cls.__instance = super(GlobalSettings, cls).__new__(cls)
            cls.__instance.__initialize_attributes()
            cls.__instance.load_from_db()
        return cls.__instance
    
    def __initialize_attributes(self):

        # instance attributes
        self.__theme : ColourScheme = Theme
        self.__currency : Currency = get_currency_by_code('USD')
        self.__currentPage : str = None
        self.__fontWeight : int = 500
        self.__currencySymbol : str = '$'
        
        # switches data for settings page
        self.__darkMode : bool = False
        self.__accessibilityMode : bool = False

    # property decorator allows us to use getter methods like normal functions
    @property
    def currencySymbol(self) -> str:
        return self.__currencySymbol
    
    # setter decorator allows us to use setter methods like normal functions
    @currencySymbol.setter
    def currencySymbol(self, value: str):
        self.__currencySymbol = value


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
            # type checking ensures there won't be runtime errors
            raise TypeError("Theme must be an instance of ColourScheme")
        
    @property
    def darkMode(self) -> bool:
        return self.__darkMode
    
    @darkMode.setter
    def darkMode(self, value : bool):
        self.__darkMode = value

    @property
    def currency(self) -> Currency:
        return self.__currency

    @currency.setter
    def currency(self, value: Currency):
        self.__currency = value

    def load_from_db(self):
        try:
            cursor.execute("SELECT data FROM GlobalSettingsTable WHERE id = 1")
            row = cursor.fetchone()
            if row:
                # reconstruct the singleton state from the blob from database
                saved_settings : GlobalSettings = pickle.loads(row[0])

                # get the singleton instance
                instance : GlobalSettings = self() 

                # update the singleton instance with the loaded settings
                instance.theme = saved_settings.theme
                instance.darkMode = saved_settings.darkMode
                instance.currency = saved_settings.currency
                print("Settings loaded successfully from Database.")
        except Exception as e:
            print(f"Error loading settings: {e}")

# create the singleton instance
globalSettings = GlobalSettings()
from dataclasses import dataclass
from modules.colourScheme import ColourScheme, Theme

@dataclass
class GlobalSettings:
    def __init__(self):
        # Default Forest Green palette from Section 2 of the Spec
        self.__theme = Theme
        self.__currency = "USD"

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
    def currency(self) -> str:
        return self.__currency

    @currency.setter
    def currency(self, value: str):
        self.__currency = value

globalSettings = GlobalSettings()
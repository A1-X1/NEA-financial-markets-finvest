from dataclasses import dataclass
from modules.colourScheme import ColourScheme

@dataclass
class GlobalSettings:
    def __init__(self):
        # Default Forest Green palette from Section 2 of the Spec
        self.__theme = ColourScheme(
            bg='#FFFFFF',
            surface='#F8F8FA',
            accent='#24986D',
            btn_bg='#E2F0ED',
            btn_fg='#24986D',
            text_p='#0E7850',
            text_s='#000000',
            text_ph='#C4C4C4',
            pos='#10B981',
            neg='#EF4444',
            sb_act_bg='#E2F0ED',
            sb_act_fg='#24986D',
            sb_inact_bg='#F8F8FA',
            sb_inact_fg='#7C8D88'
        )
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
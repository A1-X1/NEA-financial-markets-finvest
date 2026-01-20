from dataclasses import dataclass

@dataclass
class GlobalSettings:
    def __init__(self):
        self.__currency = "USD"
        self.__risk_threshold = 0.05
        self.__ui_theme = "Dark Forest"

    @property
    def currency(self) -> str:
        return self.__currency

    @currency.setter
    def currency(self, value: str):
        valid_currencies = ["USD", "GBP", "EUR", "JPY"]
        if value in valid_currencies:
            self.__currency = value
        else:
            raise ValueError(f"Unsupported currency: {value}")

    @property
    def risk_threshold(self) -> float:
        return self.__risk_threshold

    @risk_threshold.setter
    def risk_threshold(self, value: float):
        if 0 < value <= 1:
            self.__risk_threshold = value
        else:
            raise ValueError("Risk threshold must be between 0 and 1")
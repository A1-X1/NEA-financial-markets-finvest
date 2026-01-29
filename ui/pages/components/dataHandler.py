import yfinance as yf
import pandas as pd
from dataclasses import dataclass

@dataclass
class DataHandler:
    __ticker_symbol: str = "AAPL"
    __period: str = "1mo"
    __raw_data: pd.DataFrame = None
    __processed_data: pd.DataFrame = None

    @property
    def ticker_symbol(self) -> str:
        return self.__ticker_symbol

    @ticker_symbol.setter
    def ticker_symbol(self, value: str):
        if not value or not isinstance(value, str):
            raise ValueError("DataHandler: Ticker symbol must be a non-empty string.")
        self.__ticker_symbol = value.upper()

    @property
    def period(self) -> str:
        return self.__period

    @period.setter
    def period(self, value: str):
        valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
        if value not in valid_periods:
            raise ValueError(f"DataHandler: Period must be one of {valid_periods}")
        self.__period = value

    @property
    def raw_data(self) -> pd.DataFrame:
        return self.__raw_data

    def fetch_market_data(self):
        ticker = yf.Ticker(self.__ticker_symbol)
        data = ticker.history(period=self.__period)
        
        if data.empty:
            raise ValueError(f"DataHandler: No data found for ticker '{self.__ticker_symbol}'.")
        
        # reset_index moves 'Date' from the index to a column
        self.__raw_data = data.reset_index()
        return self.__raw_data

    def prepare_risk_data(self):
        if self.__raw_data is None:
            raise ValueError("DataHandler: Cannot prepare data before fetching.")
        
        df = self.__raw_data.copy()
        
        # Calculate returns (Math operations work best on Timestamps, so we do this first)
        df['Daily_Return'] = df['Close'].pct_change()
        df['Volatility'] = df['Daily_Return'].rolling(window=5).std()
        
        df = df.dropna()

        # --- THE FIX IS HERE ---
        # Convert the 'Date' column from Timestamp objects to Strings.
        # JSON cannot handle Timestamp objects, but it can handle Strings.
        if 'Date' in df.columns:
            df['Date'] = df['Date'].astype(str)
        
        self.__processed_data = df
        return self.__processed_data
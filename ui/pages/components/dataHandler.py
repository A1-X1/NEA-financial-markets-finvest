import yfinance as yf
import pandas as pd
from dataclasses import dataclass

@dataclass
class DataHandler:
    # stores the private attributes for ticker symbol, period, raw data, processed data and currency
    __ticker_symbol: str = "AAPL"
    __period: str = "1mo"
    __raw_data: pd.DataFrame = None
    __processed_data: pd.DataFrame = None
    __currency: str = "USD"  # Default fallback

    # fetches the market data
    def fetch_market_data(self):
        # prints the ticker symbol and period
        print(f'Fetching data for {self.__ticker_symbol} with period {self.__period}')
        ticker = yf.Ticker(self.__ticker_symbol)
        
        # fetch data
        data = ticker.history(period=self.__period)
        
        if data.empty:
            raise ValueError(f"DataHandler: No data found for ticker '{self.__ticker_symbol}'.")
        
        # fetch currency (using info dict)
        try:
            self.__currency = ticker.info.get('currency', 'USD')
            print(f'Currency for generated graph is: {self.__currency}')
        except Exception:
            # incase of error use usd as default
            self.__currency = "USD" 

        # store raw data
        self.__raw_data = data.reset_index()
        return self.__raw_data

    # prepares the data for risk analysis
    def prepare_risk_data(self):
        if self.__raw_data is None:
            raise ValueError("DataHandler: Cannot prepare data before fetching.")
        
        df = self.__raw_data.copy()
        
        # calculate returns
        df['Daily_Return'] = df['Close'].pct_change()
        df['Volatility'] = df['Daily_Return'].rolling(window=5).std()
        
        df = df.dropna()

        if 'Date' in df.columns:
            df['Date'] = df['Date'].astype(str)
        
        self.__processed_data = df
        return self.__processed_data

    # getters and setters
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
    def currency(self) -> str:
        return self.__currency

    @property
    def raw_data(self) -> pd.DataFrame:
        return self.__raw_data



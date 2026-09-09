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



    @staticmethod
    def get_current_prices(tickers: list) -> dict:
        # fetches {ticker: {'price': float, 'currency': str}}
        if not tickers:
            return {}
            
        try:
            tickers_str = " ".join(tickers)
            # fetch valid data
            ticker_objs = yf.Tickers(tickers_str)
            
            # if multiple tickers, download returns dataframe
            data = yf.download(tickers_str, period="1d", progress=False)['Close']
            
            results = {}
            if len(tickers) == 1:
                price = data.iloc[-1].item() if not data.empty else 0.0
                try:
                    currency = ticker_objs.tickers[tickers[0]].info.get('currency', 'USD')
                except:
                    currency = 'USD'
                results[tickers[0]] = {'price': price, 'currency': currency}
            else:
                current_vals = data.iloc[-1]
                for tick in tickers:
                    price = current_vals[tick] if tick in current_vals else 0.0
                    try:
                        currency = ticker_objs.tickers[tick].info.get('currency', 'USD')
                    except:
                        currency = 'USD'
                    results[tick] = {'price': price, 'currency': currency}
                    
            return results
        except Exception as e:
            print(f"Error fetching prices: {e}")
            return {t: {'price': 0.0, 'currency': 'USD'} for t in tickers}

    @staticmethod
    def get_exchange_rate(from_currency: str, to_currency: str) -> float:
        # fetching exchange rate from Yahoo Finance
        if from_currency == to_currency:
            return 1.0
        
        # crypto/major pairs usually work like GBPUSD=X
        pair = f"{from_currency}{to_currency}=X" 
        try:
            data = yf.Ticker(pair).history(period="1d")
            if not data.empty:
                return data['Close'].iloc[-1]
            
            # try inverse
            pair_inv = f"{to_currency}{from_currency}=X"
            data_inv = yf.Ticker(pair_inv).history(period="1d")
            if not data_inv.empty:
                return 1.0 / data_inv['Close'].iloc[-1]
            
            # fallback value
            return 1.0
        except:
            return 1.0

    @staticmethod
    def get_currency_symbol(code: str) -> str:
        symbols = {'USD': '$', 'GBP': '£', 'EUR': '€', 'JPY': '¥', 'AUD': 'A$', 'CAD': 'C$'}
        return symbols.get(code, code)

import numpy as np
from ui.pages.components.dataHandler import DataHandler
from modules.calculations import generate_gbm_paths

class SimulationEngine:
    def __init__(self):
        # private attributes for simulation parameters
        self.__volatility = 0.2
        self.__drift = 0.05
        self.__risk_free_rate = 0.02
        self.__num_simulations = 100
        self.__num_steps = 252
        self.__initial_price = 100.0
        self.__ticker = ""

    # getters and setters with strict validation
    @property
    def volatility(self):
        return self.__volatility

    @volatility.setter
    def volatility(self, value):
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("volatility must be a non-negative number")
        self.__volatility = float(value)

    @property
    def drift(self):
        return self.__drift

    @drift.setter
    def drift(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("drift must be a number")
        self.__drift = float(value)

    @property
    def risk_free_rate(self):
        return self.__risk_free_rate

    @risk_free_rate.setter
    def risk_free_rate(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("risk free rate must be a number")
        self.__risk_free_rate = float(value)

    @property
    def num_simulations(self):
        return self.__num_simulations

    @num_simulations.setter
    def num_simulations(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("number of simulations must be a positive integer")
        if value > 10000:
            raise ValueError("limit simulations to 10,000 for performance")
        self.__num_simulations = value

    @property
    def num_steps(self):
        return self.__num_steps

    @num_steps.setter
    def num_steps(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("number of steps must be a positive integer")
        self.__num_steps = value

    @property
    def ticker(self):
        return self.__ticker

    @ticker.setter
    def ticker(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("ticker must be a non-empty string")
        self.__ticker = value.upper()

    def fetch_parameters_from_market(self, ticker, period="1y"):
        # fetches historical data to estimate drift and volatility
        handler = DataHandler()
        handler.ticker_symbol = ticker
        handler.period = period
        data = handler.fetch_market_data()
        
        if data.empty:
            raise ValueError(f"no data found for ticker {ticker}")
            
        # calculate log returns
        close_prices = data['Close'].values
        log_returns = np.diff(np.log(close_prices))
        
        # estimate annualised drift and volatility
        # simplified drift: mean of log returns * 252 + 0.5 * sigma^2
        sigma = np.std(log_returns) * np.sqrt(252)
        mu = np.mean(log_returns) * 252 + 0.5 * sigma**2
        
        self.__ticker = ticker.upper()
        self.__initial_price = close_prices[-1]
        self.__volatility = sigma
        self.__drift = mu
        
        return {
            'initial_price': self.__initial_price,
            'volatility': self.__volatility,
            'drift': self.__drift
        }

    def run_simulation(self):
        # runs the gbm simulation
        # dt is time step size (annualised)
        dt = 1 / 252 # assuming 252 trading days per year
        
        paths = generate_gbm_paths(
            self.__initial_price,
            self.__drift,
            self.__volatility,
            self.__num_simulations,
            self.__num_steps,
            dt
        )
        
        return paths

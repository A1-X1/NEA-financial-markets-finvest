from nicegui import ui, run
from modules.globalSettings import globalSettings
from ui.pages.components.dataHandler import DataHandler
from ui.pages.components.visualisation import RiskTrendVisualisation, PortfolioVisualisation, GBMVisualisation
from modules.simulationEngine import SimulationEngine
from modules.database.database import cursor, connection
import pandas as pd
import pickle

class HomeWidget(ui.element):
    # initialises the widget
    def __init__(self, title: str):
        # initialise parent as a div
        super().__init__('div') 
        
        # gets the theme from singleton instance of globalSettings
        theme = globalSettings.theme

        # applies styling through tailwind classes and theme
        self.classes('w-full h-[400px] flex flex-col p-4 gap-4 rounded-xl shadow-sm border border-gray-100/10')
        self.classes(f'bg-[{theme.surface}] text-[{theme.text_primary}]')

        # creates the title and more icon with options menu
        with self:
            with ui.row().classes('w-full items-center justify-between'):
                ui.label(title).classes('text-lg font-bold tracking-wide')
                
                # more options menu
                with ui.element('div'):
                    more_icon = ui.icon('more_horiz').classes(f'text-[{theme.text_secondary}] cursor-pointer')
                    with ui.menu() as menu:
                        ui.menu_item('Move Up', on_click=lambda: self.__handle_action('move_up')).classes('text-sm')
                        ui.menu_item('Move Down', on_click=lambda: self.__handle_action('move_down')).classes('text-sm')
                        ui.separator()
                        ui.menu_item('Delete', on_click=lambda: self.__handle_action('delete')).classes('text-sm text-red-500')
                    
                    more_icon.on('click', menu.open)

            self.__content_container = ui.element('div').classes('w-full flex-grow relative overflow-hidden')
            with self.__content_container:
                pass 

        # callbacks for actions
        self.on_action = None

    def __handle_action(self, action: str):
        if self.on_action:
            self.on_action(action)

    @property
    def content(self):
        return self.__content_container
    
# creates a child class of HomeWidget for Market Charts
class MarketChartWidget(HomeWidget):
    def __init__(self, title: str, ticker: str, chart_mode: str = 'Line', timeframe: str = '1mo'):
        super().__init__(title)
        
        # stores the ticker symbol, chart view preference and data handler
        self.__ticker = ticker
        self.__chart_mode = chart_mode
        self.__handler = DataHandler()
        self.__handler.ticker_symbol = self.__ticker
        self.__handler.period = timeframe

        # creates the chart container and refreshes the data
        with self.content:
            self.__chart_container = ui.element('div').classes('w-full h-full flex items-center justify-center')
            ui.timer(0.1, self.refresh_data, once=True)

    # refreshes the data
    async def refresh_data(self):
        try:
            # fetch data
            await run.io_bound(self.__handler.fetch_market_data)
            processed_data = self.__handler.prepare_risk_data()
            
            # get currency
            market_currency = self.__handler.currency

            # create visualisation (pass currency)
            viz = RiskTrendVisualisation(
                title_input=f"{self.__ticker} Trend",
                data_input=processed_data,
                currency_input=market_currency
            )
            fig = viz.generate_chart(chart_mode=self.__chart_mode)
            
            # remove redundant title inside the plot for homepage
            fig.update_layout(title="", margin=dict(l=10, r=10, t=10, b=10))

            # render
            with self.__chart_container:
                self.__chart_container.clear()
                ui.plotly(fig).classes('w-full h-full')
                
        # error handling
        except Exception as e:
            with self.__chart_container:
                self.__chart_container.clear()
                ui.label(f"{self.__ticker} Error: {str(e)}").classes('text-red-400 text-xs text-center p-4')

# child class for Portfolio Visualization
class PortfolioChartWidget(HomeWidget):
    def __init__(self, portfolio_name: str = "New Portfolio"):
        super().__init__(f"Portfolio: {portfolio_name}")
        self.__name = portfolio_name
        
        with self.content:
            self.__chart_container = ui.element('div').classes('w-full h-full flex items-center justify-center')
            ui.timer(0.1, self.refresh_data, once=True)

    async def refresh_data(self):
        try:
            # load from db
            cursor.execute("SELECT data FROM PortfoliosTable WHERE name = ?", (self.__name,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Portfolio '{self.__name}' not found")
            
            items = pickle.loads(row[0])
            if not items:
                raise ValueError("Portfolio is empty")

            # fetch prices
            tickers = [item[0] for item in items]
            raw_prices = await run.io_bound(DataHandler.get_current_prices, tickers)
            
            user_ccy = globalSettings.currency.code
            plot_data = []
            
            for ticker, quantity in items:
                data = raw_prices.get(ticker, {'price': 0.0, 'currency': 'USD'})
                val_native = data['price'] * quantity
                rate = DataHandler.get_exchange_rate(data['currency'], user_ccy)
                plot_data.append({'Ticker': ticker, 'Value': val_native * rate})

            df = pd.DataFrame(plot_data)
            viz = PortfolioVisualisation(title_input="", data_input=df, currency_input=user_ccy)
            fig = viz.generate_pie_chart()
            fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))

            with self.__chart_container:
                self.__chart_container.clear()
                ui.plotly(fig).classes('w-full h-full')

        except Exception as e:
            with self.__chart_container:
                self.__chart_container.clear()
                ui.label(f"Portfolio Error: {str(e)}").classes('text-red-400 text-xs text-center p-4')

# child class for Simulation Visualization
class SimulationChartWidget(HomeWidget):
    def __init__(self, title: str, ticker: str, timeframe: str = '1y', rfr: float = 0.02, sims: int = 500, steps: int = 252):
        super().__init__(title)
        self.__params = {
            'ticker': ticker,
            'period': timeframe,
            'rfr': rfr,
            'sims': sims,
            'steps': steps
        }
        
        with self.content:
            self.__chart_container = ui.element('div').classes('w-full h-full flex items-center justify-center')
            ui.timer(0.1, self.refresh_data, once=True)

    async def refresh_data(self):
        try:
            engine = SimulationEngine()
            engine.ticker = self.__params['ticker']
            engine.risk_free_rate = self.__params['rfr']
            engine.num_simulations = self.__params['sims']
            engine.num_steps = self.__params['steps']

            # fetch params
            await run.io_bound(engine.fetch_parameters_from_market, engine.ticker, period=self.__params['period'])
            
            # run simulation
            from ui.pages.simulation import compute_simulation
            df = await run.cpu_bound(compute_simulation, engine)

            viz = GBMVisualisation(title_input="", data_input=df, currency_input="USD")
            fig = viz.generate_chart()
            fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))

            with self.__chart_container:
                self.__chart_container.clear()
                ui.plotly(fig).classes('w-full h-full')

        except Exception as e:
            with self.__chart_container:
                self.__chart_container.clear()
                ui.label(f"Simulation Error: {str(e)}").classes('text-red-400 text-xs text-center p-4')
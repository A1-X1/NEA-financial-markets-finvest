from nicegui import ui
import pandas as pd
from modules.globalSettings import globalSettings
from ui.pages.components.hashTable import HashTable
from ui.pages.components.dataHandler import DataHandler
from ui.pages.components.visualisation import PortfolioVisualisation
import csv
import io
import pickle
from modules.database.database import cursor, connection

class PortfolioPage:
    def __init__(self):
        self.__settings = globalSettings
        # Instantiate the custom HashTable
        self.__portfolio_data = HashTable(capacity=50) 
        
        self.__ticker_input = None
        self.__shares_input = None
        self.__table_container = None
        self.__chart_container = None
        
        self.__polling_timer = None
        
        # Load any saved state (optional extension)
        self.__load_portfolio()

    def __load_portfolio(self):
        """Loads portfolio from DB if exists (Simple persistence)"""
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='PortfolioTable'")
            if not cursor.fetchone():
                return
                
            cursor.execute("SELECT data FROM PortfolioTable WHERE id = 1")
            row = cursor.fetchone()
            if row:
                # We stored a list of tuples, simpler for pickling than the whole object
                items = pickle.loads(row[0])
                for ticker, quantity in items:
                    self.__portfolio_data.put(ticker, quantity)
        except Exception:
            pass

    def __save_portfolio(self):
        """Persists custom hashtable content to DB"""
        try:
            items = self.__portfolio_data.get_all()
            binary_data = pickle.dumps(items)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS PortfolioTable (
                    id INTEGER PRIMARY KEY CHECK (id = 1), 
                    data BLOB
                )
            """)
            cursor.execute("INSERT OR REPLACE INTO PortfolioTable (id, data) VALUES (1, ?)", (binary_data,))
            connection.commit()
            ui.notify('Portfolio Saved', color='positive')
        except Exception as e:
            ui.notify(f"Save failed: {e}", color='negative')

    def add_asset(self):
        ticker = self.__ticker_input.value
        shares = self.__shares_input.value
        
        if not ticker or not shares:
            ui.notify('Please provide both Ticker and Shares', color='warning')
            return
            
        try:
            shares = float(shares)
            if shares <= 0:
                raise ValueError
        except:
            ui.notify('Shares must be a positive number', color='warning')
            return
            
        # Put into HashTable (Handles Duplicates/Updates)
        self.__portfolio_data.put(ticker.upper(), shares)
        
        self.__ticker_input.value = ''
        self.__shares_input.value = ''
        
        self.refresh_view()
        ui.notify(f"Added {ticker.upper()}", color='positive')

    def remove_asset(self, ticker):
        if self.__portfolio_data.remove(ticker):
            self.refresh_view()
            ui.notify(f"Removed {ticker}", color='positive')

    def export_csv(self):
        # 1. Get Composition
        items = self.__portfolio_data.get_all()
        if not items:
            ui.notify('Portfolio is empty', color='warning')
            return
            
        tickers = [item[0] for item in items]
        
        # 2. Get Fresh Data (Ensure data integrity)
        prices = DataHandler.get_current_prices(tickers)
        
        # 3. Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Ticker', 'Quantity', 'Current Price', 'Total Value'])
        
        total_value = 0
        for ticker, quantity in items:
            price = prices.get(ticker, 0.0)
            val = price * quantity
            writer.writerow([ticker, quantity, f"{price:.2f}", f"{val:.2f}"])
            total_value += val
            
        writer.writerow([])
        writer.writerow(['Total Portfolio Value', '', '', f"{total_value:.2f}"])
        
        ui.download(output.getvalue().encode('utf-8'), 'portfolio_export.csv')
        ui.notify('CSV Exported', color='positive')

    def refresh_view(self):
        # 1. Get Assets
        items = self.__portfolio_data.get_all()
        if not items:
            self.__chart_container.clear()
            self.__table_container.clear()
            with self.__table_container:
                ui.label('Portfolio is empty').classes('text-gray-400 italic')
            return

        # 2. Fetch Prices
        tickers = [item[0] for item in items]
        prices = DataHandler.get_current_prices(tickers)
        
        # 3. Prepare Data for UI
        table_rows = []
        plot_data = [] # Ticker, Value
        total_mv = 0
        
        for ticker, quantity in items:
            price = prices.get(ticker, 0.0)
            val = price * quantity
            total_mv += val
            
            table_rows.append({
                'Symbol': ticker,
                'Units': quantity,
                'Price': f"${price:.2f}",
                'Value': f"${val:.2f}",
                'action': ticker # for naming the delete button
            })
            
            plot_data.append({'Ticker': ticker, 'Value': val})

        # 4. Render Table
        self.__table_container.clear()
        with self.__table_container:
            # Create a simple clean table manually for full control or use ui.table
            # Using ui.grid for custom row layout as shown in reference image "AAPL 20 (X)"
            
            ui.label('Current Composition').classes('text-lg font-bold mb-2') \
                .style(f'color: {self.__settings.theme.accent}')
            
            # Header
            with ui.row().classes('w-full border-b border-gray-600/20 pb-2 mb-2 justify-between'):
                ui.label('Symbol').classes('w-16 font-semibold')
                ui.label('Units').classes('w-16 font-semibold')
                ui.label('Value').classes('w-24 font-semibold text-right')
                ui.label('').classes('w-8') # Action col
                
            # Rows
            for row in table_rows:
                with ui.row().classes('w-full items-center justify-between py-1'):
                    ui.label(row['Symbol']).classes('w-16')
                    ui.label(str(row['Units'])).classes('w-16')
                    ui.label(row['Value']).classes('w-24 text-right')
                    
                    # Delete Button
                    ui.button(icon='cancel', on_click=lambda t=row['Symbol']: self.remove_asset(t)) \
                        .props('flat dense size=sm color=red') \
                        .classes('w-8')

            # Total
            with ui.row().classes('w-full border-t border-gray-600/20 pt-4 mt-2 justify-between'):
                ui.label('Total Value').classes('font-bold')
                ui.label(f"${total_mv:.2f}").classes('font-bold text-xl')

        # 5. Render Chart
        self.__chart_container.clear()
        with self.__chart_container:
            df = pd.DataFrame(plot_data)
            if not df.empty and total_mv > 0:
                viz = PortfolioVisualisation(
                    title_input=f"Portfolio Value: ${total_mv:,.2f}",
                    data_input=df,
                    currency_input="USD"
                )
                fig = viz.generate_pie_chart()
                ui.plotly(fig).classes('w-full h-full')
            else:
                 ui.label('No Value to Display').classes('self-center text-gray-400')

    def render(self):
        theme = self.__settings.theme
        
        # Consistent Styles (borrowed/adapted from charts.py)
        input_style = (
            f'--custom-input-color: {theme.text_primary}; '
            f'--custom-placeholder-color: {theme.text_placeholder}; '
            f'--custom-accent-soft: {theme.sb_active_bg}; '
            f'--q-primary: {theme.accent};'
        )
        btn_style = f'background-color: {theme.sb_active_bg} !important; color: {theme.sb_active_fg} !important;'

        with ui.element('div').classes('w-full h-full flex flex-col p-8 gap-6'):
            ui.label('Portfolio').style(f'color: {theme.accent}; font-size: 200%; font-weight: bold')

            # Main Grid Layout
            with ui.row().classes('w-full flex-grow gap-8'):
                
                # LEFT: Visualization
                self.__chart_container = ui.card().classes('col-span-1 flex-grow h-[500px] w-2/3 p-4 shadow-sm border border-gray-100/10') \
                    .style(f'background-color: {theme.surface}')
                
                # RIGHT: Controls & Table
                with ui.column().classes('w-1/3 min-w-[300px] gap-6'):
                    
                    # Controls Card
                    with ui.card().classes('w-full p-6 gap-4 shadow-sm border border-gray-100/10').style(f'background-color: {theme.surface}'):
                        self.__ticker_input = ui.input(label='stock ticker symbol') \
                            .classes('w-full input-field').props('outlined dense uppercase').style(input_style)
                            
                        self.__shares_input = ui.input(label='shares owned') \
                            .classes('w-full input-field').props('outlined dense type=number').style(input_style)
                        
                        ui.button('Add to portfolio', on_click=self.add_asset) \
                            .style(btn_style).classes('w-full font-bold').props('flat unelevated')

                    # Composition Table Container
                    self.__table_container = ui.card().classes('w-full p-6 flex-grow shadow-sm border border-gray-100/10') \
                        .style(f'background-color: {theme.surface}')

            # Footer Actions
            with ui.row().classes('gap-4 mt-4'):
                ui.button('Save Portfolio', on_click=self.__save_portfolio) \
                    .style(btn_style).props('flat unelevated')
                
                ui.button('Load Portfolio', on_click=lambda: (self.__load_portfolio(), self.refresh_view())) \
                    .style(btn_style).props('flat unelevated')
                    
                ui.button('Export CSV', on_click=self.export_csv) \
                    .style(btn_style).props('flat unelevated')

        # Initial View
        self.refresh_view()
        
        # START POLLING (Every 10 seconds)
        self.__polling_timer = ui.timer(10.0, self.refresh_view)
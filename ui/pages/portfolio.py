from nicegui import ui
import pandas as pd
from modules.globalSettings import globalSettings
from ui.pages.components.hashTable import HashTable
from ui.pages.components.dataHandler import DataHandler
from ui.pages.components.visualisation import PortfolioVisualisation
import csv
import io
import pickle
import os
from modules.database.database import cursor, connection

# global CSS for Portfolio Page 
ui.add_css('''
    .input-field .q-field__native, .input-field .q-item__label {
        color: var(--custom-input-color) !important;
    }
    
    .input-field .q-field__label, 
    .input-field .q-field__native::placeholder {
        color: var(--custom-placeholder-color) !important;
    }

    .input-field .q-field__control:before {
        border-color: var(--custom-input-color) !important;
        opacity: 0.5; 
    }

    .input-field .q-field__control:hover:before {
        border-color: var(--custom-input-color) !important;
        opacity: 1;
    }

    .q-manual-focusable--focused > .q-focus-helper,
    .q-item--active, 
    .q-item.q-item--clickable:hover {
        background: var(--custom-accent-soft) !important;
        color: var(--custom-input-color) !important;
        opacity: 1 !important;
    }

    .q-item.q-item--active .q-item__section {
        color: var(--custom-input-color) !important;
    }
''', shared=True)

class PortfolioPage:
    def __init__(self):
        self.__settings = globalSettings
        # instantiate the custom HashTable
        self.__portfolio_data = HashTable(capacity=50) 
        
        self.__ticker_input = None
        self.__shares_input = None
        self.__table_container = None
        self.__chart_container = None
        
        self.__polling_timer = None
        self.__current_portfolio_Name = "New Portfolio" # Default
        
        # ensure DB Table Exists
        self.__init_db()

    def __init_db(self):
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS PortfoliosTable (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT UNIQUE,
                    data BLOB
                )
            """)
            connection.commit()
        except Exception as e:
            print(f"DB Init Error: {e}")

    def __load_portfolio_by_name(self, name):
        # loads a specific portfolio by name
        try:
            cursor.execute("SELECT data FROM PortfoliosTable WHERE name = ?", (name,))
            row = cursor.fetchone()
            if row:
                self.__portfolio_data.clear()
                items = pickle.loads(row[0])
                for ticker, quantity in items:
                    self.__portfolio_data.put(ticker, quantity)
                
                self.__current_portfolio_Name = name
                self.refresh_view()
                ui.notify(f"Loaded '{name}'", color='positive')
        except Exception as e:
            ui.notify(f"Load failed: {e}", color='negative')

    def __save_current_portfolio(self, name):
        # saves current hashtable content to DB with a name
        if not name:
             ui.notify("Name cannot be empty", color='warning')
             return

        try:
            items = self.__portfolio_data.get_all()
            if not items:
                 ui.notify("Cannot save empty portfolio", color='warning')
                 return
                 
            binary_data = pickle.dumps(items)
            
            cursor.execute("INSERT OR REPLACE INTO PortfoliosTable (name, data) VALUES (?, ?)", (name, binary_data))
            connection.commit()
            
            self.__current_portfolio_Name = name
            ui.notify(f"Saved as '{name}'", color='positive')
        except Exception as e:
            ui.notify(f"Save failed: {e}", color='negative')

    def __delete_portfolio(self, name, dialog):
        try:
            cursor.execute("DELETE FROM PortfoliosTable WHERE name = ?", (name,))
            connection.commit()
            ui.notify(f"Deleted '{name}'", color='positive')
            dialog.close()
            self.__open_load_dialog() # re open to refresh list
        except Exception as e:
            ui.notify(f"Delete failed: {e}", color='negative')


    def __quick_save(self):
        # saves immediately if already named, otherwise opens dialog
        if self.__current_portfolio_Name == "New Portfolio":
            self.__open_save_dialog()
        else:
            self.__save_current_portfolio(self.__current_portfolio_Name)

    def __open_save_dialog(self):
        theme = self.__settings.theme
        # Dialog Styles
        dialog_style = f'background-color: {theme.surface} !important; color: {theme.text_primary} !important; border: 1px solid {theme.accent} !important;'
        input_style = (
            f'--custom-input-color: {theme.text_primary}; '
            f'--custom-placeholder-color: {theme.text_placeholder}; '
            f'--q-primary: {theme.accent};'
        )
        btn_style = f'background-color: {theme.sb_active_bg} !important; color: {theme.sb_active_fg} !important;'

        with ui.dialog() as dialog, ui.card().style(dialog_style):
            ui.label('Save Portfolio As').classes('text-lg font-bold')
            name_input = ui.input(label='New Name', value="").classes('w-full input-field').style(input_style).props('outlined dense')
            
            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Cancel', on_click=dialog.close).style(f'color: {theme.text_primary} !important').props('flat')
                ui.button('Save', on_click=lambda: (self.__save_current_portfolio(name_input.value), dialog.close())) \
                    .style(btn_style).props('flat unelevated')

        dialog.open()

    def __open_load_dialog(self):
        theme = self.__settings.theme
        dialog_style = f'background-color: {theme.surface} !important; color: {theme.text_primary} !important; border: 1px solid {theme.accent} !important;'
        btn_style = f'background-color: {theme.sb_active_bg} !important; color: {theme.sb_active_fg} !important;'

        with ui.dialog() as dialog, ui.card().classes('w-[400px] h-[400px]').style(dialog_style):
            ui.label('Load Portfolio').classes('text-lg font-bold mb-4')
            
            cursor.execute("SELECT name FROM PortfoliosTable")
            rows = cursor.fetchall()
            
            if not rows:
                ui.label('No saved portfolios found.').classes('italic').style(f'color: {theme.text_secondary} !important')
            else:
                with ui.scroll_area().classes('w-full flex-grow'):
                    for row in rows:
                        name = row[0]
                        # Row Style
                        with ui.row().classes('w-full justify-between items-center border-b py-2').style(f'border-color: {theme.text_secondary}33 !important'):
                            ui.label(name).classes('text-base cursor-pointer hover:font-bold') \
                                .style(f'color: {theme.text_primary} !important') \
                                .on('click', lambda n=name: (self.__load_portfolio_by_name(n), dialog.close()))
                            
                            ui.button(icon='close', on_click=lambda n=name: self.__delete_portfolio(n, dialog)) \
                                .props('flat round dense size=sm').style(f'color: {theme.accent} !important')
                            
            ui.button('Close', on_click=dialog.close).classes('self-end mt-4') \
                .style(f'color: {theme.text_primary} !important').props('flat')
            
        dialog.open()

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
            
        # put into HashTable (handles duplicates/updates)
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
        # get composition
        items = self.__portfolio_data.get_all()
        if not items:
            ui.notify('Portfolio is empty', color='warning')
            return
            
        tickers = [item[0] for item in items]
        
        # get fresh data (ensure data integrity)
        raw_prices = DataHandler.get_current_prices(tickers)
        
        # create CSV
        try:
            downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
            file_path = os.path.join(downloads_path, 'portfolio_export.csv')
            
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Ticker', 'Quantity', 'Price', 'Currency', 'Value (Local)'])
                
                for ticker, quantity in items:
                    data = raw_prices.get(ticker, {'price': 0.0, 'currency': 'USD'})
                    price = data['price']
                    currency = data['currency']
                    val = price * quantity
                    writer.writerow([ticker, quantity, f"{price:.2f}", currency, f"{val:.2f}"])
                
            ui.notify(f'CSV Exported to {file_path}', color='positive')
        except Exception as e:
            ui.notify(f'Export failed: {e}', color='negative')

    def refresh_view(self):
        # update title
        if hasattr(self, '_PortfolioPage__header_label') and self.__header_label:
            self.__header_label.set_text(f'Portfolio: {self.__current_portfolio_Name}')

        # get assets
        items = self.__portfolio_data.get_all()
        if not items:
            self.__chart_container.clear()
            self.__table_container.clear()
            with self.__table_container:
                ui.label('Portfolio is empty').classes('text-gray-400 italic')
            return

        # fetch prices & logic
        tickers = [item[0] for item in items]
        raw_prices = DataHandler.get_current_prices(tickers)
        
        user_currency_obj = self.__settings.currency 
        user_currency_code = user_currency_obj.code if user_currency_obj else 'USD'
        user_currency_symbol = DataHandler.get_currency_symbol(user_currency_code)

        table_rows = []
        plot_data = [] 
        total_mv_user_currency = 0
        
        for ticker, quantity in items:
            data = raw_prices.get(ticker, {'price': 0.0, 'currency': 'USD'})
            price = data['price']
            asset_currency = data['currency']
            
            # value in asset's native currency
            val_native = price * quantity
            asset_symbol = DataHandler.get_currency_symbol(asset_currency)
            
            # convert to user's preferred currency for total and chart
            rate = DataHandler.get_exchange_rate(asset_currency, user_currency_code)
            val_in_user_ccy = val_native * rate
            total_mv_user_currency += val_in_user_ccy
            
            table_rows.append({
                'Symbol': ticker,
                'Units': quantity,
                'Price': f"{asset_symbol}{price:,.2f}",
                'Value': f"{asset_symbol}{val_native:,.2f}", 
                # 'Value' col in table shows native currency as requested ("make the composition use the units of the currency itself")
                'action': ticker 
            })
            
            plot_data.append({'Ticker': ticker, 'Value': val_in_user_ccy})

        # render table
        self.__table_container.clear()
        with self.__table_container:
            theme = self.__settings.theme
            
            with ui.row().classes('items-center justify-between mb-2'):
                ui.label('Current Composition').classes('text-lg font-bold') \
                    .style(f'color: {theme.text_primary}')
                # total value header
                ui.label(f"Total: {user_currency_symbol}{total_mv_user_currency:,.2f}").classes('text-xl font-bold') \
                    .style(f'color: {theme.accent}')
            
            # header
            with ui.row().classes('w-full border-b border-gray-600/20 pb-2 mb-2 justify-between'):
                ui.label('Symbol').classes('w-16 font-semibold').style(f'color: {theme.text_primary}')
                ui.label('Units').classes('w-16 font-semibold').style(f'color: {theme.text_primary}')
                ui.label('Value (Local)').classes('w-28 font-semibold text-right').style(f'color: {theme.text_primary}')
                ui.label('').classes('w-8') 
                
            # rows
            with ui.scroll_area().classes('h-64 w-full'):
                for row in table_rows:
                    with ui.row().classes('w-full items-center justify-between py-1 hover:bg-gray-500/10'):
                        ui.label(row['Symbol']).classes('w-16').style(f'color: {theme.text_primary}')
                        ui.label(str(row['Units'])).classes('w-16').style(f'color: {theme.text_primary}')
                        ui.label(row['Value']).classes('w-28 text-right').style(f'color: {theme.text_primary}')
                        
                        ui.button(icon='cancel', on_click=lambda t=row['Symbol']: self.remove_asset(t)) \
                            .props('flat dense size=sm color=red') \
                            .classes('w-8')

        # render chart
        self.__chart_container.clear()
        with self.__chart_container:
            df = pd.DataFrame(plot_data)
            if not df.empty and total_mv_user_currency > 0:
                viz = PortfolioVisualisation(
                    title_input=f"Total: {user_currency_symbol}{total_mv_user_currency:,.2f}",
                    data_input=df,
                    currency_input="USD" # Not critical for Pie, logic is handled
                )
                fig = viz.generate_pie_chart()
                ui.plotly(fig).classes('w-full h-full')
            else:
                 ui.label('No Value to Display').classes('self-center text-gray-400')

    def render(self):
        theme = self.__settings.theme
        
        # Styles
        input_style = (
            f'--custom-input-color: {theme.text_primary}; '
            f'--custom-placeholder-color: {theme.text_placeholder}; '
            f'--custom-accent-soft: {theme.sb_active_bg}; '
            f'--q-primary: {theme.accent};'
        )
        btn_style = f'background-color: {theme.sb_active_bg} !important; color: {theme.sb_active_fg} !important;'

        with ui.element('div').classes('w-full h-full flex flex-col p-8 gap-6'):
            
            # header row
            with ui.row().classes('items-center justify-between w-full'):
                self.__header_label = ui.label(f'Portfolio: {self.__current_portfolio_Name}') \
                    .style(f'color: {theme.accent}; font-size: 200%; font-weight: bold')
                
                # portfolio actions
                with ui.row().classes('gap-2'):
                    ui.button('Save', icon='save', on_click=self.__quick_save) \
                        .style(btn_style).props('flat unelevated')
                    
                    ui.button('Save As', icon='save_as', on_click=self.__open_save_dialog) \
                        .style(btn_style).props('flat unelevated')
                        
                    ui.button('Load', icon='folder_open', on_click=self.__open_load_dialog) \
                        .style(btn_style).props('flat unelevated')
                        
                    ui.button('Export', icon='download', on_click=self.export_csv) \
                        .style(btn_style).props('flat unelevated')

            # layout single row containing 3 equal(ish) sections
            
            with ui.row().classes('w-full h-[600px] gap-6 flex-nowrap'):
                
                # visualization (Larger)
                self.__chart_container = ui.card().classes('w-1/2 h-full p-4 shadow-sm border border-gray-100/10') \
                    .style(f'background-color: {theme.surface}')
                
                # controls
                with ui.card().classes('w-1/4 h-full p-6 gap-4 shadow-sm border border-gray-100/10 flex flex-col').style(f'background-color: {theme.surface}'):
                    ui.label('Add Asset').classes('text-lg font-bold mb-4').style(f'color: {theme.text_primary}')
                    
                    self.__ticker_input = ui.input(label='stock ticker symbol') \
                        .classes('w-full input-field').props('outlined dense uppercase').style(input_style)
                        
                    self.__shares_input = ui.input(label='shares owned') \
                        .classes('w-full input-field').props('outlined dense type=number').style(input_style)
                    
                    ui.button('Add to portfolio', on_click=self.add_asset) \
                        .style(btn_style).classes('w-full font-bold mt-2').props('flat unelevated')

                # composition table
                self.__table_container = ui.card().classes('w-1/4 h-full p-6 shadow-sm border border-gray-100/10 flex flex-col') \
                    .style(f'background-color: {theme.surface}')

        # initial view
        self.refresh_view()
        
        # start polling (every 10 seconds)
        if self.__polling_timer:
            self.__polling_timer.cancel()
        self.__polling_timer = ui.timer(15.0, self.refresh_view)
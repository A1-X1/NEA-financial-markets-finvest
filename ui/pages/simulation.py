from nicegui import ui, run
import pandas as pd
import asyncio
from modules.globalSettings import globalSettings
from modules.simulationEngine import SimulationEngine
from ui.pages.components.visualisation import GBMVisualisation

# global CSS for Simulation Page (consistent with Portfolio styles)
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
''', shared=True)

# Helper function for CPU-bound simulation work (must be pickleable)
def compute_simulation(engine: SimulationEngine):
    # run gbm
    paths = engine.run_simulation()
    
    # prepare data for visualisation (blocking CPU work)
    df = pd.DataFrame(paths.T) 
    df['Mean'] = df.mean(axis=1) 
    
    return df

class SimulationPage:
    def __init__(self):
        self.__settings = globalSettings
        self.__engine = SimulationEngine()
        
        # UI state
        self.__ticker_input = None
        self.__title_input = None
        self.__timeframe_select = None
        self.__rfr_input = None
        self.__sims_input = None
        self.__steps_input = None
        self.__chart_container = None
        self.__simulate_btn = None
        self.__loading_spinner = None

    async def __run_simulation(self):
        # asynchronous method to handle heavy calculations without blocking UI
        try:
            # validate and sync inputs to engine
            self.__engine.ticker = self.__ticker_input.value
            self.__engine.risk_free_rate = float(self.__rfr_input.value or 0.02)
            self.__engine.num_simulations = int(self.__sims_input.value or 100)
            self.__engine.num_steps = int(self.__steps_input.value or 252)
            
            # Show loading state
            self.__simulate_btn.disable()
            self.__loading_spinner.set_visibility(True)
            self.__chart_container.clear()
            with self.__chart_container:
                ui.label('Processing simulation paths...').classes('text-gray-400 italic animate-pulse')
            
            ui.notify(f"Fetching market data for {self.__engine.ticker}...", color='info')
            
            # I/O bound work: fetch parameters (run in thread to keep loop free)
            # We don't use cpu_bound here because network I/O doesn't block CPU
            await run.io_bound(self.__engine.fetch_parameters_from_market, 
                               self.__engine.ticker, 
                               period=self.__timeframe_select.value)
            
            # CPU bound work: generate paths and process data
            # run.cpu_bound offloads to a separate process to avoid heartbeat timeouts
            df = await run.cpu_bound(compute_simulation, self.__engine)
            
            # update chart container (UI work must be in main thread, which we are now back in)
            self.__chart_container.clear()
            with self.__chart_container:
                title = self.__title_input.value or f"{self.__engine.ticker} - forecast"
                viz = GBMVisualisation(
                    title_input=title,
                    data_input=df,
                    currency_input="USD"
                )
                fig = viz.generate_chart()
                ui.plotly(fig).classes('w-full h-[500px]')
                
            ui.notify("Simulation complete", color='positive')
            
        except ValueError as e:
            ui.notify(str(e), color='negative')
        except Exception as e:
            ui.notify(f"Unexpected error: {e}", color='negative')
            print(f"Simulation Error Detail: {e}")
        finally:
            self.__simulate_btn.enable()
            self.__loading_spinner.set_visibility(False)

    def render(self):
        theme = self.__settings.theme
        
        # matching styles from Portfolio and reference image
        input_style = (
            f'--custom-input-color: {theme.text_primary}; '
            f'--custom-placeholder-color: {theme.text_placeholder}; '
            f'--q-primary: {theme.accent};'
        )
        btn_style = f'background-color: {theme.sb_active_bg} !important; color: {theme.sb_active_fg} !important;'

        with ui.element('div').classes('w-full h-full flex flex-col p-8 gap-6'):
            
            # header
            with ui.row().classes('items-center gap-4'):
                ui.label('Simulation') \
                    .style(f'color: {theme.accent}; font-size: 200%; font-weight: bold')
                self.__loading_spinner = ui.spinner(size='lg', color=theme.accent).classes('hidden')
            
            # main content row
            with ui.row().classes('w-full flex-nowrap gap-8'):
                
                # left side: chart and actions
                with ui.column().classes('flex-grow gap-6'):
                    self.__chart_container = ui.card().classes('w-full h-[600px] flex items-center justify-center') \
                        .style(f'background-color: {theme.surface}; border: 1px solid {theme.text_secondary}22')
                    
                    with self.__chart_container:
                        ui.label('No simulation data. Enter parameters and click Simulate.').classes('text-gray-400 italic')
                    
                    ui.button('Add to home', icon='home') \
                        .style(btn_style).props('flat unelevated').classes('w-48 font-bold')

                # right side: control panel card
                with ui.card().classes('w-[350px] p-6 gap-4 shadow-md flex flex-col').style(f'background-color: {theme.surface}; border: 1px solid {theme.text_secondary}22'):
                    
                    self.__ticker_input = ui.input(label='stock ticker symbol') \
                        .classes('w-full input-field').props('outlined dense uppercase').style(input_style)
                    
                    self.__title_input = ui.input(label='title (optional)') \
                        .classes('w-full input-field').props('outlined dense').style(input_style)
                    
                    self.__timeframe_select = ui.select(
                        label='Select Timeframe',
                        options={'1y': '1 Year', '2y': '2 Years', '5y': '5 Years'},
                        value='1y'
                    ).classes('w-full input-field').props('outlined dense').style(input_style)
                    
                    self.__rfr_input = ui.input(label='Risk free rate', value="0.02") \
                        .classes('w-full input-field').props('outlined dense type=number').style(input_style)
                    
                    self.__sims_input = ui.input(label='number of simulations', value="500") \
                        .classes('w-full input-field').props('outlined dense type=number').style(input_style)
                    
                    self.__steps_input = ui.input(label='number of steps', value="252") \
                        .classes('w-full input-field').props('outlined dense type=number').style(input_style)
                    
                    ui.element('div').classes('flex-grow') # spacer
                    
                    self.__simulate_btn = ui.button('Simulate', on_click=self.__run_simulation) \
                        .style(btn_style).classes('w-full h-14 font-bold text-lg').props('flat unelevated')
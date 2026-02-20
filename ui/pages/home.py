from nicegui import ui
from modules.globalSettings import GlobalSettings, globalSettings
from ui.pages.components.homeWidget import HomeWidget, MarketChartWidget, PortfolioChartWidget, SimulationChartWidget
from ui.pages.components.newHomeWidget import NewHomeWidget
from ui.pages.components.widgetLinkedList import WidgetLinkedList, WidgetNode
from ui.pages.components import homeWidgetManager
from ui.pages.components.stack import Stack
import plotly.graph_objects as go

class HomePage:
    def __init__(self):
        self.__settings = globalSettings
        self.__widgets = WidgetLinkedList()
        self.__grid_container = None
        
        # initialise undo/redo stacks (limit to 5 actions)
        self.__undo_stack = Stack(max_size=5)
        self.__redo_stack = Stack(max_size=5)
        
        # load state from database
        state = homeWidgetManager.load_widget_list()
        self.__widgets.from_list(state)
        
        # load undo/redo stacks from database
        undo_list, redo_list = homeWidgetManager.load_undo_redo_stacks()
        self.__undo_stack.from_list(undo_list)
        self.__redo_stack.from_list(redo_list)

    def __handle_widget_action(self, widget_id: str, action: str):
        # handles move and delete actions from widgets
        
        # save current state to undo stack before any modification
        current_state = self.__widgets.to_list()
        
        if action == 'move_up':
            if self.__widgets.move_up(widget_id):
                self.__undo_stack.push(current_state)
                self.__redo_stack = Stack(max_size=5) # clear redo on new action
                self.__save_and_refresh()
        elif action == 'move_down':
            if self.__widgets.move_down(widget_id):
                self.__undo_stack.push(current_state)
                self.__redo_stack = Stack(max_size=5)
                self.__save_and_refresh()
        elif action == 'delete':
            if self.__widgets.remove(widget_id):
                self.__undo_stack.push(current_state)
                self.__redo_stack = Stack(max_size=5)
                self.__save_and_refresh()

    def __undo(self):
        # restores previous state from undo stack
        if self.__undo_stack.is_empty():
            return
            
        # push current state to redo
        self.__redo_stack.push(self.__widgets.to_list())
        
        # pop and apply previous state
        prev_state = self.__undo_stack.pop()
        self.__widgets.from_list(prev_state)
        self.__save_and_refresh()

    def __redo(self):
        # restores state from redo stack
        if self.__redo_stack.is_empty():
            return
            
        # push current state to undo
        self.__undo_stack.push(self.__widgets.to_list())
        
        # pop and apply redo state
        next_state = self.__redo_stack.pop()
        self.__widgets.from_list(next_state)
        self.__save_and_refresh()

    def __save_and_refresh(self):
        # saves current linked list state and stacks to DB and refreshes UI
        homeWidgetManager.save_widget_list(self.__widgets.to_list())
        homeWidgetManager.save_undo_redo_stacks(
            self.__undo_stack.to_list(), 
            self.__redo_stack.to_list()
        )
        self.__render_grid()
        
        # refresh the header to update button states (enabled/disabled)
        self.__render_header()

    def __render_grid(self):
        # clears and rebuilds the widget grid
        if not self.__grid_container:
            return
            
        self.__grid_container.clear()
        
        with self.__grid_container:
            cur = self.__widgets.head
            while cur:
                node = cur
                self.__render_widget_node(node)
                cur = cur.next
            
            # placeholder "Add Widget" button at the end
            NewHomeWidget()

    def __render_widget_node(self, node: WidgetNode):
        # renders an individual widget based on its type
        colours = self.__settings.theme
        
        if node.widget_type == 'MarketChart':
            w = MarketChartWidget(
                title=node.config.get('title', 'Market Chart'), 
                ticker=node.config.get('ticker', 'AAPL'),
                chart_mode=node.config.get('chart_mode', 'Line'),
                timeframe=node.config.get('timeframe', '1mo')
            )
        elif node.widget_type == 'Simulation':
            w = SimulationChartWidget(
                title=node.config.get('title', 'Simulation Forecast'),
                ticker=node.config.get('ticker', 'AAPL'),
                timeframe=node.config.get('timeframe', '1y'),
                rfr=node.config.get('rfr', 0.02),
                sims=node.config.get('sims', 500),
                steps=node.config.get('steps', 252)
            )
        elif node.widget_type == 'PortfolioValue':
            w = PortfolioChartWidget(
                portfolio_name=node.config.get('name', 'New Portfolio')
            )
        elif node.widget_type == 'RiskMetric':
            w = HomeWidget("Risk Metric")
            with w.content:
                # render a simple plot
                fig = go.Figure(go.Scatter(x=[1, 2, 3, 4], y=[1, 2, 3, 2.5], mode='lines+markers', line=dict(color=colours.accent, width=3)))
                fig.update_layout(margin=dict(l=20, r=20, t=10, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                 xaxis=dict(showgrid=False, showticklabels=False), yaxis=dict(showgrid=True, gridcolor=colours.sb_inactive_fg, showticklabels=True),
                                 font=dict(color=colours.text_secondary))
                ui.plotly(fig).classes('w-full h-full')
        elif node.widget_type == 'News':
            w = HomeWidget("Recent News")
            with w.content:
                ui.label(node.config.get('text', "No news available.")).classes('text-sm italic').style(f'color: {colours.text_secondary}')
        else:
            w = HomeWidget(f"Widget: {node.widget_type}")
            with w.content:
                ui.label("Unknown widget type")

        # attach action handler
        w.on_action = lambda action, id=node.widget_id: self.__handle_widget_action(id, action)

    def __render_header(self):
        # renders the dashboard header with undo/redo buttons
        if not self.__header_container:
            return
            
        self.__header_container.clear()
        colours = self.__settings.theme
        
        with self.__header_container:
            ui.label('Dashboard').style(f'color: {colours.text_primary}; font-size: 200%; font-weight: bold')
            
            with ui.row().classes('items-center gap-4'):
                # undo/redo buttons
                with ui.row().classes('gap-1'):
                    undo_btn = ui.button(icon='undo', on_click=self.__undo).props('flat dense unelevated') \
                        .style(f'color: {colours.text_primary}')
                    if self.__undo_stack.is_empty():
                        undo_btn.disable()
                        
                    redo_btn = ui.button(icon='redo', on_click=self.__redo).props('flat dense unelevated') \
                        .style(f'color: {colours.text_primary}')
                    if self.__redo_stack.is_empty():
                        redo_btn.disable()
                
                with ui.element('div').classes('px-4 py-2 rounded-full shadow-sm flex items-center gap-2').style(f'background-color: {colours.surface}'):
                    ui.icon('monetization_on').style(f'color: {colours.accent}')
                    ui.label(f'{self.__settings.currencySymbol}{self.__settings.currency.code}').style(f'color: {colours.text_primary}; font_weight: 600')

    def render(self):
        colours = self.__settings.theme
        
        with ui.element('div').classes('w-full flex flex-col items-center mt-8 pb-10'):
            with ui.element('div').classes('w-[90%] max-w-7xl flex flex-col gap-8'):
                
                # header row container
                self.__header_container = ui.row().classes('w-full justify-between items-center')
                self.__render_header()

                # grid for widgets
                self.__grid_container = ui.element('div').classes('w-full grid grid-cols-1 lg:grid-cols-2 gap-6')
                self.__render_grid()

        # auto-save every 30 seconds as requested
        ui.timer(30.0, lambda: (
            homeWidgetManager.save_widget_list(self.__widgets.to_list()),
            homeWidgetManager.save_undo_redo_stacks(self.__undo_stack.to_list(), self.__redo_stack.to_list())
        ))
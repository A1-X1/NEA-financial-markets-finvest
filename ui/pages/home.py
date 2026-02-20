from nicegui import ui
from modules.globalSettings import GlobalSettings, globalSettings
from ui.pages.components.homeWidget import HomeWidget, MarketChartWidget, PortfolioChartWidget, SimulationChartWidget
from ui.pages.components.newHomeWidget import NewHomeWidget
from ui.pages.components.widgetLinkedList import WidgetLinkedList, WidgetNode
from ui.pages.components import homeWidgetManager
import plotly.graph_objects as go

class HomePage:
    def __init__(self):
        self.__settings = globalSettings
        self.__widgets = WidgetLinkedList()
        self.__grid_container = None
        
        # load state from database
        state = homeWidgetManager.load_widget_list()
        self.__widgets.from_list(state)

    def __handle_widget_action(self, widget_id: str, action: str):
        # handles move and delete actions from widgets
        if action == 'move_up':
            if self.__widgets.move_up(widget_id):
                self.__save_and_refresh()
        elif action == 'move_down':
            if self.__widgets.move_down(widget_id):
                self.__save_and_refresh()
        elif action == 'delete':
            if self.__widgets.remove(widget_id):
                self.__save_and_refresh()

    def __save_and_refresh(self):
        # saves current linked list state to DB and refreshes UI
        homeWidgetManager.save_widget_list(self.__widgets.to_list())
        self.__render_grid()

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

    def render(self):
        colours = self.__settings.theme
        
        with ui.element('div').classes('w-full flex flex-col items-center mt-8 pb-10'):
            with ui.element('div').classes('w-[90%] max-w-7xl flex flex-col gap-8'):
                
                # header row
                with ui.row().classes('w-full justify-between items-center'):
                    ui.label('Dashboard').style(f'color: {colours.text_primary}; font-size: 200%; font-weight: bold')
                    
                    with ui.element('div').classes('px-4 py-2 rounded-full shadow-sm flex items-center gap-2').style(f'background-color: {colours.surface}'):
                        ui.icon('monetization_on').style(f'color: {colours.accent}')
                        ui.label(f'{self.__settings.currencySymbol}{self.__settings.currency.code}').style(f'color: {colours.text_primary}; font_weight: 600')

                # grid for widgets
                self.__grid_container = ui.element('div').classes('w-full grid grid-cols-1 lg:grid-cols-2 gap-6')
                self.__render_grid()

        # auto-save every 30 seconds as requested
        ui.timer(30.0, lambda: homeWidgetManager.save_widget_list(self.__widgets.to_list()))
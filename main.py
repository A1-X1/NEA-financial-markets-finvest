from nicegui import ui
from modules.globalSettings import globalSettings
from ui.pages.dashboard import DashboardLayout
from ui.pages.home import HomePage
from ui.pages.charts import ChartsPage
from ui.pages.simulation import SimulationPage
from ui.pages.news import NewsPage
from ui.pages.portfolio import PortfolioPage
from ui.pages.settings import SettingsPage


from nicegui.javascript_request import JavaScriptRequest

# monkeypatch to increase the default javascript timeout from 1.0s to 60.0s
# this prevents the app from resetting when rendering 10,000+ simulation paths
original_init = JavaScriptRequest.__init__
def patched_init(self, request_id: str, *, timeout: float = 60.0):
    original_init(self, request_id, timeout=timeout)
JavaScriptRequest.__init__ = patched_init


# instantiate the app class
class MainApp:
    def __init__(self):
        self.globalSettings = globalSettings
        self.layout_renderer = DashboardLayout()
        self.setup_routes()

    def setup_routes(self):
        # routing for page (/ is home page)
        @ui.page('/')
        def index():
            self.layout_renderer.render(active_route='home')
            
            with ui.column().classes('w-full p-4'):
                page = HomePage()
                page.render()

        # routing for settingspage
        @ui.page('/settings')
        def settings():
            self.layout_renderer.render(active_route='settings')
            
            with ui.column().classes('w-full p-4'):
                page = SettingsPage()
                page.render()

        # routing for charts page
        @ui.page('/charts')
        def charts():
            self.layout_renderer.render(active_route='charts')
            
            with ui.column().classes('w-full p-4'):
                page = ChartsPage()
                page.render()

        # routing for portfolio page
        @ui.page('/portfolio')
        def portfolio():
            self.layout_renderer.render(active_route='portfolio')
            
            with ui.column().classes('w-full p-4'):
                page = PortfolioPage()
                page.render()

        # routing for simulation page
        @ui.page('/simulation')
        def simulation():
            self.layout_renderer.render(active_route='simulation')
            
            with ui.column().classes('w-full p-4'):
                page = SimulationPage()
                page.render()

        # routing for news page
        @ui.page('/news')
        def news():
            self.layout_renderer.render(active_route='news')
            
            with ui.column().classes('w-full p-4'):
                page = NewsPage()
                page.render()

    def start(self):
        # ensures all prerequisites are ready before loading the app
        print("Checking prerequisites...")
        if not self.globalSettings:
            print("Error: Global settings not loaded.")
            return False
            
        print("Prerequisites check passed.")
        return True

    def runApplication(self):
        # launches the ui
        ui.run(title="Finvest Risk Manager", port=8080, native=True)


if __name__ in {"__main__", "__mp_main__"}:
    app = MainApp()
    if app.start():
        app.runApplication()
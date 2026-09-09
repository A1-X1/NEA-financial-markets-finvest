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

            # show disclaimer notice on first launch
            ui.notify(
                'Disclaimer: The developer of Finvest is not liable for financial misconduct by users. '
                'Professional financial experience is recommended.',
                type='warning',
                position='bottom',
                duration=5.0
            )
            
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
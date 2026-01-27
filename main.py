from nicegui import ui
from modules.globalSettings import globalSettings
from ui.pages.dashboard import DashboardLayout
from ui.pages.home import HomePage
from ui.pages.charts import ChartsPage
from ui.pages.simulation import SimulationPage
from ui.pages.news import NewsPage
from ui.pages.portfolio import PortfolioPage
from ui.pages.settings import SettingsPage

# Instantiate the layout renderer
layout_renderer = DashboardLayout()

@ui.page('/')
def index():
    layout_renderer.render(active_route='home')
    
    with ui.column().classes('w-full p-4'):
        page = HomePage()
        page.render()

@ui.page('/settings')
def settings():
    layout_renderer.render(active_route='settings')
    
    with ui.column().classes('w-full p-4'):
        page = SettingsPage()
        page.render()

@ui.page('/charts')
def charts():
    layout_renderer.render(active_route='charts')
    
    with ui.column().classes('w-full p-4'):
        page = ChartsPage()
        page.render()

@ui.page('/portfolio')
def portfolio():
    layout_renderer.render(active_route='portfolio')
    
    with ui.column().classes('w-full p-4'):
        page = PortfolioPage()
        page.render()

@ui.page('/simulation')
def simulation():
    layout_renderer.render(active_route='simulation')
    
    with ui.column().classes('w-full p-4'):
        page = SimulationPage()
        page.render()

@ui.page('/news')
def news():
    layout_renderer.render(active_route='news')
    
    with ui.column().classes('w-full p-4'):
        page = NewsPage()
        page.render()


# Runs the main app
ui.run(title="Finvest Risk Manager", port=8080, native=False)
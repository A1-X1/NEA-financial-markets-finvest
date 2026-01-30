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

# routing for page (default page is home)
@ui.page('/')
def index():
    layout_renderer.render(active_route='home')
    
    with ui.column().classes('w-full p-4'):
        page = HomePage()
        page.render()

# routing for settings page
@ui.page('/settings')
def settings():
    layout_renderer.render(active_route='settings')
    
    with ui.column().classes('w-full p-4'):
        page = SettingsPage()
        page.render()

# routing for charts page
@ui.page('/charts')
def charts():
    layout_renderer.render(active_route='charts')
    
    with ui.column().classes('w-full p-4'):
        page = ChartsPage()
        page.render()

# routing for portfolio page
@ui.page('/portfolio')
def portfolio():
    layout_renderer.render(active_route='portfolio')
    
    with ui.column().classes('w-full p-4'):
        page = PortfolioPage()
        page.render()

# routing for simulation page
@ui.page('/simulation')
def simulation():
    layout_renderer.render(active_route='simulation')
    
    with ui.column().classes('w-full p-4'):
        page = SimulationPage()
        page.render()

# routing for news page
@ui.page('/news')
def news():
    layout_renderer.render(active_route='news')
    
    with ui.column().classes('w-full p-4'):
        page = NewsPage()
        page.render()


# Runs the main app (native param just tells the app to run in a native process rather than in browser)
ui.run(title="Finvest Risk Manager", port=8080, native=True)
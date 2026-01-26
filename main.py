from nicegui import ui
from modules.globalSettings import GlobalSettings
from ui.pages.dashboard import DashboardLayout

from nicegui import ui

settings = GlobalSettings()
layout = DashboardLayout(settings)

@ui.page('/')
def index():
    layout.build_ui()
    layout.load_home_page() # Default view

ui.run(title="Finvest Risk Manager", port=8080, native=False)
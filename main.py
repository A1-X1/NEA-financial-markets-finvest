from nicegui import ui
from modules.settings import GlobalSettings
from ui.pages.dashboard import DashboardLayout

settings = GlobalSettings()
layout = DashboardLayout(settings)

@ui.page('/')
def index():
    layout.build_ui()
    layout.load_home_page() # Default view

ui.run(title="Finvest Risk Manager", port=8080)
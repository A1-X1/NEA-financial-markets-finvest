from nicegui import ui
from modules.globalSettings import globalSettings
from ui.pages.dashboard import DashboardLayout
from ui.pages.home import HomePage
from ui.pages.settings import SettingsPage

# Instantiate the layout renderer
layout_renderer = DashboardLayout()

@ui.page('/')
def index():
    # 1. Render the Shell (Sidebar), marking 'home' as active
    layout_renderer.render(active_route='home')
    
    # 2. Render the specific Page Content
    # We create a container for the page content to apply padding/structuring
    with ui.column().classes('w-full p-4'):
        page = HomePage()
        page.render()

@ui.page('/settings')
def settings():
    # 1. Render the Shell, marking 'settings' as active
    layout_renderer.render(active_route='settings')
    
    # 2. Render Page Content
    with ui.column().classes('w-full p-4'):
        page = SettingsPage()
        page.render()

# Add other routes similarly

ui.run(title="Finvest Risk Manager", port=8080, native=False)
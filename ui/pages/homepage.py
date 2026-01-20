from nicegui import ui
from modules.settings import GlobalSettings

class HomePage:
    def __init__(self, settings: GlobalSettings):
        self.__settings = settings

    def render(self):
        ui.label('Welcome to your Financial Dashboard').style('color: #F8F8FA; font-size: 200%')
        with ui.card().style('background-color: #7C8D88'):
            ui.label(f'Active Currency: {self.__settings.currency}')
            ui.label(f'Risk Threshold: {self.__settings.risk_threshold * 100}%')
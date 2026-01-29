from dataclasses import dataclass, field
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from modules.globalSettings import globalSettings

@dataclass
class Visualisation:
    # 1. Public Inputs
    title_input: str
    data_input: pd.DataFrame
    currency_input: str  # New input field
    
    # 2. Private Storage
    __chart_title: str = field(init=False, repr=False)
    __data: pd.DataFrame = field(init=False, repr=False)
    __currency: str = field(init=False, repr=False)

    def __post_init__(self):
        self.chart_title = self.title_input
        self.data = self.data_input
        self.__currency = self.currency_input

    @property
    def chart_title(self) -> str:
        return self.__chart_title
    
    @chart_title.setter
    def chart_title(self, value: str):
        if not value or len(value) < 3:
            raise ValueError("Visualisation: Title is too short.")
        self.__chart_title = value

    @property
    def data(self) -> pd.DataFrame:
        return self.__data

    @data.setter
    def data(self, value: pd.DataFrame):
        if value is None or (isinstance(value, pd.DataFrame) and value.empty):
            raise ValueError("Visualisation: Data source cannot be empty.")
        self.__data = value

    @property
    def currency(self) -> str:
        return self.__currency

    def _apply_theme_layout(self, fig: go.Figure):
        theme = globalSettings.theme
        fig.update_layout(
            paper_bgcolor=theme.background,
            plot_bgcolor=theme.surface,
            font=dict(color=theme.text_primary),
            title_font=dict(color=theme.accent),
            # Add grid colors
            xaxis=dict(gridcolor=theme.text_placeholder, zerolinecolor=theme.accent),
            yaxis=dict(gridcolor=theme.text_placeholder, zerolinecolor=theme.accent),
            margin=dict(l=20, r=40, t=40, b=20)
        )
        return fig

@dataclass
class RiskTrendVisualisation(Visualisation):
    def generate_chart(self) -> go.Figure:
        theme = globalSettings.theme
        
        # Label the Y-Axis with the currency
        y_label = f'Price ({self.currency})'
        
        fig = px.line(
            self.data, 
            x='Date', 
            y='Close', 
            title=f"{self.chart_title} ({self.currency})", # Add currency to title
            labels={'Close': y_label} # Add currency to hover tooltip/axis
        )
        
        fig.update_traces(line_color=theme.accent, line_width=2)
        return self._apply_theme_layout(fig)
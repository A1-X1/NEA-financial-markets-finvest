from dataclasses import dataclass, field
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from modules.globalSettings import globalSettings

@dataclass
class Visualisation:
    # 1. Define public-facing arguments for the constructor
    title_input: str
    data_input: pd.DataFrame
    
    # 2. Define private storage fields that the dataclass won't try to 'init' automatically
    __chart_title: str = field(init=False, repr=False)
    __data: pd.DataFrame = field(init=False, repr=False)

    def __post_init__(self):
        # 3. This triggers the @setters below, ensuring validation happens on start
        self.chart_title = self.title_input
        self.data = self.data_input

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

    def _apply_theme_layout(self, fig: go.Figure):
        theme = globalSettings.theme
        fig.update_layout(
            paper_bgcolor=theme.background,
            plot_bgcolor=theme.surface,
            font=dict(color=theme.text_primary),
            title_font=dict(color=theme.accent),
            xaxis=dict(gridcolor=theme.text_placeholder, zerolinecolor=theme.accent),
            yaxis=dict(gridcolor=theme.text_placeholder, zerolinecolor=theme.accent),
            margin=dict(l=20, r=40, t=40, b=20)
        )
        return fig

@dataclass
class RiskTrendVisualisation(Visualisation):
    def generate_chart(self) -> go.Figure:
        theme = globalSettings.theme
        # Use self.data (the property) rather than __data (the mangled private field)
        fig = px.line(self.data, x='Date', y='Close', title=self.chart_title)
        fig.update_traces(line_color=theme.accent, line_width=2)
        return self._apply_theme_layout(fig)
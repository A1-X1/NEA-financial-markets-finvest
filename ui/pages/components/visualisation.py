import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dataclasses import dataclass
from modules.globalSettings import globalSettings

@dataclass
class Visualisation:
    # Use constructor arguments that map to private storage in __post_init__ 
    # for cleaner OCR-level encapsulation
    def __init__(self, title: str, data: pd.DataFrame):
        self.chart_title = title
        self.data = data

    @property
    def chart_title(self) -> str:
        return self.__chart_title
    
    @chart_title.setter
    def chart_title(self, value: str):
        if not value or len(value) < 3:
            raise ValueError("Visualisation: Title must be descriptive.")
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
        """Applies the current global theme to the Plotly figure."""
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
    """
    Inherits from Visualisation. 
    Focuses on Trend analysis (Prototype 2 requirements).
    """
    def generate_chart(self) -> go.Figure:
        theme = globalSettings.theme
        
        # Accessing data through the public property defined in the parent
        fig = px.line(
            self.data, 
            x='Date', 
            y='Close', 
            title=self.chart_title
        )
        
        fig.update_traces(line_color=theme.accent, line_width=2)
        return self._apply_theme_layout(fig)
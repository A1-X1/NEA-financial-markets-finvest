from dataclasses import dataclass, field
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from modules.globalSettings import globalSettings

@dataclass
class Visualisation:
    # defining public attributes
    title_input: str
    data_input: pd.DataFrame
    currency_input: str
    
    # defining private attributes
    __chart_title: str = field(init=False, repr=False)
    __data: pd.DataFrame = field(init=False, repr=False)
    __currency: str = field(init=False, repr=False)

    # constructor/initialiser
    def __post_init__(self):
        # Using setters to ensure validation logic is triggered
        self.chart_title = self.title_input
        self.data = self.data_input
        self.currency = self.currency_input

    def _apply_theme_layout(self, fig: go.Figure):
        theme = globalSettings.theme
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=theme.text_primary),
            title_font=dict(color=theme.accent),
            xaxis=dict(
                gridcolor='rgba(128,128,128,0.2)', 
                zerolinecolor=theme.accent,
                tickfont=dict(color=theme.text_secondary)
            ),
            yaxis=dict(
                gridcolor='rgba(128,128,128,0.2)', 
                zerolinecolor=theme.accent,
                tickfont=dict(color=theme.text_secondary)
            ),
            margin=dict(l=40, r=40, t=60, b=40)
        )
        return fig

    # getters and setters
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

    @currency.setter
    def currency(self, value: str):
        if not value:
            self.__currency = "USD"
        else:
            self.__currency = value


@dataclass
class RiskTrendVisualisation(Visualisation):
    def generate_chart(self, chart_mode: str = 'Line') -> go.Figure:
        theme = globalSettings.theme
        fig = go.Figure()

        # add candlestick trace if mode is candlestick
        if chart_mode == 'Candlestick':
            fig.add_trace(go.Candlestick(
                x=self.data['Date'],
                open=self.data['Open'],
                high=self.data['High'],
                low=self.data['Low'],
                close=self.data['Close'],
                name='Market Data'
                # default colors are green (increasing) and red (decreasing)
            ))
        
        # add line trace if mode is line
        else:
            fig.add_trace(go.Scatter(
                x=self.data['Date'], 
                y=self.data['Close'],
                mode='lines',
                line=dict(color=theme.accent, width=2),
                name='Price'
            ))

        # update layout
        fig.update_layout(title=self.chart_title)
        return self._apply_theme_layout(fig)
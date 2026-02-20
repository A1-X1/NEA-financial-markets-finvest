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

@dataclass
class PortfolioVisualisation(Visualisation):
    # specialised method to generate pie chart, data_input is expected to be a dataframe with columns ['Ticker', 'Value']
    def generate_pie_chart(self) -> go.Figure:
        theme = globalSettings.theme
        
        fig = px.pie(
            self.data, 
            values='Value', 
            names='Ticker', 
            title=self.chart_title,

            # customises what the visualisation looks like
            hole=0.4
        )
        
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            marker=dict(line=dict(color=theme.background, width=2))
        )
        
        # apply standard layout but with some differences for pie chart
        fig = self._apply_theme_layout(fig)
        fig.update_layout(
            showlegend=False,
            font=dict(size=14)
        )
        
        return fig

@dataclass
class GBMVisualisation(Visualisation):
    # specialised method to generate gbm path chart
    # data_input is a dataframe where each row is a time step
    def generate_chart(self) -> go.Figure:
        theme = globalSettings.theme
        fig = go.Figure()
        
        # ensure 'Date' or index is used for X axis
        x_axis = self.data.index
        
        # filter for simulation columns (avoiding 'Date' or 'Mean' if they exist)
        sim_cols = [c for c in self.data.columns if c not in ['Date', 'Mean', 'Max', 'Min']]
        
        # calculate the daily highest and lowest values across all simulation paths
        daily_max = self.data[sim_cols].max(axis=1)
        daily_min = self.data[sim_cols].min(axis=1)

        # limit drawn paths to 3000 to avoid ui timeouts but keep the data for calculations
        drawn_sim_cols = sim_cols[:3000]
        
        # add simulation paths (background lines)
        for col in drawn_sim_cols:
            fig.add_trace(go.Scatter(
                x=x_axis,
                y=self.data[col],
                mode='lines',
                line=dict(width=1),
                opacity=0.15, 
                name=f'Path {col}',
                showlegend=False,
                hoverinfo='skip'
            ))

        # add daily high trace (for tooltip and clear bound)
        fig.add_trace(go.Scatter(
            x=x_axis,
            y=daily_max,
            mode='lines',
            line=dict(width=1, dash='dot', color=theme.accent),
            opacity=0.5,
            name='Daily High',
            hovertemplate='<b>Daily High</b><br>Day %{x}<br>Price: %{y:.2f}<extra></extra>'
        ))

        # add daily low trace (for tooltip and clear bound)
        fig.add_trace(go.Scatter(
            x=x_axis,
            y=daily_min,
            mode='lines',
            line=dict(width=1, dash='dot', color=theme.accent),
            opacity=0.5,
            name='Daily Low',
            hovertemplate='<b>Daily Low</b><br>Day %{x}<br>Price: %{y:.2f}<extra></extra>'
        ))
            
        # add mean path if it exists
        if 'Mean' in self.data.columns:
            fig.add_trace(go.Scatter(
                x=x_axis,
                y=self.data['Mean'],
                mode='lines',
                line=dict(color=theme.accent, width=4),
                name='Mean Path',
                hovertemplate='<b>Mean Path</b><br>Day %{x}<br>Price: %{y:.2f}<extra></extra>'
            ))
            
        fig.update_layout(
            title=self.chart_title,
            xaxis_title='Trading Days (Forecast)',
            yaxis_title=f'Price ({self.currency})',
            hovermode='x unified'
        )
        
        return self._apply_theme_layout(fig)
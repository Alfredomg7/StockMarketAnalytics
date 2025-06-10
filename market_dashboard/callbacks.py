from typing import List, Tuple
from dash import Dash, Input, Output, ctx
import plotly.graph_objects as go
import components as cmp
import services.db as db
from config import CREDENTIALS_DICT, PROJECT_ID
from utils.callback_utils import get_period, get_volume_range
from utils.google_cloud_utils import get_bigquery_client

def register_callbacks(app: Dash) -> None:    
    @app.callback(
        Output({'type': 'time-period-store', 'section': 'market'}, 'data'),
        [
            Input({'type': 'btn-one-month', 'section': 'market'}, 'n_clicks'),
            Input({'type': 'btn-three-months', 'section': 'market'}, 'n_clicks'),
            Input({'type': 'btn-six-months', 'section': 'market'}, 'n_clicks'),
            Input({'type': 'btn-one-year', 'section': 'market'}, 'n_clicks'),
            Input({'type': 'btn-five-years', 'section': 'market'}, 'n_clicks'),
            Input({'type': 'btn-max', 'section': 'market'}, 'n_clicks'),
        ],
        prevent_initial_call=True
    )
    def update_time_period_store(*args) -> str:
        triggered_id = ctx.triggered_id
        period = get_period(triggered_id['type'])
        return period
    
    @app.callback(
        [
            Output({'type': 'dynamic-output-line', 'section': 'market'}, 'figure'),
            Output({'type': 'dynamic-output-candlestick', 'section': 'market'}, 'figure'),
            Output({'type': 'dynamic-output-bar', 'section': 'market'}, 'figure'),
        ],
        [
            Input({'type': 'dynamic-select-stock', 'section': 'market'}, 'value'),
            Input({'type': 'time-period-store', 'section': 'market'}, 'data'),
            Input({'type': 'dynamic-select-volume', 'section': 'market'}, 'value'),
        ]
    )
    def update_stock_and_volume_charts(ticker: str, period: str, selected_volume_range: str) -> Tuple[go.Figure, go.Figure, go.Figure]:
        bigquery_client = get_bigquery_client(CREDENTIALS_DICT, PROJECT_ID)
        try:
            price_df = db.get_price_data(bigquery_client, ticker, period)
            volume_range = get_volume_range(selected_volume_range)
            volume_df = db.get_volume_data(bigquery_client, ticker, period, volume_range)
            
            time_period_text = f'Last {period.capitalize()}' if period != 'max' else 'All Time'
            line_chart_title = f'{ticker} Closing Price - {time_period_text}'
            candlestick_chart_title = f'{ticker} Price Movement - {time_period_text}'
            
            if not price_df.is_empty():
                line_fig = cmp.create_line_chart(price_df, x='date', y='close', title=line_chart_title, color=cmp.PRIMARY_COLOR)
                candlestick_fig = cmp.create_candlestick_chart(price_df, title=candlestick_chart_title)
            else:
                line_fig = cmp.create_empty_chart(line_chart_title)
                candlestick_fig = cmp.create_empty_chart(candlestick_chart_title)
            
            volume_chart_title = f"{ticker} Trading Volume - {time_period_text}"
            
            short_term_periods = ['1 month', '3 months', '6 months']
            long_term_periods = ['1 year', '5 years', 'max']
            
            if not volume_df.is_empty():
                if period in short_term_periods:
                    volume_fig = cmp.create_bar_chart(volume_df, x='date', y='volume', title=volume_chart_title, color=cmp.SECONDARY_COLOR)
                elif period in long_term_periods:
                    volume_fig = cmp.create_scatter_chart(volume_df, x='date', y='volume', title=volume_chart_title, color=cmp.SECONDARY_COLOR)
                volume_fig.update_layout(yaxis=dict(title='Transactions'))
            else:
                volume_fig = cmp.create_empty_chart(volume_chart_title)
            
            return line_fig, candlestick_fig, volume_fig
        finally:
            bigquery_client.close()
    
    @app.callback(
        Output({'type': 'dynamic-output-heatmap', 'section': 'market'}, 'figure'),
        [
            Input({'type': 'dynamic-select-corr', 'section': 'market'}, 'value'),
            Input({'type': 'time-period-store', 'section': 'market'}, 'data'),
        ]
    )
    def update_heatmap(tickers: List[str], period: str) -> go.Figure:
        client = get_bigquery_client(CREDENTIALS_DICT, PROJECT_ID)
        try:
            corr_matrix = db.get_corr_matrix(client, tickers, period)
            time_period_text = f'Last {period.capitalize()}' if period != 'max' else 'All Time'
            chart_title = f'Stocks Correlation Matrix - {time_period_text}'
            if not corr_matrix.is_empty():
                fig = cmp.create_correlation_heatmap(corr_matrix=corr_matrix, title=chart_title)
                return fig
            return cmp.create_empty_chart(chart_title)
        finally:
            client.close()
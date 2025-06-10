from io import StringIO
from dash import Dash, Input, Output
import pandas as pd
import polars as pl
from config import CREDENTIALS_DICT, PROJECT_ID
import components as cmp
import services.db as db
from utils.fig_utils import format_currency, format_percent
from utils.google_cloud_utils import get_bigquery_client

def register_callbacks(app: Dash) -> None:
    @app.callback(
        [
            # Outputs for KPIs
            *[Output({'type': 'kpi-value', 'section': kpi}, 'children')
              for kpi in ['Total Value', 'Unique Stocks', 'AVG Price', 'HHI']],
            # Outputs for the charts
            *[
                Output({'type': chart, 'section': 'portfolio'}, 'figure')
                for chart in ['portfolio-distribution-chart', 'sector-distribution-chart']
            ]
        ],
        [
            Input("url", "pathname"),
            Input({'type': 'portfolio-data', 'section': 'global'}, 'data')
        ]
    )
    def update_dashboard(pathname, portfolio_data: str) -> list:
        # Load and prepare portfolio data
        portfolio_df = pd.read_json(StringIO(portfolio_data), orient="records")
        if not portfolio_df.empty:
            portfolio_df = portfolio_df.sort_values(by="Value")

        # Handle empty portfolio
        if portfolio_df.empty:
            kpis_placeholders = ['-', '-', '-', '-']
            empty_charts = [
                cmp.create_empty_chart(
                    title='No Data', 
                    text="Please add stocks to your portfolio in 'My Portfolio' section."
                ) for _ in range(2)
            ]
            return kpis_placeholders + empty_charts
        
        # Calculate and format KPIs
        total_value = format_currency(portfolio_df["Value"].sum())
        unique_stocks = str(len(portfolio_df))
        avg_price = format_currency(portfolio_df["Price"].mean())
        hhi = format_percent(portfolio_df["Weight"].pow(2).sum())

        # Create portfolio distribution chart
        portfolio_distribution_chart = cmp.create_bar_chart(
            data=portfolio_df,
            x="Ticker",
            y="Value",
            title="Portfolio Distribution",
            color=cmp.PRIMARY_COLOR,
            orientation='h',
            show_data_labels=True,
        )
        portfolio_distribution_chart.update_layout(xaxis=dict(title='Value (USD)'))

        # Get sector data and create sector distribution chart
        client = get_bigquery_client(CREDENTIALS_DICT, PROJECT_ID)
        try:
            sector_df = db.get_sector_data(client)
            aggregated_df = db.aggregate_portfolio_by_sector(
                pl.from_pandas(portfolio_df), 
                sector_df
            )
            sector_distribution_chart = cmp.create_bar_chart(
                data=aggregated_df,
                x="sector",
                y="Total Value",
                title="Sector Allocation",
                color=cmp.PRIMARY_COLOR,
                show_data_labels=True,
            )
            sector_distribution_chart.update_layout(yaxis=dict(title='Value (USD)'))
        finally:
            client.close()
        
        # Prepare values to return
        kpis = [total_value, unique_stocks, avg_price, hhi]
        charts = [
            portfolio_distribution_chart,
            sector_distribution_chart
        ]
        return kpis + charts
import sqlite3
from typing import List, Dict
from google.cloud import bigquery
import polars as pl
from config import PROJECT_ID, DATASET_ID, STOCKS_TABLE_ID, SECTORS_TABLE_ID
 
def get_price_data(
    client: bigquery.Client,
    ticker: str,
    period: str = 'max'
) -> pl.DataFrame:
    # Define the SQL query to fetch stock price data
    period_filter = '' if period == 'max' else "AND date > DATE_SUB(CURRENT_DATE(), INTERVAL @period_days DAY)"
    
    query = f"""
        SELECT
            date, open, close, high, low
        FROM
            `{PROJECT_ID}.{DATASET_ID}.{STOCKS_TABLE_ID}`
        WHERE
            ticker = @ticker
        {period_filter}
        ORDER BY
            date ASC
    """
    # prepare the query parameters based on the period
    try:
        if period == 'max':
            query_params = [
                bigquery.ScalarQueryParameter("ticker", "STRING", ticker)
            ]
        else:
            period_days = {
                '1 month': 30,
                '3 months': 90,
                '6 months': 180,
                '1 year': 365,
                '5 years': 1825
            }.get(period, 30)
            
            query_params = [
                bigquery.ScalarQueryParameter("ticker", "STRING", ticker),
                bigquery.ScalarQueryParameter("period_days", "INT64", period_days)
            ]
        
        job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        
        # Execute the query and convert the result to a Polars DataFrame
        pandas_df = client.query(query, job_config=job_config).to_dataframe()
        return pl.from_pandas(pandas_df)
    except Exception as e:
        print(f"Error during get_stock_data call: {e}")
        return pl.DataFrame()

def get_volume_data(
    client: bigquery.Client,
    ticker: str,
    period: str = 'max',
    volume_range: tuple = (0, 100000)
) -> pl.DataFrame:
    # Define the SQL query to fetch stock volume data
    period_filter = '' if period == 'max' else "AND date > DATE_SUB(CURRENT_DATE(), INTERVAL @period_days DAY)"
    
    min_volume = volume_range[0]
    max_volume = volume_range[1]
    
    # Handle infinite volume range
    if max_volume == float('inf'):
        volume_condition = "AND volume >= @min_volume"
    else:
        volume_condition = "AND volume BETWEEN @min_volume AND @max_volume"
    
    query = f"""
        SELECT
            date, ticker, volume
        FROM
            `{PROJECT_ID}.{DATASET_ID}.{STOCKS_TABLE_ID}`
        WHERE
            ticker = @ticker
            {volume_condition}
            {period_filter}
        ORDER BY
            date ASC
    """
    
    try:
        # Prepare the query parameters
        query_params = [
            bigquery.ScalarQueryParameter("ticker", "STRING", ticker),
            bigquery.ScalarQueryParameter("min_volume", "INT64", min_volume)
        ]
        
        # Add max_volume parameter if it is not infinite
        if max_volume != float('inf'):
            query_params.append(
                bigquery.ScalarQueryParameter("max_volume", "INT64", max_volume)
            )
        
        # Add period_days parameter when needed
        if period != 'max':
            period_days = {
                '1 month': 30,
                '3 months': 90,
                '6 months': 180,
                '1 year': 365,
                '5 years': 1825
            }.get(period, 30)
            
            query_params.append(
                bigquery.ScalarQueryParameter("period_days", "INT64", period_days)
            )
        
        job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        
        # Execute the query and convert the result to a Polars DataFrame
        pandas_df = client.query(query, job_config=job_config).to_dataframe()
        return pl.from_pandas(pandas_df)
    except Exception as e:
        print(f"Error during get_volume_data call: {e}")
        return pl.DataFrame()
    
def get_corr_matrix(
    client: bigquery.Client,
    tickers: List[str],
    period: str = 'max'
) -> pl.DataFrame:
    ticker_placeholders = ', '.join([f"'{ticker}'" for ticker in tickers])
    period_filter = '' if period == 'max' else "AND date > DATE_SUB(CURRENT_DATE(), INTERVAL @period_days DAY)"
    
    query = f"""
        SELECT
            ticker, date, MAX(close) AS close
        FROM
            `{PROJECT_ID}.{DATASET_ID}.{STOCKS_TABLE_ID}`
        WHERE
            ticker IN ({ticker_placeholders})
            {period_filter}
        GROUP BY
            ticker, date
        ORDER BY
            date ASC
    """
    
    try:
        query_params = []
        if period != 'max':
            period_days = {
                '1 month': 30,
                '3 months': 90,
                '6 months': 180,
                '1 year': 365,
                '5 years': 1825
            }.get(period, 30)
            query_params.append(
                bigquery.ScalarQueryParameter("period_days", "INT64", period_days)
            )
        
        job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        pandas_df = client.query(query, job_config=job_config).to_dataframe()
        
        stock_data = pl.from_pandas(pandas_df)
        if stock_data.is_empty():
            return pl.DataFrame()
        
        pivoted_data = stock_data.pivot(
            values='close',
            index='date',
            columns='ticker'
        )
        numeric_data = pivoted_data.drop("date")
        corr_matrix = numeric_data.corr()
        return corr_matrix
    except Exception as e:
        print(f"Error during get_corr_matrix_bigquery call: {e}")
        return pl.DataFrame()

def get_tickers(client: bigquery.Client) -> List[str]:
    query = f"""
        SELECT DISTINCT ticker
        FROM `{PROJECT_ID}.{DATASET_ID}.{SECTORS_TABLE_ID}`
        ORDER BY ticker
    """
    try:
        pandas_df = client.query(query).to_dataframe()
        return pandas_df['ticker'].tolist()
    except Exception as e:
        print(f"Error during get_tickers call: {e}")
        return ['NA']

def get_stocks_current_price(
    client: bigquery.Client,
    tickers: List[str]
) -> Dict[str, float]:
    ticker_placeholders = ', '.join([f"'{ticker}'" for ticker in tickers])
    query = f"""
        SELECT
            ticker, close
        FROM
            `{PROJECT_ID}.{DATASET_ID}.{STOCKS_TABLE_ID}`
        WHERE
            date = (SELECT MAX(date) FROM `{PROJECT_ID}.{DATASET_ID}.{STOCKS_TABLE_ID}`)
        AND
            ticker IN ({ticker_placeholders})
    """
    try:
        pandas_df = client.query(query).to_dataframe()
        return dict(zip(pandas_df["ticker"], pandas_df["close"]))
    except Exception as e:
        print(f"Error during get_stocks_current_price call: {e}")
        return {}

def get_sector_data(client: bigquery.Client) -> pl.DataFrame:
    # Define the SQL query to fetch sector data
    query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.{SECTORS_TABLE_ID}`
    """
    
    try:
        # Set up the query job configuration
        job_config = bigquery.QueryJobConfig()
        
        # Execute the query and convert the result to a Polars DataFrame
        pandas_df = client.query(query, job_config=job_config).to_dataframe()
        return pl.from_pandas(pandas_df)
    except Exception as e:
        print(f"Error during get_sector_data call: {e}")
        return pl.DataFrame()
    
def aggregate_portfolio_by_sector(portfolio_data: pl.DataFrame, sector_data: pl.DataFrame) -> pl.DataFrame:
    try:
        merged_data = portfolio_data.join(
            sector_data,
            left_on='Ticker',
            right_on='ticker',
            how='left'
        )
        
        aggregated_data = merged_data.group_by('sector').agg(
            pl.col('Value').sum().alias('Total Value')
        )
        
        aggregated_data = aggregated_data.sort('Total Value', descending=True)
        
        return aggregated_data
    except Exception as e:
        print(f"Error during portfolio aggregation: {e}")
        return pl.DataFrame()

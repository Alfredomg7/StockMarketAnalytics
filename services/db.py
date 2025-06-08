import sqlite3
from typing import List, Dict
import polars as pl
from config import DATABASE_URL

def get_connection(database: str = DATABASE_URL) -> sqlite3.Connection:
    """ Create and return a connection to the SQLite database file located at the URL provided """
    try:
        conn = sqlite3.connect(database)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None
 
def get_price_data(
    conn: sqlite3.Connection,
    ticker: str,
    period: str = 'max'
) -> pl.DataFrame:
    period_filter = '' if period == 'max' else "AND date > date('now', ?)"
    query = f"""
        SELECT
            date, open, close, high, low
        FROM
            stock_prices
        WHERE
            ticker = ?
        {period_filter}
    """
    query = query.format(period_filter=period_filter)

    try:
        parameters = [ticker] if period == 'max' else [ticker, f'-{period}']
        stock_data = pl.read_database(
            query=query,
            connection=conn,
            execute_options={"parameters": parameters}
        )
        return stock_data
    except Exception as e:
        print(f"Error during get_stock_data call: {e}")
        return pl.DataFrame()

def get_volume_data(
    conn: sqlite3.Connection,
    ticker: str,
    period: str = 'max',
    volume_range: tuple = (0, 100000)
) -> pl.DataFrame:
    period_filter = "" if period == 'max' else "AND date > date('now', ?)"
    query = """
        SELECT
            ticker, date, volume
        FROM
            stock_prices
        WHERE
            ticker = ?
        {period_filter}
        AND
            volume BETWEEN ? AND ?
    """
    query = query.format(period_filter=period_filter)
    try:
        if period == 'max':
            parameters = [ticker, volume_range[0], volume_range[1]]
        else:
            parameters = [ticker, f'-{period}', volume_range[0], volume_range[1]]
        stock_data = pl.read_database(
            query=query,
            connection=conn,
            execute_options={"parameters": parameters}
        )
        return stock_data
    except Exception as e:
        print(f"Error during get_volume_data call: {e}")
        return pl.DataFrame()

def get_corr_matrix(
    conn: sqlite3.Connection,
    tickers: list,
    period: str = 'max'
) -> pl.DataFrame:
    ticker_placeholders = ', '.join(['?' for _ in tickers])
    period_filter = '' if period == 'max' else "AND date > date('now', ?)"
    query = f"""
            SELECT
                ticker, date, close
            FROM
                stock_prices
            WHERE
                ticker IN ({ticker_placeholders})
            {period_filter}
        """
    query = query.format(period_filter=period_filter)
    try:
        parameters = tickers if period == 'max' else tickers + [f'-{period}']
        stock_data = pl.read_database(
            query=query,
            connection=conn,
            execute_options={"parameters": parameters}
        )
        if stock_data.is_empty():
            return pl.DataFrame()
        
        pivoted_data = stock_data.pivot(
            values='close',
            index='date',
            columns='ticker'
        )
        min_date = pivoted_data.drop_nulls().select('date').min()
        max_date = pivoted_data.drop_nulls().select('date').max()
        pivoted_data = pivoted_data.filter(
            (pl.col("date") >= min_date) & (pl.col("date") <= max_date)
        )
        numeric_data = pivoted_data.drop("date")
        corr_matrix = numeric_data.corr()
        return corr_matrix
    except Exception as e:
        print(f"Error during get_corr_matrix call: {e}")
        return pl.DataFrame()

def get_tickers(conn: sqlite3.Connection) -> List[str]:
    query = "SELECT DISTINCT ticker FROM stock_sector ORDER BY ticker"
    try:
        tickers = pl.read_database(query=query, connection=conn)
        return tickers['ticker'].to_list()
    except Exception as e:
        print(f"Error during get_tickers call: {e}")
        return ['NA']

def get_stocks_current_price(
    conn: sqlite3.Connection,
    tickers: List[str]
) -> Dict[str, float]:
    query = """
        SELECT
            ticker, close
        FROM
            stock_prices
        WHERE
            date = (SELECT MAX(date) FROM stock_prices)
        AND
            ticker IN ({ticker_placeholders})
    """
    ticker_placeholders = ', '.join(['?' for _ in tickers])
    query = query.format(ticker_placeholders=ticker_placeholders)
    try:
        stock_data = pl.read_database(
            query=query,
            connection=conn,
            execute_options={"parameters": tickers}
        )
        return dict(zip(stock_data["ticker"], stock_data["close"]))
    except Exception as e:
        print(f"Error during get_stocks_current_price call: {e}")
        return {}

def get_sector_data(conn: sqlite3.Connection) -> pl.DataFrame:
    query = "SELECT * FROM stock_sector"
    try:
        sector_data = pl.read_database(query=query, connection=conn)
        return sector_data
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

from typing import Dict
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output
import components as cmp
from guide.layout import create_layout as create_guide_layout
from market_dashboard.layout import create_layout as create_market_dashboard_layout
from portfolio_dashboard.layout import create_layout as create_portfolio_dashboard_layout
from portfolio_form.layout import create_layout as create_portfolio_form_layout
from market_dashboard.callbacks import register_callbacks as register_market_callbacks
from portfolio_dashboard.callbacks import register_callbacks as register_portfolio_callbacks
from portfolio_form.callbacks import register_callbacks as register_portfolio_form_callbacks
from services.db import get_stocks_current_price, get_tickers
import services.db as db

def create_app() -> Dash:
    # Init Dash app with bootstrap theme
    dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
    app = Dash(__name__, external_stylesheets=[dbc.themes.LUX, dbc_css])
    app.title = 'Stock Market Analytics App'

    # Define paths for the sidebar
    paths = {
        'Market Dashboard': '/',
        'My Portfolio': '/portfolio-form',
        'Portfolio Dashboard': '/portfolio-dashboard',
        'User Guide': '/guide',
    }
    
    # Create app main components
    sidebar = cmp.create_sidebar(paths)
    content = html.Div(
                id='page-content', 
                className='p-4',
                style={
                    'height': '100%',
                    "overflow-y": "auto",
                })
    footer = cmp.create_footer()

    # Define app layout
    app.layout = html.Div([
            dcc.Location(id='url'),
            dcc.Store(id={'type': 'portfolio-data', 'section': 'global'}, storage_type='local'),
            dcc.Store(id={'type': 'price-data', 'section': 'global'}, storage_type='local'),
            dbc.Row([
                sidebar,
                dbc.Col(content, sm=12, md={'size': 10, 'offset': 2}, className='mb-4')
            ], className='h-100'),
            footer
        ],
        className="bg-primary text-light h-100",
    )

    # Handle page navigation through callbacks
    @app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname')
    )
    def display_page(pathname: str) -> html.Div:
        if pathname == '/':
            return create_market_dashboard_layout()
        elif pathname == '/portfolio-form':
            return create_portfolio_form_layout()
        elif pathname == '/portfolio-dashboard':
            return create_portfolio_dashboard_layout()
        elif pathname == '/guide':
            return create_guide_layout()
        else:
            return html.H1('404 - Page Not Found', className='text-center text-danger fs-4 fw-bold mt-5')

    # Fetch stock prices on app load
    @app.callback(
        Output({"type": "price-data", "section": "global"}, "data"),
        Input("url", "pathname"),
        prevent_initial_call=True,
    )
    def fetch_prices_on_load(_) -> Dict[str, float]:
        conn = db.get_connection()
        try:
            tickers = db.get_tickers(conn)
            if not tickers:
                return {}
            prices = db.get_stocks_current_price(conn, tickers)
            return prices
        except Exception as e:
            return {"Error during fetch_prices_on_load": str(e)}
        finally:
            conn.close()

    register_market_callbacks(app)
    register_portfolio_callbacks(app)
    register_portfolio_form_callbacks(app)
    return app

# Init app and server
app = create_app()
server = app.server

# Run app
if __name__ == '__main__':
    app.run_server(debug=True)
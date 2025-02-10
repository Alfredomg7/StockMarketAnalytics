from dash import html
import dash_bootstrap_components as dbc
import components as cmp
from services.db import get_tickers

def create_layout() -> dbc.Container:
    # Header components
    title = html.H1("My Portfolio", className="text-center display-4 text-light")
    description = html.P("Customize your stocks portfolio", className="text-center opacity-75 fs-4")

    # Feedback Alert
    alert_feedback = cmp.create_alert(id={"type": "alert-feedback", "section": "portfolio-form"})

    # Get ticker options
    ticker_list = get_tickers()
    ticker_options = [{"label": ticker, "value": ticker} for ticker in ticker_list]

    # Select input for stock ticker
    ticker_select = dbc.Col(
        [
            cmp.create_label("Stock Ticker:", {"type": "input-ticker", "section": "portfolio-form"}),
            cmp.create_select(
                id={"type": "input-ticker", "section": "portfolio-form"},
                options=ticker_options,
                value=ticker_options[0]["value"]
            )
        ],
        xs=12, sm=10, md=6, lg=5, xl=4, class_name="pe-lg-3 mb-3 mb-lg-0"
    )

    # Slider input for number of shares
    shares_slider = dbc.Col(
        [
            cmp.create_label("Shares Qt:", {"type": "input-shares", "section": "portfolio-form"}),
            cmp.create_numeric_input(
                id={"type": "input-shares", "section": "portfolio-form"},
                min=0,
                max=1000,
                step=0.01,
                value=10.00
            )
        ],
        xs=12, sm=10, md=6, lg=5, xl=4, class_name="pe-lg-3 mb-3 mb-lg-0"
    )

    # Buttons
    blank_space = html.Div(style={"height": "34px"})
    add_button = dbc.Col(
        [        
            blank_space,
            cmp.create_button(
                    id={"type": "button-submit", "section": "portfolio-form"},
                    text="Add",
                    color="success"
            ),
        ],
        xs=12, sm=4, md=3, lg=2, xl=2, class_name="d-grid align-items-center"
    )

    edit_button = dbc.Col(
        [        
            blank_space,
            cmp.create_button(
                    id={"type": "button-edit", "section": "portfolio-form"},
                    text="Edit",
                    color="warning"
            ),
        ],
        xs=12, sm=4, md=3, lg=2, xl=2, class_name="d-grid align-items-center"
    )
                
    delete_button = dbc.Col(
        [        
            blank_space,
            cmp.create_button(
                    id={"type": "button-delete", "section": "portfolio-form"},
                    text="Delete",
                    color="danger"
            ),
        ],
        xs=12, sm=4, md=3, lg=2, xl=2, class_name="d-grid align-items-center"
    )

    # Cards
    # Portfolio Form Card
    portfolio_form_group = dbc.Card(
        dbc.CardBody([
            html.H4("Manage Portfolio", className="card-title text-center mb-4"),
            dbc.Row(
                [ticker_select, shares_slider], 
                class_name="justify-content-center mb-3"
            ),
            dbc.Row(
                [add_button, edit_button, delete_button], 
                class_name="justify-content-center"
            )
        ]),
        class_name="mb-4 shadow-sm bg-dark text-light"
    )

    # Portfolio Display Card
    portfolio_table_container = dbc.Card(
        dbc.CardBody(
            [
                html.H4("Overview", className="card-title text-center mb-4"),
                html.Div(id={"type": "output-portfolio-data", "section": "portfolio-form"})
            ]
        ),
        class_name="mb-4 shadow-sm bg-dark text-light"
    )

    # Layout
    layout = dbc.Container([
        # Alert for feedback on user actions
        alert_feedback,
        # Header Section
        dbc.Row([dbc.Col(title, width=12)], class_name="my-2 text-center"),
        dbc.Row([dbc.Col(description, width=12)], class_name="mb-2 text-center"),
        html.Hr(className='mb-4'),

        # Portfolio Form Section
        dbc.Row([dbc.Col(portfolio_form_group, md=12, xl=10, class_name="mx-auto mb-4")]),

        # Portfolio Display Section
        dbc.Row([dbc.Col(portfolio_table_container, md=12, xl=10, class_name="mx-auto mb-4")]),
    ], fluid=True)

    return layout

from dash import dcc, html
import dash_bootstrap_components as dbc
import components as cmp
import services.db as db
from utils.google_cloud_utils import get_bigquery_client

def create_layout(tickers: list) -> dbc.Container:
    title = html.H1('Market Dashboard', className='text-center display-4 text-light')
    description = html.P(
        'Discover insights about the stock market', 
        className='text-center opacity-75 fs-4'
    )

    # Get options dictionaries for the select components
    ticker_options = [{'label': ticker, 'value': ticker} for ticker in tickers]

    volume_options = [
        {'label': 'All', 'value': 'all'},
        {'label': 'Very High (> 5M)', 'value': 'very_high'},
        {'label': 'High (1M - 5M)', 'value': 'high'},
        {'label': 'Medium (500K - 1M)', 'value': 'medium'},
        {'label': 'Low (100K - 500K)', 'value': 'low'},
        {'label': 'Very Low (< 100K)', 'value': 'very_low'}
    ]

    # Create the UI components
    general_filters_group = dbc.Card(
        dbc.CardBody([
            dbc.Row([
                # Ticker select input
                dbc.Col([
                    cmp.create_label('Select Stock:', {'type': 'dynamic-select-stock', 'section': 'market'}),
                    cmp.create_select(
                        id={'type': 'dynamic-select-stock', 'section': 'market'},
                        options=ticker_options,
                        value=ticker_options[0]['value']
                    )
                ], sm=12, md=4, className="pe-3 my-2 align-self-center"),

                # Time period buttons
                dbc.Col([
                    cmp.create_label('Select Time Period:', {'type': 'time-period-group', 'section': 'market'}),
                    cmp.create_button_group(
                        id={'type': 'time-period-group', 'section': 'market'},
                        buttons=[
                            {'id': {'type': 'btn-one-month', 'section': 'market'}, 'text': '1M'},
                            {'id': {'type': 'btn-three-months', 'section': 'market'}, 'text': '3M'},
                            {'id': {'type': 'btn-six-months', 'section': 'market'}, 'text': '6M'},
                            {'id': {'type': 'btn-one-year', 'section': 'market'}, 'text': '1Y'},
                            {'id': {'type': 'btn-five-years', 'section': 'market'}, 'text': '5Y'},
                            {'id': {'type': 'btn-max', 'section': 'market'}, 'text': 'MAX'},
                        ],
                        color="primary",
                        size="md",
                    )
                ], sm=12, md=8, className="ps-3 align-self-center")
            ])
        ]),
        class_name="mb-4 shadow-sm bg-dark text-light"
    )

    navigation_buttons_group = dbc.Card(
        dbc.CardBody(
            dbc.ButtonGroup(
                [
                    dbc.Button("My Portfolio", href="/portfolio-form", color="success"),
                    dbc.Button("Portfolio Dashboard", href="/portfolio-dashboard", color="info"),
                    dbc.Button("Guide", href="/guide", color="secondary"),
                ],
                size="sm",
                className="w-100",
                style={"justify-content": "center"}
            )
        ),
        class_name="mb-4 shadow-sm bg-dark text-light"
    )

    # Charts section
    charts_section = dbc.Row([
        # Line and Candlestick charts row
        dbc.Row([
            dbc.Col(
                cmp.create_chart_container(
                    content_id={'type': 'dynamic-output-line', 'section': 'market'},
                    bg_color='dark',
                    loading_color=cmp.PRIMARY_COLOR
                ), 
                xl=6, md=12, sm=12
            ),
            dbc.Col(
                cmp.create_chart_container(
                    content_id={'type': 'dynamic-output-candlestick', 'section': 'market'},
                    bg_color='dark',
                    loading_color=cmp.PRIMARY_COLOR
                ), 
                xl=6, md=12, sm=12
            )
        ], className='mb-4 align-items-stretch'),
        
        # Volume and Correlation charts row
        dbc.Row([
            dbc.Col(
                cmp.create_chart_container(
                    content_id={'type': 'dynamic-output-bar', 'section': 'market'},
                    inputs=[
                        dbc.Row([
                            dbc.Col(
                                cmp.create_label(
                                    'Filter by Volume:', 
                                    {'type': 'dynamic-select-volume', 'section': 'market'}
                                ), 
                                width=12
                            )
                        ]),
                        dbc.Row([
                            dbc.Col(
                                cmp.create_select(
                                    id={'type': 'dynamic-select-volume', 'section': 'market'},
                                    options=volume_options,
                                    value=volume_options[0]['value'],
                                    placeholder='Select a volume range'
                                ), 
                                width=12
                            )
                        ])
                    ],
                    bg_color='dark',
                    loading_color=cmp.PRIMARY_COLOR
                ),
                xl=6, md=12, sm=12
            ),
            dbc.Col(
                cmp.create_chart_container(
                    content_id={'type': 'dynamic-output-heatmap', 'section': 'market'},
                    inputs=[
                        dbc.Row([
                            dbc.Col(
                                cmp.create_label(
                                    'Select Stocks for Correlation Analysis:', 
                                    {'type': 'dynamic-select-corr', 'section': 'market'}
                                ), 
                                width=12
                            )
                        ]),
                        dbc.Row([
                            dbc.Col(
                                cmp.create_multi_select(
                                    id={'type': 'dynamic-select-corr', 'section': 'market'},
                                    options=ticker_options,
                                    value=[ticker_options[0]['value'], ticker_options[1]['value']],
                                    placeholder='Select stocks'
                                ), 
                                width=12
                            )
                        ])
                    ],
                    bg_color='dark',
                    loading_color=cmp.PRIMARY_COLOR
                ),
                xl=6, md=12, sm=12
            )
        ], className='align-items-stretch')
    ])

    # Main layout
    layout = dbc.Container([
        # Store components
        dcc.Store(
            id={'type': 'time-period-store', 'section': 'market'}, 
            data='1 month'  # Valor inicial
        ),

        # Header section
        dbc.Row([dbc.Col(title, width=12)], class_name='mt-2 mb-2 text-center'),
        dbc.Row([dbc.Col(description, width=12)], class_name='mb-2 text-center'),
        html.Hr(className='mb-4'),

        # Filters and navigation section
        dbc.Row([
            dbc.Col(general_filters_group, md=12, lg=10, xl=8),
            dbc.Col(navigation_buttons_group, md=12, lg=10, xl=4)
        ], class_name='mb-4 justify-content-center'),

        # Charts section
        charts_section

    ], fluid=True)

    return layout
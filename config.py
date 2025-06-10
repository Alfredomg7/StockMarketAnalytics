import os
from dotenv import load_dotenv

load_dotenv()

# Define list of required environment variables
REQUIRED_ENV_VARS = [
    'TYPE',
    'PROJECT_ID',
    'DATASET_ID',
    'STOCKS_TABLE_ID',
    'SECTORS_TABLE_ID',
    'PRIVATE_KEY_ID',
    'PRIVATE_KEY',
    'CLIENT_EMAIL',
    'CLIENT_ID',
    'AUTH_URI',
    'TOKEN_URI',
    'AUTH_PROVIDER_X509_CERT_URL',
    'CLIENT_X509_CERT_URL',
    'UNIVERSE_DOMAIN',
]

# Google Cloud
# Create dictionary with credentials environment variables
CREDENTIALS_DICT = {
    "type": os.getenv("TYPE"),
    "project_id": os.getenv("PROJECT_ID"),
    "private_key_id": os.getenv("PRIVATE_KEY_ID"),
    "private_key": os.getenv("PRIVATE_KEY"),
    "client_email": os.getenv("CLIENT_EMAIL"),
    "client_id": os.getenv("CLIENT_ID"),
    "auth_uri": os.getenv("AUTH_URI"),
    "token_uri": os.getenv("TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("UNIVERSE_DOMAIN"),
}

# Google Cloud project ID
PROJECT_ID = os.getenv("PROJECT_ID")
# BigQuery dataset and tables IDs
DATASET_ID = os.getenv("DATASET_ID")
STOCKS_TABLE_ID = os.getenv("STOCKS_TABLE_ID")
SECTORS_TABLE_ID = os.getenv("SECTORS_TABLE_ID")

"""BigQuery connection, shared across every page.

Uses the same least-privilege `evidence-reporting` service account set up
for the (now-retired) Evidence.dev report: bigquery.dataViewer +
bigquery.jobUser only, no write access. Credentials come from Streamlit
Secrets (st.secrets["gcp_service_account"]), matching Streamlit's official
BigQuery example — not a GOOGLE_APPLICATION_CREDENTIALS file path, so the
same code works unchanged on Streamlit Community Cloud (secrets pasted into
App -> Settings -> Secrets) as it does locally (.streamlit/secrets.toml,
gitignored, never committed).
"""

import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

from utils.config import PROJECT_ID


@st.cache_resource
def get_client() -> bigquery.Client:
    if "gcp_service_account" not in st.secrets:
        st.error(
            "No `gcp_service_account` found in Streamlit secrets. Add "
            "`.streamlit/secrets.toml` locally (gitignored, never committed), or "
            "for Streamlit Community Cloud, paste it under App -> Settings -> Secrets. "
            "See streamlit/README.md."
        )
        st.stop()
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    return bigquery.Client(credentials=credentials, project=PROJECT_ID)


@st.cache_data(ttl=300)
def run_query(sql: str):
    """Runs a query and returns a pandas DataFrame. Cached for 5 minutes so
    repeated widget interactions on a page don't re-hit BigQuery."""
    return get_client().query(sql).to_dataframe()

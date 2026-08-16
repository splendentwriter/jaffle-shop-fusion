"""BigQuery connection, shared across every page.

Uses the same least-privilege `evidence-reporting` service account set up
for the (now-retired) Evidence.dev report: bigquery.dataViewer +
bigquery.jobUser only, no write access. Auth is via Application Default
Credentials — point GOOGLE_APPLICATION_CREDENTIALS at that key (see .env).
"""

import os

import streamlit as st
from dotenv import load_dotenv
from google.cloud import bigquery

from utils.config import PROJECT_ID

load_dotenv()


@st.cache_resource
def get_client() -> bigquery.Client:
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        st.error(
            "GOOGLE_APPLICATION_CREDENTIALS is not set. Export it or add it to "
            "streamlit/.env — see streamlit/README.md."
        )
        st.stop()
    return bigquery.Client(project=PROJECT_ID)


@st.cache_data(ttl=300)
def run_query(sql: str):
    """Runs a query and returns a pandas DataFrame. Cached for 5 minutes so
    repeated widget interactions on a page don't re-hit BigQuery."""
    return get_client().query(sql).to_dataframe()

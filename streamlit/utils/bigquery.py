"""BigQuery connection, shared across every page.

Uses the same least-privilege `evidence-reporting` service account set up
for the (now-retired) Evidence.dev report: bigquery.dataViewer +
bigquery.jobUser only, no write access. Auth is via Application Default
Credentials — point GOOGLE_APPLICATION_CREDENTIALS at that key (see .env).
"""

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from google.cloud import bigquery

from utils.config import PROJECT_ID

# load_dotenv() with no args searches from the current working directory,
# which isn't reliable — it depends on where `streamlit run` was invoked
# from (e.g. the repo root vs streamlit/). Anchor it to this file's
# location instead so it finds streamlit/.env regardless of CWD.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


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

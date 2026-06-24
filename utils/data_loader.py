import pandas as pd
import streamlit as st

DATA_PATH = "data/mock_clients.csv"


@st.cache_data
def load_clients() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)

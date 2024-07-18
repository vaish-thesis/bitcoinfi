import streamlit as st
import requests
import pandas as pd

# Function to get all protocols
def get_protocols():
    response = requests.get("https://api.llama.fi/protocols")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to load protocols")
        return []

# Function to get TVL for a protocol
def get_tvl(protocol_slug):
    response = requests.get(f"https://api.llama.fi/tvl/{protocol_slug}")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to load TVL for {protocol_slug}")
        return None

# Function to get historical TVL for a protocol
def get_historical_tvl(protocol_slug):
    response = requests.get(f"https://api.llama.fi/protocol/{protocol_slug}")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to load historical TVL for {protocol_slug}")
        return []

# Streamlit app
st.title("DeFi Protocol Comparison")

# Load protocols
protocols = get_protocols()
protocol_names = [protocol['name'] for protocol in protocols]
protocol_slugs = {protocol['name']: protocol['slug'] for protocol in protocols}

# Select protocols to compare
selected_protocols = st.multiselect("Select protocols to compare", protocol_names)

if selected_protocols:
    data = []
    for protocol_name in selected_protocols:
        protocol_slug = protocol_slugs[protocol_name]
        tvl_data = get_tvl(protocol_slug)
        if tvl_data:
            data.append({
                "Protocol": protocol_name,
                "TVL": tvl_data['totalLiquidityUSD']
            })
    df = pd.DataFrame(data)
    st.table(df)

    # Option to show historical data
    if st.checkbox("Show historical TVL"):
        for protocol_name in selected_protocols:
            protocol_slug = protocol_slugs[protocol_name]
            historical_tvl_data = get_historical_tvl(protocol_slug)
            if historical_tvl_data:
                tvl_df = pd.DataFrame(historical_tvl_data['tvl'])
                tvl_df['date'] = pd.to_datetime(tvl_df['date'], unit='s')
                tvl_df.set_index('date', inplace=True)
                st.line_chart(tvl_df['totalLiquidityUSD'], width=0, height=400)
                st.write(f"Historical TVL for {protocol_name}")


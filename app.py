import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Set page title
st.set_page_config(page_title="DeFi Protocol Comparison")

st.title("DeFi Protocol Comparison Tool")

# Function to fetch data from DeFi Llama API
def fetch_protocols():
    url = "https://api.llama.fi/protocols"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch data from DeFi Llama API")
        return None

# Fetch protocols data
protocols_data = fetch_protocols()

if protocols_data:
    # Create a DataFrame from the protocols data
    df = pd.DataFrame(protocols_data)
    
    # Allow users to select protocols
    selected_protocols = st.multiselect(
        "Select protocols to compare",
        options=df['name'].tolist(),
        default=df['name'].iloc[:5].tolist()  # Default to top 5 protocols
    )
    
    if selected_protocols:
        # Filter the DataFrame based on selected protocols
        selected_df = df[df['name'].isin(selected_protocols)]
        
        # Display comparison table
        st.subheader("Protocol Comparison Table")
        comparison_table = selected_df[['name', 'tvl', 'chain', 'change_1d', 'change_7d', 'change_1m']]
        st.dataframe(comparison_table)
        
        # Create a bar chart of TVL for selected protocols
        st.subheader("Total Value Locked (TVL) Comparison")
        fig = px.bar(selected_df, x='name', y='tvl', title="TVL by Protocol")
        st.plotly_chart(fig)
        
        # Allow user to select a protocol for detailed view
        selected_protocol = st.selectbox("Select a protocol for detailed view", selected_protocols)
        
        if selected_protocol:
            st.subheader(f"Detailed View: {selected_protocol}")
            protocol_data = selected_df[selected_df['name'] == selected_protocol].iloc[0]
            
            col1, col2, col3 = st.columns(3)
            col1.metric("TVL", f"${protocol_data['tvl']:,.0f}")
            col2.metric("24h Change", f"{protocol_data['change_1d']:.2f}%")
            col3.metric("7d Change", f"{protocol_data['change_7d']:.2f}%")
            
            # Display additional information
            st.write(f"Chain: {protocol_data['chain']}")
            st.write(f"Description: {protocol_data['description']}")
            
            # Fetch historical data for the selected protocol
            historical_url = f"https://api.llama.fi/protocol/{protocol_data['slug']}"
            historical_response = requests.get(historical_url)
            if historical_response.status_code == 200:
                historical_data = historical_response.json()
                if 'tvl' in historical_data and isinstance(historical_data['tvl'], list):
                    tvl_data = historical_data['tvl']
                    tvl_df = pd.DataFrame(tvl_data, columns=['Date', 'TVL'])
                    tvl_df['Date'] = pd.to_datetime(tvl_df['Date'], unit='s')
                    
                    # Plot historical TVL
                    st.subheader("Historical TVL")
                    fig = px.line(tvl_df, x='Date', y='TVL', title=f"{selected_protocol} Historical TVL")
                    st.plotly_chart(fig)
                else:
                    st.warning("Historical TVL data not available or in unexpected format for this protocol")
            else:
                st.error("Failed to fetch historical data")
else:
    st.error("No data available. Please try again later.")

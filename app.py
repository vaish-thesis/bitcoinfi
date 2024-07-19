import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page title
st.set_page_config(page_title="DeFi Protocol Comparison", layout="wide")

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
        
        # Define the columns we want to display if they're available
        desired_columns = ['name', 'tvl', 'chain', 'change_1d', 'change_7d', 'change_1m']
        
        # Filter to only include columns that are actually in the DataFrame
        available_columns = [col for col in desired_columns if col in selected_df.columns]
        
        comparison_table = selected_df[available_columns]
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
            
            # Define major stats to highlight
            major_stats = ['tvl', 'change_1d', 'change_7d']
            
            # Display major stats
            for stat in major_stats:
                if stat in protocol_data and pd.notna(protocol_data[stat]):
                    value = protocol_data[stat]
                    if stat == 'tvl':
                        st.markdown(f"<h2 style='text-align: center;'>TVL: ${value:,.2f}</h2>", unsafe_allow_html=True)
                    elif 'change' in stat:
                        st.markdown(f"<h3 style='text-align: center;'>{stat.capitalize()}: {value:.2f}%</h3>", unsafe_allow_html=True)

            # Display other information
            st.subheader("Additional Information")
            for key, value in protocol_data.items():
                if key not in major_stats and pd.notna(value) and value != '':
                    if isinstance(value, (float, int)):
                        st.write(f"**{key.capitalize()}:** {value:,}")
                    elif isinstance(value, str):
                        st.write(f"**{key.capitalize()}:** {value}")
                    elif isinstance(value, list):
                        st.write(f"**{key.capitalize()}:** {', '.join(map(str, value))}")
                    elif isinstance(value, dict):
                        st.write(f"**{key.capitalize()}:**")
                        for sub_key, sub_value in value.items():
                            st.write(f"  - {sub_key}: {sub_value}")
                    else:
                        st.write(f"**{key.capitalize()}:** {value}")
            
            # Fetch historical data for the selected protocol
            historical_url = f"https://api.llama.fi/protocol/{protocol_data['slug']}"
            historical_response = requests.get(historical_url)
            if historical_response.status_code == 200:
                historical_data = historical_response.json()
                if 'tvl' in historical_data and isinstance(historical_data['tvl'], list):
                    tvl_data = historical_data['tvl']
                    tvl_df = pd.DataFrame(tvl_data, columns=['Date', 'TVL'])
                    tvl_df['Date'] = pd.to_datetime(tvl_df['Date'], unit='s')
                    
                    # Calculate 1-day and 7-day changes
                    tvl_df['1d_change'] = tvl_df['TVL'].pct_change(periods=1) * 100
                    tvl_df['7d_change'] = tvl_df['TVL'].pct_change(periods=7) * 100
                    
                    # Create subplots
                    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                                        subplot_titles=("TVL", "1-day Change (%)", "7-day Change (%)"))
                    
                    # Add TVL trace
                    fig.add_trace(go.Scatter(x=tvl_df['Date'], y=tvl_df['TVL'], name="TVL"), row=1, col=1)
                    
                    # Add 1-day change trace
                    fig.add_trace(go.Scatter(x=tvl_df['Date'], y=tvl_df['1d_change'], name="1-day Change"), row=2, col=1)
                    
                    # Add 7-day change trace
                    fig.add_trace(go.Scatter(x=tvl_df['Date'], y=tvl_df['7d_change'], name="7-day Change"), row=3, col=1)
                    
                    # Update layout
                    fig.update_layout(height=900, title_text=f"{selected_protocol} Historical Data")
                    fig.update_xaxes(title_text="Date", row=3, col=1)
                    fig.update_yaxes(title_text="TVL ($)", row=1, col=1)
                    fig.update_yaxes(title_text="Change (%)", row=2, col=1)
                    fig.update_yaxes(title_text="Change (%)", row=3, col=1)
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Historical TVL data not available or in unexpected format for this protocol")
            else:
                st.error("Failed to fetch historical data")
else:
    st.error("No data available. Please try again later.")

import streamlit as st
import pandas as pd
import plotly.express as px

# cache data
@st.cache_data
def load_data():
    data = pd.read_csv("output.csv")
    return data 

df = load_data()

st.title("Veterans Demographics Explorer")

# siderbar
st.sidebar.header("Filter Data")

# State filter
state_options = sorted(df['State'].dropna().unique())
selected_states = st.sidebar.multiselect("Select State(s):", state_options)

# counties based on states
if selected_states:
    county_options = sorted(
        df[df['State'].isin(selected_states)]['County'].dropna().unique()
    )
else:
    county_options = sorted(df['County'].dropna().unique())

selected_counties = st.sidebar.multiselect("Select County(ies):", county_options)

# filter data by selections
filtered_df = df.copy()

if selected_states:
    filtered_df = filtered_df[filtered_df['State'].isin(selected_states)]

if selected_counties:
    filtered_df = filtered_df[filtered_df['County'].isin(selected_counties)]

# dataframe categories
category_groups = {
    "Age Ranges": [col for col in df.columns if "(Age Range" in col],
    "Ethnic Groupings": [col for col in df.columns if "(Broad Ethnic Groupings)" in col],
    "Income Ranges": [col for col in df.columns if "(Estimated Income Range)" in col],
    "Voting Frequency": [col for col in df.columns if "(Voting Frequency)" in col],
    "Ideology": [col for col in df.columns if "(Ideology - General)" in col],
    "Party Affiliation": [col for col in df.columns if "(Parties Description)" in col]
}

st.sidebar.header("Graph Options")
graph_type = st.sidebar.selectbox("Select Category to Visualize:", list(category_groups.keys()))
columns_to_graph = category_groups[graph_type]

chart_type = st.sidebar.radio("Chart Type:", ["Bar", "Pie"])

# transform data for plots
melted_df = filtered_df[columns_to_graph].sum().reset_index()
melted_df.columns = ['Category', 'Count']
melted_df = melted_df[melted_df['Count'] > 0]

# plotly
st.subheader(f"{graph_type} Distribution")

if chart_type == "Bar":
    fig = px.bar(
        melted_df, 
        x='Category', 
        y='Count', 
        text='Count', 
        labels={'Count': 'Number of People'},
    )
    fig.update_layout(xaxis_tickangle=-45)
else:
    fig = px.pie(
        melted_df, 
        names='Category', 
        values='Count', 
        hole=0.3 if "🧓" in graph_type else 0.0  # Donut for age groups, optional
    )

st.plotly_chart(fig, use_container_width=True)


# dropdown with filtered dataframe
with st.expander("🔍 View Filtered Data"):
    st.dataframe(filtered_df)

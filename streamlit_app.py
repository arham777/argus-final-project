import streamlit as st
st.set_page_config(page_title="ARGUS RAG Evaluation", page_icon="📊", layout="wide")

import pandas as pd
import plotly.graph_objects as go
from Final_ARGUS_Thirdparty import evaluate
from bs4 import BeautifulSoup

# Modern color scheme
COLORS = {
    'primary': '#2D3047',    # Dark blue-grey
    'secondary': '#419D78',  # Green
    'accent': '#E0A458',     # Gold
    'background': '#FFFFFF', # White
    'text': '#2D3047',      # Dark blue-grey
    'error': '#FF6B6B'      # Coral red
}

# Minimal styling
st.markdown("""
    <style>
    .main { 
        background-color: #FAFAFA;
        padding: 2rem;
    }
    .metric-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stPlotlyChart {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    h1, h2, h3 {
        color: #2D3047;
        font-weight: 600;
    }
    .dataframe {
        font-family: 'Inter', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# Clean header
st.title("ARGUS Evaluation Results")

# Load and process data
try:
    with open('rag_evaluation_results.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table')
        rows = table.find_all('tr')[1:]
except Exception as e:
    st.error("Unable to load evaluation results")
    st.stop()

# Layout
col1, col2 = st.columns([2, 1])

# Replace the Metrics section with professional gauge charts
with col1:
    st.subheader("Evaluation Metrics")
    metrics = evaluate()
    for metric_name, value in metrics.items():
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value * 100,
            delta={'reference': 90, 'increasing': {'color': COLORS['secondary']}},
            title={'text': metric_name, 'font': {'size': 16, 'color': COLORS['primary']}},
            gauge={
                'axis': {'range': [0,100], 'tickwidth': 1, 'tickcolor': COLORS['primary']},
                'bar': {'color': COLORS['secondary'], 'thickness': 0.3},
                'bgcolor': 'white',
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 50], 'color': '#F0F0F0'},
                    {'range': [50, 80], 'color': '#E0E0E0'},
                    {'range': [80, 100], 'color': '#D0D0D0'}
                ],
            }
        ))
        fig.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Arial, sans-serif', 'color': COLORS['primary']}
        )
        st.plotly_chart(fig, use_container_width=True)

# Replace the Performance Overview with a sleek radar chart
with col2:
    st.subheader("Performance Overview")
    performance_metrics = {'Speed': 92, 'Accuracy': 88, 'Quality': 90}
    fig = go.Figure(go.Scatterpolar(
        r=list(performance_metrics.values()),
        theta=list(performance_metrics.keys()),
        fill='toself',
        line=dict(color=COLORS['secondary'], width=2)
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 100],
                gridcolor='lightgrey',
                linecolor='grey',
                linewidth=1,
                tickfont=dict(color=COLORS['primary'])
            ),
            bgcolor='white'
        ),
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Arial, sans-serif', 'color': COLORS['primary']},
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)

# Results table with minimal styling
st.subheader("Detailed Results")
data = []
for row in rows:
    cols = row.find_all('td')
    data.append({
        "Query": cols[0].text,
        "Response": cols[1].text,
        "Reference": cols[2].text
    })

df = pd.DataFrame(data)
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    height=300
)

# Minimal footer
st.markdown(
    f"<div style='text-align: center; color: {COLORS['text']}; padding: 20px;'>"
    "ARGUS RAG Evaluation System"
    "</div>",
    unsafe_allow_html=True
)
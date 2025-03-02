import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import base64
from PIL import Image
import time
import pdfkit
from Final_ARGUS_Thirdparty import query_rag, evaluate
from bs4 import BeautifulSoup
import numpy as np
import urllib.parse
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Page configuration
st.set_page_config(
    page_title="CyberGen ARGUS RAG Evaluation", 
    page_icon="🔍", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CyberGen color scheme
COLORS = {
    # Dark Mode Colors
    'dark': {
        'primary': '#131D41',       # Dark blue (main brand color)
        'secondary': '#2E5BFF',     # Bright blue (accent)
        'tertiary': '#1E3A8A',      # Mid blue
        'accent': '#27AE60',        # Green
        'background': '#0F172A',    # Very dark blue background
        'surface': '#1E293B',       # Dark blue card background
        'text': '#192026FF',          # Almost white text
        'text_secondary': '#545C69FF', # Lighter text for secondary elements
        'border': '#334155',        # Border color
        'error': '#EF4444',         # Red
    },
    # Light Mode Colors
    'light': {
        'primary': '#1E40AF',       # Strong blue (main brand color)
        'secondary': '#3B82F6',     # Bright blue (accent)
        'tertiary': '#2563EB',      # Mid blue
        'accent': '#10B981',        # Green
        'background': '#F1F5F9',    # Very light blue background
        'surface': '#FFFFFF',       # White card background
        'text': '#0F172A',          # Very dark blue text
        'text_secondary': '#64748B', # Medium gray-blue for secondary text
        'border': '#E2E8F0',        # Light border color
        'error': '#EF4444',         # Red
    }
}

# Add a session state for theme persistence if not already set
if 'theme_mode' not in st.session_state:
    st.session_state.theme_mode = 'light'  # Default to light mode

# Theme Selector in sidebar
with st.sidebar:
    st.title("Settings")
    selected_theme = st.radio(
        "Select Theme",
        options=["Light", "Dark"],
        index=0 if st.session_state.theme_mode == 'light' else 1,
        horizontal=True
    )
    
    # Update the session state based on selection
    if selected_theme == "Light" and st.session_state.theme_mode != 'light':
        st.session_state.theme_mode = 'light'
        st.rerun()
    elif selected_theme == "Dark" and st.session_state.theme_mode != 'dark':
        st.session_state.theme_mode = 'dark'
        st.rerun()

# Use the session state theme value
theme_mode = st.session_state.theme_mode
theme = COLORS[theme_mode]

# Custom CSS for theming
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    
    .main {{
        background: linear-gradient(135deg, 
            {theme['primary']} 0%,
            {theme['secondary']} 50%,
            {theme['tertiary']} 100%
        );
        background-attachment: fixed;
        color: {theme['text']};
        padding: 1rem;
        min-height: 100vh;
    }}
    
    /* Streamlit containers */
    .block-container {{
        max-width: 1200px;
        padding-top: 1rem;
        padding-bottom: 3rem;
        background: {theme['background']};
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }}
    
    /* Header styles */
    .stTitleContainer h1 {{
        color: {theme['primary']} !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
    }}
    
    /* Card styles */
    .custom-section {{
        background-color: {theme['surface']};
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
        margin-bottom: 1.5rem !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        overflow: hidden;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        display: flex;
        flex-direction: column;
        align-items: stretch;
        width: 100%;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    
    .custom-section:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
    }}
    
    /* Gradient banner styles */
    .gradient-banner {{
        background: linear-gradient(120deg, 
            {theme['primary']} 0%,
            {theme['secondary']} 50%,
            {theme['tertiary']} 100%
        );
        color: white;
        padding: 1.5rem;
        margin-bottom: 0 !important;
        box-shadow: none;
        border-radius: 8px 8px 0 0;
        width: 100%;
        position: relative;
        overflow: hidden;
    }}
    
    .gradient-banner::after {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, 
            rgba(255,255,255,0.1) 0%,
            rgba(255,255,255,0) 100%
        );
        pointer-events: none;
    }}
    
    /* Content padding container */
    .section-content {{
        padding: 1.5rem;
    }}
    
    /* Button styles */
    .stButton button {{
        background: linear-gradient(135deg, {theme['secondary']}, {theme['tertiary']}) !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s ease !important;
        width: 100%;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
    }}
    
    .stButton button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2) !important;
        background: linear-gradient(135deg, {theme['tertiary']}, {theme['secondary']}) !important;
    }}
    
    .stButton button::after {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, 
            rgba(255,255,255,0.1) 0%,
            rgba(255,255,255,0) 100%
        );
        pointer-events: none;
    }}
    
    /* Download button */
    .download-btn {{
        display: inline-block;
        background: linear-gradient(135deg, {theme['secondary']}, {theme['tertiary']});
        color: white;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 0.75rem 1.5rem;
        text-decoration: none;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin-bottom: 0.5rem;
        position: relative;
        overflow: hidden;
    }}
    
    .download-btn:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        background: linear-gradient(135deg, {theme['tertiary']}, {theme['secondary']});
    }}
    
    .download-btn::after {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, 
            rgba(255,255,255,0.1) 0%,
            rgba(255,255,255,0) 100%
        );
        pointer-events: none;
    }}
    
    /* Input styles */
    div[data-testid="stTextInput"] > div {{
        border-radius: 6px !important;
        border: 1px solid {theme['border']} !important;
        background-color: {theme['surface']} !important;
    }}
    
    div[data-testid="stTextInput"] > div:focus-within {{
        border-color: {theme['secondary']} !important;
        box-shadow: 0 0 0 2px rgba(46, 91, 255, 0.2) !important;
    }}
    
    /* Input text color */
    .stTextInput input {{
        color: {theme['text']} !important;
    }}
    
    /* Number Input */
    div[data-testid="stNumberInput"] > div {{
        border-radius: 6px !important;
        border: 1px solid {theme['border']} !important;
        background-color: {theme['surface']} !important;
    }}
    
    div[data-testid="stNumberInput"] input {{
        color: {theme['text']} !important;
    }}
    
    /* Chart styles */
    .stPlotlyChart {{
        background-color: transparent;
        border-radius: 0;
        padding: 0;
        box-shadow: none;
        border: none;
        margin-bottom: 1rem;
    }}
    
    /* Table styles */
    .dataframe {{
        font-family: 'Inter', sans-serif !important;
    }}
    
    .dataframe th {{
        background-color: {theme['primary']} !important;
        color: white !important;
        font-weight: 600 !important;
    }}
    
    /* DataTable */
    div[data-testid="stDataFrame"] > div {{
        background-color: {theme['surface']};
        border-radius: 8px;
        border: 1px solid {theme['border']};
        padding: 1rem;
    }}
    
    /* Success/Info/Warning/Error messages */
    .stAlert {{
        background-color: {theme['surface']} !important;
        border: 1px solid {theme['border']} !important;
        color: {theme['text']} !important;
    }}
    
    /* Progress bar container */
    div[data-testid="stProgressBar"] {{
        background-color: {theme['surface']};
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid {theme['border']};
    }}
    
    /* Animations */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    div[data-testid="stVerticalBlock"] {{
        animation: fadeIn 0.5s ease-out;
    }}
    
    /* Loading animation */
    .stSpinner > div {{
        border-top-color: {theme['secondary']} !important;
    }}
    
    /* Progress bar */
    div[role="progressbar"] > div {{
        background-color: {theme['secondary']} !important;
    }}
    
    /* For responsive layouts */
    @media screen and (max-width: 768px) {{
        .main {{
            padding: 0.5rem;
        }}
        
        .custom-section {{
            border-radius: 6px;
        }}
        
        .gradient-banner {{
            padding: 1rem;
        }}
        
        .download-btn {{
            width: 100%;
            margin-right: 0;
            margin-bottom: 0.75rem;
        }}
        
        .metric-card {{
            padding: 1rem;
        }}
        
        .html-table-wrapper th, 
        .html-table-wrapper td {{
            padding: 8px;   
            font-size: 0.85rem;
        }}
        
        .gradient-banner h2 {{
            font-size: 1.2rem;
        }}
    }}
    
    /* Add smooth scrolling */
    html {{
        scroll-behavior: smooth;
    }}
    
    /* Improved input labels */
    .stTextInput > label, 
    .stNumberInput > label {{
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 0.25rem;
        color: {theme['text_secondary']};
    }}
    
    /* Custom HTML table styles */
    .html-table-wrapper {{
        overflow-x: auto;
        margin-bottom: 1.5rem;
        background-color: {theme['surface']};
        border: 1px solid {theme['border']};
        border-radius: 8px;
    }}
    
    .html-table-wrapper table {{
        width: 100%;
        border-collapse: collapse;
        font-family: 'Inter', sans-serif;
    }}
    
    .html-table-wrapper th {{
        background-color: {theme['primary']};
        color: white;
        font-weight: 600;
        padding: 16px;
        text-align: left;
    }}
    
    .html-table-wrapper td {{
        padding: 16px;
        border-bottom: 1px solid {theme['border']};
        color: {theme['text']};
    }}
    
    .html-table-wrapper tr:nth-child(even) {{
        background-color: {('rgba(255,255,255,0.02)' if theme_mode=='dark' else 'rgba(0,0,0,0.02)')};
    }}
    
    /* Metric card styles */
    .metric-card {{
        background: linear-gradient(145deg, {theme['surface']}, {theme['background']});
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.1);
        height: 100%;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }}
    
    .metric-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.2);
        background: linear-gradient(145deg, {theme['surface']}, {theme['primary']});
    }}
    
    /* Custom section styles */
    .section-header {{
        color: {theme['primary']};
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {theme['border']};
    }}
    </style>
""", unsafe_allow_html=True)

# Helper functions
def get_base64_encoded_image(image_path):
    """Get base64 encoded image"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def get_image_html(image_path, width="180px"):
    """Get HTML for displaying image"""
    encoded_image = get_base64_encoded_image(image_path)
    return f'<img src="data:image/png;base64,{encoded_image}" width="{width}">'

def get_download_link(file_path, text, mime_type="text/html"):
    """Generate a download link for a file"""
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    download_filename = os.path.basename(file_path)
    href = f'<a href="data:{mime_type};base64,{b64}" download="{download_filename}" class="download-btn">{text}</a>'
    return href

def generate_csv(data, filename="rag_evaluation_results.csv"):
    """Generate CSV file from evaluation data"""
    df = pd.DataFrame([
        {"Query": d["user_input"], 
         "Response": d["response"], 
         "Reference": d["reference"]} 
        for d in data
    ])
    df.to_csv(filename, index=False)
    return filename

def generate_pdf_fallback(dataset, metrics, filename="rag_evaluation_results_fallback.pdf"):
    """Generate PDF using ReportLab (pure Python) as fallback when wkhtmltopdf is not available"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                           rightMargin=36, leftMargin=36,  # Reduce margins to allow more content width
                           topMargin=72, bottomMargin=72,
                           title="CyberGen ARGUS Evaluation Results")
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1  # Center alignment
    subtitle_style = styles['Heading2']
    subtitle_style.alignment = 1  # Center alignment
    subtitle_style.fontSize = 14
    
    # Create custom style for table cells with wordWrap
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,  # Line spacing
        wordWrap='CJK',  # Enable word wrapping
        allowWidows=1,
        allowOrphans=1
    )
    
    # Create content elements
    elements = []
    
    # Title
    elements.append(Paragraph("CyberGen ARGUS Evaluation Results", title_style))
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph("Advanced Retrieval Generation Unified System", subtitle_style))
    elements.append(Spacer(1, 0.5*inch))
    
    # Metrics section
    elements.append(Paragraph("Evaluation Metrics", styles['Heading2']))
    elements.append(Spacer(1, 0.1*inch))
    
    # Create metrics table
    metrics_data = [["Metric", "Score"]]
    for metric_name, value in metrics.items():
        metrics_data.append([metric_name, f"{value*100:.1f}%"])
    
    metrics_table = Table(metrics_data, colWidths=[3*inch, 1.5*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#131D41")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white])
    ]))
    
    elements.append(metrics_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Results section
    elements.append(Paragraph("Detailed Results", styles['Heading2']))
    elements.append(Spacer(1, 0.1*inch))
    
    # Prepare data for results table
    # Convert all strings to paragraphs to enable proper text wrapping
    results_data = [["Query", "Response", "Reference"]]
    for item in dataset:
        row = [
            Paragraph(item["user_input"], cell_style),
            Paragraph(item["response"], cell_style),
            Paragraph(item["reference"], cell_style)
        ]
        results_data.append(row)
    
    # Calculate column widths based on available space
    table_width = doc.width
    col_widths = [table_width * 0.25, table_width * 0.375, table_width * 0.375]
    
    # Create the table with the data
    results_table = Table(results_data, colWidths=col_widths, repeatRows=1)
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#131D41")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white])
    ]))
    
    elements.append(results_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Footer
    footer_text = "Generated by CyberGen ARGUS Evaluation System\n© 2023 CyberGen. All rights reserved."
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        alignment=1,  # Center alignment
        textColor=colors.gray,
        fontSize=9
    )
    elements.append(Paragraph(footer_text, footer_style))
    
    # Build document
    doc.build(elements)
    
    # Save the PDF
    with open(filename, 'wb') as f:
        f.write(buffer.getvalue())
    
    return filename

def try_generate_pdf(html_path, pdf_path):
    """Try to generate PDF from HTML, return success status"""
    try:
        # First try with wkhtmltopdf
        config = pdfkit.configuration()
        options = {
            'page-size': 'A4',
            'margin-top': '1cm',
            'margin-right': '1cm',
            'margin-bottom': '1cm',
            'margin-left': '1cm',
            'encoding': 'UTF-8',
            'no-outline': None,
            'title': 'CyberGen ARGUS Evaluation Results'
        }
        pdfkit.from_file(html_path, pdf_path, options=options, configuration=config)
        return True, pdf_path
    except Exception as e:
        st.warning(f"Could not generate PDF with wkhtmltopdf: {str(e)}")
        st.info("Using fallback PDF generator instead.")
        # This will be handled downstream, where we'll use the fallback method
        return False, None

# Display CyberGen logo and header in a more contained design
st.markdown("""
<div class="custom-section">
    <div style="display: flex; align-items: center; padding: 1.5rem;">
        <div style="flex: 0 0 auto; margin-right: 1.5rem;">
""", unsafe_allow_html=True)

try:
    logo_path = "assets/cybergen-logo-light.png"
    st.markdown(get_image_html(logo_path, width="120px"), unsafe_allow_html=True)
except Exception as e:
    st.error(f"Logo not found: {str(e)}. Please ensure it exists in the assets folder.")

st.markdown("""
        </div>
        <div>
            <h1 style="margin: 0; padding: 0; font-size: 1.8rem;">ARGUS RAG Evaluation System</h1>
            <p style="margin: 0; padding: 0; color: var(--text-secondary); font-size: 1rem;">Advanced Retrieval Generation Unified System</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main content container
main_container = st.container()

with main_container:
    # Create a custom container for all content
    st.markdown('<div class="custom-section">', unsafe_allow_html=True)
    
    # Banner with gradient - now inside the custom section
    st.markdown("""
    <div class="gradient-banner">
        <h2 style="margin:0; font-weight: 600; color: white; font-size: 1.4rem;">Evaluate Your RAG System</h2>
        <p style="margin-top: 5px; opacity: 0.9;">Enter your API endpoint and generate comprehensive evaluation reports.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Configuration section in a card - now with internal padding
    st.markdown('<div class="section-content">', unsafe_allow_html=True)
    st.markdown('<h3 class="section-header">Configure Evaluation</h3>', unsafe_allow_html=True)
    
    # Get API endpoint from user
    api_endpoint = st.text_input(
        "RAG API Endpoint", 
        value="http://10.229.222.15:8000/knowledgebase",
        help="Enter the base URL of your RAG API"
    )
    
    col1, col2 = st.columns([1, 1])
    with col1:
        group_id = st.number_input("Group ID", value=12, min_value=1, help="Enter the group ID for the RAG system")
    with col2:
        session_id = st.number_input("Session ID", value=111, min_value=1, help="Enter the session ID for the RAG system")
    
    # Only show the run button if an endpoint is provided
    if api_endpoint:
        if st.button("Run Evaluation", use_container_width=True):
            with st.spinner("Running evaluation... This may take a minute."):
                try:
                    # Create a progress bar
                    progress_bar = st.progress(0)
                    
                    # Import these variables from the module
                    from Final_ARGUS_Thirdparty import sample_queries, expected_responses
                    
                    # Clear previous results if they exist
                    if os.path.exists("rag_evaluation_results.html"):
                        os.remove("rag_evaluation_results.html")
                    if os.path.exists("rag_evaluation_results.pdf"):
                        os.remove("rag_evaluation_results.pdf")
                    if os.path.exists("rag_evaluation_results.csv"):
                        os.remove("rag_evaluation_results.csv")
                    
                    # Update BASE_RAG_ENDPOINT in the module
                    import Final_ARGUS_Thirdparty
                    Final_ARGUS_Thirdparty.BASE_RAG_ENDPOINT = api_endpoint
                    
                    # Initialize result tracking
                    dataset = []
                    
                    # Process each query
                    for i, (query, reference) in enumerate(zip(sample_queries, expected_responses)):
                        # Update progress
                        progress_bar.progress((i + 1) / len(sample_queries))
                        
                        # Encode the query for URL safety
                        encoded_query = urllib.parse.quote(query)
                        
                        # Run query
                        response = query_rag(encoded_query, group_id=group_id, session_id=session_id)
                        
                        # Ensure retrieved_contexts is always a list
                        response_list = [response] if isinstance(response, str) else response
                        
                        # Add to dataset
                        dataset.append({
                            "user_input": query,
                            "retrieved_contexts": response_list,
                            "response": response,
                            "reference": reference
                        })
                        
                        # Small delay for visual effect
                        time.sleep(0.3)
                    
                    # Create DataFrame
                    eval_data = pd.DataFrame(dataset)
                    
                    # Generate HTML report with more sophisticated design
                    html_content = """
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>CyberGen ARGUS Evaluation Results</title>
                        <style>
                            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
                            
                            :root {
                                --primary: #131D41;
                                --secondary: #2E5BFF;
                                --accent: #27AE60;
                                --background: #F5F7FA;
                                --text: #1A1A1A;
                                --light-text: #666;
                                --border: #E0E0E0;
                            }
                            
                            * {
                                margin: 0;
                                padding: 0;
                                box-sizing: border-box;
                            }
                            
                            body { 
                                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; 
                                background-color: var(--background);
                                color: var(--text);
                                line-height: 1.6;
                            }
                            
                            .container {
                                max-width: 1200px;
                                margin: 0 auto;
                                padding: 40px 20px;
                            }
                            
                            .header {
                                display: flex;
                                flex-direction: column;
                                align-items: center;
                                margin-bottom: 40px;
                                text-align: center;
                            }
                            
                            .logo {
                                max-width: 180px;
                                margin-bottom: 20px;
                            }
                            
                            h1 { 
                                font-size: 32px;
                                font-weight: 700;
                                color: var(--primary);
                                margin-bottom: 10px;
                            }
                            
                            h2 {
                                font-size: 24px;
                                font-weight: 600;
                                color: var(--primary);
                                margin: 30px 0 20px 0;
                            }
                            
                            .subtitle {
                                font-size: 18px;
                                color: var(--light-text);
                                margin-bottom: 30px;
                            }
                            
                            .banner {
                                background: linear-gradient(120deg, var(--primary), var(--secondary));
                                color: white;
                                padding: 30px;
                                border-radius: 10px;
                                margin-bottom: 40px;
                                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                            }
                            
                            .banner h2 {
                                color: white;
                                margin-top: 0;
                            }
                            
                            .metrics {
                                display: flex;
                                justify-content: space-between;
                                flex-wrap: wrap;
                                gap: 20px;
                                margin-bottom: 40px;
                            }
                            
                            .metric-card {
                                flex: 1;
                                min-width: 200px;
                                background: white;
                                border-radius: 10px;
                                padding: 25px 20px;
                                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                                text-align: center;
                                transition: transform 0.3s ease;
                            }
                            
                            .metric-card:hover {
                                transform: translateY(-5px);
                            }
                            
                            .metric-value {
                                font-size: 36px;
                                font-weight: 700;
                                color: var(--secondary);
                                margin: 10px 0;
                            }
                            
                            .metric-label {
                                font-size: 16px;
                                color: var(--light-text);
                                font-weight: 500;
                            }
                            
                            .table-container {
                                background: white;
                                border-radius: 10px;
                                overflow: hidden;
                                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                                margin-bottom: 40px;
                            }
                            
                            table { 
                                width: 100%; 
                                border-collapse: collapse; 
                            }
                            
                            th, td { 
                                padding: 16px; 
                                text-align: left; 
                            }
                            
                            th { 
                                background-color: var(--primary); 
                                color: white; 
                                font-weight: 600;
                                font-size: 16px;
                            }
                            
                            td {
                                border-bottom: 1px solid var(--border);
                            }
                            
                            tr:last-child td {
                                border-bottom: none;
                            }
                            
                            tr:nth-child(even) {
                                background-color: rgba(0,0,0,0.02);
                            }
                            
                            .footer {
                                margin-top: 60px;
                                text-align: center;
                                color: var(--light-text);
                                font-size: 14px;
                                border-top: 1px solid var(--border);
                                padding-top: 30px;
                            }
                            
                            .footer p {
                                margin: 5px 0;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <div class="header">
                                <h1>CyberGen ARGUS Evaluation Results</h1>
                                <div class="subtitle">Advanced Retrieval Generation Unified System</div>
                            </div>
                            
                            <div class="banner">
                                <h2>Evaluation Summary</h2>
                                <p>Comprehensive analysis of RAG system performance across key metrics.</p>
                            </div>
                            
                            <div class="metrics">
                    """
                    
                    # Get evaluation metrics
                    metrics = evaluate(dataset)
                    
                    # Add metrics to HTML
                    for metric_name, value in metrics.items():
                        html_content += f"""
                            <div class="metric-card">
                                <div class="metric-label">{metric_name}</div>
                                <div class="metric-value">{value*100:.1f}%</div>
                            </div>
                        """
                    
                    html_content += """
                            </div>
                            
                            <h2>Detailed Results</h2>
                            <div class="table-container">
                                <table>
                                    <tr>
                                        <th>User Query</th>
                                        <th>Generated Response</th>
                                        <th>Reference Answer</th>
                                    </tr>
                    """
                    
                    # Add result rows
                    for data in dataset:
                        html_content += f"""
                            <tr>
                                <td style="padding: 16px; text-align: left; border-bottom: 1px solid var(--border); vertical-align: top; word-wrap: break-word;">{data["user_input"]}</td>
                                <td style="padding: 16px; text-align: left; border-bottom: 1px solid var(--border); vertical-align: top; word-wrap: break-word;">{data["response"]}</td>
                                <td style="padding: 16px; text-align: left; border-bottom: 1px solid var(--border); vertical-align: top; word-wrap: break-word;">{data["reference"]}</td>
                            </tr>
                        """
                    
                    # Close HTML
                    html_content += """
                                </table>
                            </div>
                            
                            <div class="footer">
                                <p>Generated by CyberGen ARGUS Evaluation System</p>
                                <p>© 2023 CyberGen. All rights reserved.</p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    
                    # Write HTML file
                    html_path = "rag_evaluation_results.html"
                    with open(html_path, "w", encoding="utf-8") as file:
                        file.write(html_content)
                    
                    # Generate CSV file
                    csv_path = generate_csv(dataset)
                    
                    # Try to generate PDF with wkhtmltopdf
                    pdf_path = "rag_evaluation_results.pdf"
                    pdf_generated, pdf_file = try_generate_pdf(html_path, pdf_path)
                    
                    # If wkhtmltopdf fails, use fallback method
                    if not pdf_generated:
                        pdf_path = generate_pdf_fallback(dataset, metrics)
                        pdf_generated = True  # We're sure the fallback method works
                    
                    # Complete the progress bar
                    progress_bar.progress(100)
                    
                    # Display success message with animation
                    st.success("Evaluation completed successfully!")
                    
                    # Create a container for results
                    st.markdown('<div class="custom-section">', unsafe_allow_html=True)
                    
                    # Create visuals
                    st.markdown("""
                    <div class="gradient-banner">
                        <h2 style="margin:0; font-weight: 600; color: white; font-size: 1.4rem;">Evaluation Results</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Add an inner div with padding for content
                    st.markdown('<div class="section-content">', unsafe_allow_html=True)
                    
                    # Display metrics cards
                    metrics_cols = st.columns(len(metrics))
                    for i, (metric_name, value) in enumerate(metrics.items()):
                        with metrics_cols[i]:
                            st.markdown(f"""
                            <div style="background-color: {theme['surface']}; border-radius: 8px; padding: 25px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); transition: transform 0.3s ease; border: 1px solid {theme['border']};" onmouseover="this.style.transform='scale(1.03)';" onmouseout="this.style.transform='scale(1.0)';">
                                <p style="color: {theme['text_secondary']}; font-size: 1rem; margin-bottom: 5px; font-weight: 500;">{metric_name}</p>
                                <h2 style="color: {theme['secondary']}; font-size: 2.5rem; font-weight: 700; margin: 0;">{value*100:.1f}%</h2>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Create a chart for visualization
                    st.subheader("Performance Visualization")
                    
                    col1, col2 = st.columns([3, 2])
                    
                    with col1:
                        # Create a gauge chart for each metric
                        for metric_name, value in metrics.items():
                            fig = go.Figure(go.Indicator(
                                mode="gauge+number",
                                value=value * 100,
                                title={'text': metric_name, 'font': {'size': 16, 'color': theme['primary']}},
                                gauge={
                                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': theme['primary']},
                                    'bar': {'color': theme['secondary']},
                                    'bgcolor': theme['surface'],
                                    'borderwidth': 0,
                                    'steps': [
                                        {'range': [0, 50], 'color': '#1E293B' if theme_mode == 'dark' else '#F0F0F0'},
                                        {'range': [50, 75], 'color': '#334155' if theme_mode == 'dark' else '#E0E0E0'},
                                        {'range': [75, 100], 'color': '#475569' if theme_mode == 'dark' else '#D0D0D0'}
                                    ],
                                }
                            ))
                            
                            fig.update_layout(
                                height=200,
                                margin=dict(l=30, r=30, t=50, b=20),
                                paper_bgcolor='rgba(0,0,0,0)',
                                font={'family': 'Inter, sans-serif', 'color': theme['text']}
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Create a radar chart
                        fig = go.Figure()
                        
                        # Convert hex color to RGB for transparency
                        secondary_hex = theme['secondary'].lstrip('#')
                        secondary_rgb = tuple(int(secondary_hex[i:i+2], 16) for i in (0, 2, 4))
                        
                        accent_hex = theme['accent'].lstrip('#')
                        accent_rgb = tuple(int(accent_hex[i:i+2], 16) for i in (0, 2, 4))
                        
                        fig.add_trace(go.Scatterpolar(
                            r=[value * 100 for value in metrics.values()],
                            theta=list(metrics.keys()),
                            fill='toself',
                            name='Current Evaluation',
                            line_color=theme['secondary'],
                            fillcolor=f'rgba({secondary_rgb[0]}, {secondary_rgb[1]}, {secondary_rgb[2]}, 0.2)'
                        ))
                        
                        # Add a reference baseline at 90%
                        fig.add_trace(go.Scatterpolar(
                            r=[90 for _ in metrics.values()],
                            theta=list(metrics.keys()),
                            fill='toself',
                            name='Benchmark',
                            line_color=theme['accent'],
                            fillcolor=f'rgba({accent_rgb[0]}, {accent_rgb[1]}, {accent_rgb[2]}, 0.1)'
                        ))
                        
                        fig.update_layout(
                            polar=dict(
                                radialaxis=dict(
                                    visible=True,
                                    range=[0, 100]
                                )
                            ),
                            showlegend=True,
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=-0.2,
                                xanchor="center",
                                x=0.5
                            ),
                            height=400,
                            margin=dict(l=80, r=80, t=20, b=50),
                            paper_bgcolor='rgba(0,0,0,0)'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Display detailed results
                    st.subheader("Detailed Results")
                    
                    # Create custom HTML table instead of using dataframe
                    results_html = """
                    <div class="html-table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th style="width: 25%;">Query</th>
                                    <th style="width: 37.5%;">Response</th>
                                    <th style="width: 37.5%;">Reference</th>
                                </tr>
                            </thead>
                            <tbody>
                    """
                    
                    # Add rows with data
                    for i, d in enumerate(dataset):
                        # Add zebra striping
                        bg_color = "#f5f5f5" if i % 2 == 0 else "white"
                        
                        # Escape HTML
                        query = d["user_input"].replace("<", "&lt;").replace(">", "&gt;")
                        response = d["response"].replace("<", "&lt;").replace(">", "&gt;")
                        reference = d["reference"].replace("<", "&lt;").replace(">", "&gt;")
                        
                        results_html += f"""
                            <tr style="background-color: {bg_color};">
                                <td style="padding: 12px 15px; text-align: left; border-bottom: 1px solid #e0e0e0; vertical-align: top; word-wrap: break-word;">{query}</td>
                                <td style="padding: 12px 15px; text-align: left; border-bottom: 1px solid #e0e0e0; vertical-align: top; word-wrap: break-word;">{response}</td>
                                <td style="padding: 12px 15px; text-align: left; border-bottom: 1px solid #e0e0e0; vertical-align: top; word-wrap: break-word;">{reference}</td>
                            </tr>
                        """
                    
                    results_html += """
                            </tbody>
                        </table>
                    </div>
                    """
                    
                    # Display the custom HTML table
                    st.markdown(results_html, unsafe_allow_html=True)
                    
                    # Display downloads section within the same container
                    st.markdown("""
                    <div style="margin-top: 2rem;">
                        <h3 class="section-header">Download Reports</h3>
                        <p style="margin-bottom: 1.5rem;">Export evaluation results in your preferred format:</p>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <div style="font-weight: 600; margin-bottom: 0.8rem;">Primary Report Format</div>
                    """, unsafe_allow_html=True)
                    
                    # First emphasize the PDF download (now always available)
                    st.markdown(get_download_link(pdf_path, "📄 Download PDF Report", "application/pdf"), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Then show other formats
                    st.markdown("""
                    <div style="margin-top: 10px;">
                        <div style="font-weight: 600; margin-bottom: 10px;">Alternative Formats</div>
                        <div style="display: flex; gap: 15px; flex-wrap: wrap;">
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(get_download_link(html_path, "Download HTML Report", "text/html"), unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(get_download_link(csv_path, "Download CSV Data", "text/csv"), unsafe_allow_html=True)
                    
                    st.markdown("</div></div>", unsafe_allow_html=True)
                    
                    # Close the inner padding div
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Close the container
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Error during evaluation: {str(e)}")
                    st.info("Make sure the RAG API endpoint is accessible and properly configured.")
    else:
        st.warning("Please enter a valid API endpoint to continue.")
    
    # Close the internal padding div
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Close the custom-section container
    st.markdown('</div>', unsafe_allow_html=True)

# Footer with animation
st.markdown("""
<div class="custom-section" style="margin-top: 3rem;">
    <div class="section-content" style="text-align: center;">
        <p style="font-size: 0.9rem; margin-bottom: 0.5rem; color: var(--text-secondary);">© 2023 CyberGen. All rights reserved.</p>
        <p style="font-size: 0.8rem; color: var(--text-secondary);">ARGUS - Advanced Retrieval Generation Unified System</p>
    </div>
</div>
""", unsafe_allow_html=True) 
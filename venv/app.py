import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import google.generativeai as genai

# --- Page & VADER Setup ---
st.set_page_config(
    page_title="Portfolio Analysis Engine",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)
analyzer = SentimentIntensityAnalyzer()

# --- Data Fetching & Processing Functions ---
@st.cache_data
def get_stock_data(ticker, keywords):
    """Fetches and processes data for a single stock ticker."""
    stock = yf.Ticker(ticker)
    info = stock.info
    headlines = fetch_headlines(ticker)
    theme_score = calculate_theme_score_simple(headlines, keywords)
    current_esg_proxy = calculate_esg_proxy(fetch_headlines(ticker, years_ago=0))
    last_year_esg_proxy = calculate_esg_proxy(fetch_headlines(ticker, years_ago=1))
    return {'Ticker': ticker, 'Company Name': info.get('longName', 'N/A'), 'Sector': info.get('sector', 'N/A'),
            'Market Cap': info.get('marketCap', 0), 'Current ESG Proxy': current_esg_proxy,
            'Last Year ESG Proxy': last_year_esg_proxy, 'Thematic Score': theme_score}

@st.cache_data
def fetch_headlines(ticker, years_ago=0):
    """Fetches news headlines."""
    current_year = datetime.now().year
    start_year = current_year - years_ago
    url = f"https://news.google.com/search?q={ticker} stock after:{start_year}-01-01 before:{start_year}-12-31&hl=en-US"
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        return [a.text for a in soup.find_all('a', class_='JtKRv')][:30]
    except Exception:
        return []

def calculate_theme_score_simple(headlines, keywords):
    """Calculates theme relevance score."""
    if not headlines or not keywords: return 0
    score, text = 0, ' '.join(headlines).lower()
    for keyword in keywords: score += text.count(keyword.strip())
    return (score / len(headlines)) * 100

def calculate_esg_proxy(headlines):
    """Calculates ESG proxy score from sentiment."""
    if not headlines: return None
    scores = [analyzer.polarity_scores(h)['compound'] for h in headlines]
    return (sum(scores) / len(scores) + 1) * 50

def generate_mri_report(df, keywords):
    """Generates a portfolio analysis report using the Google Gemini API."""
    # Access the API key from Streamlit's secrets
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    prompt_summary = f"""
    Analyze the following stock portfolio based on the provided data. The user has defined a custom theme: '{', '.join(keywords)}'.
    The ESG Proxy score is derived from news sentiment (0-100, 50 is neutral).
    The Thematic Score measures relevance to the custom theme (0-100).
    The analysis was conducted on {datetime.now().strftime('%Y-%m-%d')} from Hubballi, India.

    Here is the portfolio data in CSV format:
    {df.to_csv(index=False)}

    Please act as a professional financial analyst. Generate a concise "Portfolio MRI" (Management & Risk Insights) report.
    Structure your response using Markdown with the following three sections exactly:

    ### 1. Key Thematic Opportunity
    (Identify the single most significant strength or opportunity related to the portfolio's alignment with the custom theme. Be specific.)

    ### 2. Primary Unseen Risk
    (Identify the most significant underlying risk. This could be concentration in one stock, a low ESG score in a key holding, or a sector-wide issue. Be specific.)

    ### 3. Actionable Insights for Further Research
    (Provide 2-3 concrete, forward-looking questions or points for a portfolio manager to investigate. These should NOT be 'buy' or 'sell' recommendations. Frame them as suggestions for deeper due diligence.)
    """
    try:
        response = model.generate_content(prompt_summary)
        return response.text
    except Exception as e:
        return f"An error occurred while contacting the Google AI API: {e}"

# --- UI Sidebar ---
with st.sidebar:
    st.title("🔬 Portfolio Analyzer")
    st.markdown("---")
    st.header("⚙️ Analysis Controls")
    
    with st.form(key="controls_form"):
        uploaded_file = st.file_uploader("Upload Portfolio CSV", type="csv")
        custom_keywords_input = st.text_area("Theme Keywords", "ai, artificial intelligence, machine learning, llm, generative, nvidia")
        run_button = st.form_submit_button(label="🚀 Run Analysis", use_container_width=True)

# --- Main UI Panel ---
st.title("Portfolio Intelligence Dashboard")
st.markdown("An interactive tool for thematic and ESG-proxy analysis.")
st.markdown("---")

# Logic to run analysis and display results
if uploaded_file and run_button:
    st.cache_data.clear()
    keywords = [k.lower().strip() for k in custom_keywords_input.split(',')]
    portfolio_df = pd.read_csv(uploaded_file)
    
    if 'Ticker' not in portfolio_df.columns or 'Weight' not in portfolio_df.columns:
        st.error("Invalid CSV. 'Ticker' and 'Weight' columns required.")
    else:
        st.subheader("Uploaded Portfolio Composition")
        st.dataframe(portfolio_df)
        st.markdown("---")
        
        progress_bar = st.progress(0, "Starting Analysis...")
        all_stock_data = []
        for i, ticker in enumerate(portfolio_df['Ticker']):
            progress_bar.progress((i + 1) / len(portfolio_df), f"Analyzing {ticker}...")
            try:
                all_stock_data.append(get_stock_data(ticker, keywords))
            except Exception as e:
                st.warning(f"Could not process {ticker}. Error: {e}")
        progress_bar.empty()
        
        if not all_stock_data:
            st.error("Analysis failed for all tickers.")
        else:
            results_df = pd.DataFrame(all_stock_data)
            st.session_state.final_df = pd.merge(portfolio_df, results_df, on='Ticker')
            st.session_state.keywords = keywords

if 'final_df' in st.session_state:
    final_df = st.session_state.final_df
    
    # --- Results Display ---
    st.header("📊 Executive Summary")
    final_df['Weighted Thematic'] = final_df['Thematic Score'] * final_df['Weight']
    final_df_esg = final_df.dropna(subset=['Current ESG Proxy', 'Last Year ESG Proxy'])
    portfolio_thematic_score = final_df['Weighted Thematic'].sum()
    if not final_df_esg.empty:
        current_esg = (final_df_esg['Current ESG Proxy'] * final_df_esg['Weight']).sum()
        last_year_esg = (final_df_esg['Last Year ESG Proxy'] * final_df_esg['Weight']).sum()
        esg_drift = current_esg - last_year_esg
    else:
        current_esg, esg_drift = "N/A", "N/A"
    
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        c1.metric("Portfolio Thematic Score", f"{portfolio_thematic_score:.2f}")
        c2.metric("Portfolio ESG Proxy Score", f"{current_esg:.2f}" if isinstance(current_esg, float) else "N/A")
        c3.metric("1-Year ESG Proxy Drift", f"{esg_drift:+.2f}" if isinstance(esg_drift, float) else "N/A")

    st.subheader("📄 Detailed Holdings Analysis")
    st.dataframe(final_df.style.format(formatter={
        'Weight': '{:.2%}', 'Market Cap': '{:,.0f}', 'Current ESG Proxy': '{:.2f}',
        'Last Year ESG Proxy': '{:.2f}', 'Thematic Score': '{:.2f}'
    }, na_rep="N/A").background_gradient(cmap='RdYlGn', subset=['Current ESG Proxy', 'Thematic Score']))
    
    st.markdown("---")
    
    st.header("🤖 AI-Powered Portfolio MRI")
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("Google AI API Key not found. Please add it to your .streamlit/secrets.toml file.")
    else:
        if st.button("Generate MRI Report", use_container_width=True, type="primary"):
            with st.spinner("🧠 The AI is analyzing your portfolio... Please wait."):
                report = generate_mri_report(final_df, st.session_state.keywords)
                st.session_state.report = report

    if 'report' in st.session_state:
        with st.container(border=True):
            st.markdown(st.session_state.report)
    
    st.markdown("---")
    
    st.header("🔬 Visual Deep Dive")
    tab1, tab2, tab3 = st.tabs(["🌐 Portfolio Landscape (Bubble Chart)", "🤖 Thematic Analysis (Bar Chart)", "🌱 ESG Analysis (Bar Chart)"])
    with tab1:
        st.info("💡 This chart shows your portfolio's landscape. Position shows Thematic/ESG scores, size shows portfolio weight, and color shows the sector.")
        plot_df = final_df.dropna(subset=['Current ESG Proxy', 'Thematic Score', 'Market Cap', 'Sector'])
        if not plot_df.empty:
            fig_bubble = px.scatter(
                plot_df, x="Thematic Score", y="Current ESG Proxy", size="Weight", color="Sector",
                hover_name="Company Name", size_max=60, title="Portfolio Landscape: ESG vs. Thematic Score"
            )
            st.plotly_chart(fig_bubble, use_container_width=True)
        else: st.warning("Not enough data to generate landscape chart.")
    with tab2:
        fig_theme = px.bar(final_df, x='Ticker', y='Thematic Score', color='Thematic Score',
                           title='Theme Relevance Score by Holding', color_continuous_scale=px.colors.sequential.Greens)
        st.plotly_chart(fig_theme, use_container_width=True)
    with tab3:
        esg_df = final_df.dropna(subset=['Current ESG Proxy', 'Last Year ESG Proxy'])
        if not esg_df.empty:
            fig_esg = go.Figure()
            fig_esg.add_trace(go.Bar(x=esg_df['Ticker'], y=esg_df['Last Year ESG Proxy'], name='Last Year Proxy'))
            fig_esg.add_trace(go.Bar(x=esg_df['Ticker'], y=esg_df['Current ESG Proxy'], name='Current Proxy'))
            fig_esg.update_layout(barmode='group', title='ESG Proxy Score: Current vs. Last Year')
            st.plotly_chart(fig_esg, use_container_width=True)
        else: st.warning("Not enough data to generate ESG drift chart.")

elif not run_button and not uploaded_file:
    st.info("To begin, upload a portfolio CSV and click 'Run Analysis' in the sidebar.")
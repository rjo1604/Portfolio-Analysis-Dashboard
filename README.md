# Portfolio Intelligence Dashboard 🔬

An interactive dashboard for thematic and AI-driven ESG analysis of stock portfolios. This project was built as a prototype to showcase modern data application development, creative problem-solving for data gaps, and the integration of Large Language Models (LLMs) for decision support, inspired by the analytical tools used at leading financial firms like MSCI.

---

### 🔮 Live Application Preview

![portfolio analysis engine](https://github.com/user-attachments/assets/f99213a0-096a-4a75-aed9-83f5ba43ca2c)


---

### ✨ Core Features

This application goes beyond simple data display to provide deep, actionable insights:

* **Dynamic Thematic Analysis:** Users can define their own investment themes (e.g., "AI", "Renewable Energy", "Cybersecurity") by entering custom keywords. The app then scrapes real-time news to score each stock's relevance to that theme.
* **AI-Powered ESG Proxy:** Solves the real-world problem of unavailable historical ESG data. The app uses the VADER sentiment analysis model to score news headlines from current and past years, creating a justifiable proxy for a company's ESG standing and tracking its "drift" over time.
* **Interactive Visualizations:** The portfolio is visualized through a series of Plotly charts, including:
    * A **2D Bubble Chart** mapping the entire portfolio landscape across Thematic and ESG scores.
    * Bar charts for deep-diving into individual stock performance.
* **AI-Generated Insights (Portfolio MRI):** After the quantitative analysis is complete, the user can generate a "Management & Risk Insights" report using the **Google Gemini API**. The LLM acts as a financial analyst, providing a narrative summary of the portfolio's key opportunities, unseen risks, and actionable next steps for further research.
* **Secure & Professional Backend:**
    * API keys are handled securely using Streamlit's built-in secrets management (`secrets.toml`) and are never exposed on the front end.
    * A professional dark theme is enforced for a modern, focused user experience.
    * All data fetching is cached to ensure a fast and responsive UI.

### 🛠️ Tech Stack

* **Frontend:** Streamlit
* **Data Analysis & Manipulation:** Pandas, NumPy
* **Data Fetching:** yfinance (Financial Data), Requests/BeautifulSoup (News Scraping)
* **NLP/Sentiment Analysis:** VaderSentiment
* **AI/LLM Integration:** Google Gemini API (`google-generativeai`)
* **Visualization:** Plotly, Matplotlib (for table styling)
* **Language:** Python 3.10+

---

### 🚀 How to Run Locally

To run this application on your local machine, please follow these steps:

**1. Prerequisites:**
* Python 3.8 or higher
* Git

**2. Clone the Repository:**
```bash
git clone https://github.com/rjo1604/Portfolio-Analysis-Dashboard.git
cd Portfolio-Analysis-Dashboard
```

**3. Set Up the Environment:**
* Create and activate a Python virtual environment:
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```
* Install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```

**4. Configure Your API Key (Crucial Step):**
* In the project directory, create a new folder named `.streamlit`.
* Inside the `.streamlit` folder, create a new file named `secrets.toml`.
* Add your Google AI API key to this file in the following format:
    ```toml
    GOOGLE_API_KEY = "YOUR_API_KEY_HERE"
    ```

**5. Run the Application:**
```bash
streamlit run app.py
```
The application should now be running in your browser!

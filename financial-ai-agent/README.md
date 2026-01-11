# 📊 Financial AI Agent

An AI-powered financial analysis platform built with Groq Llama 3.3 70B and Streamlit. This application provides comprehensive investment research capabilities including PDF earnings analysis, company performance evaluation, and research recommendations.

## 🚀 Features

- **📄 PDF Earnings Analysis**: Upload and analyze quarterly/annual earnings reports with automatic metric extraction
- **💼 Company Analysis**: Get detailed performance analysis with BUY/HOLD/SELL recommendations
- **🔍 Research Recommendations**: Receive curated sources for building investment conviction
- **📈 Interactive Visualizations**: Dynamic charts showing financial trends and metrics
- **🤖 Multi-Agent Architecture**: Specialized agents for different analysis types

## 📁 Project Structure

```
financial-ai-agent/
├── app.py                      # Main Streamlit application
├── agents/                     # AI agent modules
│   ├── __init__.py
│   ├── orchestrator.py        # Request routing and intent classification
│   ├── pdf_analyzer.py        # PDF earnings report analysis
│   ├── company_analyzer.py    # Company performance analysis
│   └── research_recommender.py # Research source recommendations
├── tools/                      # Utility tools
│   ├── __init__.py
│   ├── pdf_processor.py       # PDF processing utilities
│   ├── web_search.py          # Web search integration (optional)
│   └── data_fetcher.py        # Financial data API integration (placeholder)
├── storage/                    # Data storage
│   ├── __init__.py
│   ├── cache.py               # Response caching
│   └── vector_store.py        # Vector database (placeholder)
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
└── README.md                   # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Groq API key

### Setup Steps

1. **Clone or create the project directory**
```bash
mkdir financial-ai-agent
cd financial-ai-agent
```

2. **Create and activate virtual environment**
```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create .env file**
```bash
echo "GROQ_API_KEY=your_api_key_here" > .env
```

Or create `.env` manually:
```
GROQ_API_KEY=your_api_key_here
```

5. **Run the application**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### 1. Company Analysis
Select "💼 Company Analysis" mode and ask about any publicly traded company:

```
Example queries:
- "Analyze Apple's current performance and give me a recommendation"
- "Should I invest in Microsoft right now?"
- "Compare Google and Amazon as investments"
```

**Output includes:**
- Company overview and recent performance
- Financial health score
- Bull and bear cases
- Clear BUY/HOLD/SELL recommendation
- Key catalysts and risks

### 2. PDF Report Analysis
Select "📄 PDF Report Analysis" mode, upload an earnings PDF, and ask for analysis:

```
Steps:
1. Click "Upload Earnings PDF" in sidebar
2. Select your PDF file (quarterly or annual report)
3. Enter query: "Analyze this earnings report comprehensively"
4. Click "Analyze"
```

**Output includes:**
- Executive summary
- Key financial metrics (revenue, EPS, margins)
- Performance highlights
- Forward guidance
- Investment recommendation
- Interactive charts

### 3. Research Recommendations
Select "🔍 Research Guide" mode to get curated research sources:

```
Example queries:
- "What sources should I review to build conviction on Tesla?"
- "How do I research semiconductor companies?"
```

**Output includes:**
- Primary sources (SEC filings, IR materials)
- Market data sources
- News outlets to monitor
- Alternative data sources
- Research timeline

### 4. General Chat
Select "💬 General Chat" for general financial questions:

```
Example queries:
- "How do I read a 10-K filing?"
- "What's a good P/E ratio for tech companies?"
```

## 🎯 Architecture

### Agent System
The application uses a multi-agent architecture:

```
User Query → Orchestrator → Intent Classification
                ↓
         Route to Specialist Agent:
         - PDF Analyzer
         - Company Analyzer
         - Research Recommender
                ↓
         Process & Return Response
```

### Key Components

1. **Orchestrator** (`agents/orchestrator.py`)
   - Classifies user intent
   - Routes to appropriate specialist agent
   - Handles general queries

2. **PDF Analyzer** (`agents/pdf_analyzer.py`)
   - Processes earnings reports
   - Extracts financial metrics
   - Generates recommendations

3. **Company Analyzer** (`agents/company_analyzer.py`)
   - Analyzes company performance
   - Provides investment thesis
   - Generates BUY/HOLD/SELL ratings

4. **Research Recommender** (`agents/research_recommender.py`)
   - Curates research sources
   - Creates research roadmaps
   - Suggests due diligence steps

## 🔧 Configuration

### Environment Variables
Create a `.env` file with:
```
GROQ_API_KEY=your_api_key_here
```

### Streamlit Configuration (Optional)
Create `.streamlit/config.toml` to customize the UI:
```toml
[theme]
primaryColor = "#1e88e5"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

## 📊 Example Workflows

### Workflow 1: Comprehensive Company Research
```
1. Start with Company Analysis:
   "Analyze Apple's current performance"

2. Get Research Recommendations:
   "What should I research about Apple?"

3. Upload earnings PDF:
   Upload AAPL_Q4_2024.pdf
   "Analyze this report"

4. Make informed decision based on all insights
```

### Workflow 2: Quick Investment Check
```
1. Ask direct question:
   "Is Microsoft a good buy right now?"

2. Review recommendation and rationale

3. Follow up with:
   "What are the main risks?"
```

## 🚧 Future Enhancements

### Phase 2 (Planned)
- [ ] Real-time market data via web search
- [ ] Integration with financial APIs (Alpha Vantage, Yahoo Finance)
- [ ] Historical analysis caching
- [ ] Multi-document comparison
- [ ] Export reports to PDF

### Phase 3 (Future)
- [ ] Portfolio tracking and analysis
- [ ] Automated alert system
- [ ] Real-time news monitoring
- [ ] Social sentiment analysis
- [ ] API endpoints for programmatic access

## 🐛 Troubleshooting

### Common Issues

**"API Key Error"**
- Ensure `.env` file exists in project root
- Verify API key is correct
- Restart Streamlit after creating .env

**"PDF Upload Failed"**
- Check file size (max 32MB for Groq)
- Ensure PDF is text-based, not scanned images
- Try converting PDF to newer format

**"Slow Responses"**
- Check internet connection
- Large PDFs take longer to process
- Consider simplifying complex queries

**"Import Errors"**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify virtual environment is activated

## 🔐 Security Notes

- Never commit `.env` file to version control
- Add to `.gitignore`:
  ```
  .env
  .streamlit/secrets.toml
  __pycache__/
  *.pyc
  .cache/
  .vectorstore/
  ```
- Use environment-specific API keys
- Don't upload confidential documents

## 📝 Development

### Adding New Agents

Create a new agent in `agents/`:

```python
# agents/your_new_agent.py
import groq
from typing import Dict, Any, Optional

class YourNewAgent:
    def __init__(self, client: groq.Groq):
        self.client = client
        self.model = "llama-3.3-70b-versatile"

    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        # Your agent logic here
        pass
```

Register in `agents/__init__.py` and orchestrator.

### Integrating External APIs

Add API integrations in `tools/data_fetcher.py`:

```python
def get_stock_data(ticker: str) -> Dict:
    # Your API integration
    pass
```

## 📚 Resources

- [Groq Documentation](https://console.groq.com/docs/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [SEC EDGAR Database](https://www.sec.gov/edgar)
- [Financial Modeling Prep API](https://financialmodelingprep.com/)

## 📄 License

This project is for educational and research purposes.

## 🤝 Contributing

This is a prototype framework. Feel free to:
- Add new agents
- Integrate financial APIs
- Enhance visualizations
- Improve error handling

## 💬 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the code comments
3. Consult Groq's documentation

---

**Built with Groq Llama 3.3 70B | Powered by Groq**

*Last Updated: January 2025*
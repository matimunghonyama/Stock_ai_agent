"""
Research Recommender Agent
Specialized agent for recommending research sources and due diligence
"""

import groq
from typing import Dict, Any, Optional, List


class ResearchRecommenderAgent:
    """Specialized agent for recommending research sources and due diligence"""

    def __init__(self, client: groq.Groq):
        self.client = client
        self.model = "llama-3.3-70b-versatile"
    
    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process research recommendations request
        
        Args:
            query: User's question about research sources
            context: Dictionary containing entities and other context
            
        Returns:
            Curated research recommendations as formatted string
        """
        entities = context.get('entities', []) if context else []
        
        research_prompt = f"""You are a financial research strategist helping investors build conviction in their investment decisions.

User Query: {query}
Companies/Topics: {', '.join(entities) if entities else 'To be determined'}

Provide a comprehensive research roadmap with specific, actionable sources:

##  Research Objective
Clearly state what the investor needs to understand to build conviction.

##  Phase 1: Primary Sources (Company-Direct)

### SEC Filings (Essential Reading)
- **10-K Annual Report**: Look for [specific sections to focus on]
- **10-Q Quarterly Reports**: Track [key metrics to monitor]
- **8-K Current Reports**: Watch for [types of events]
- **Proxy Statements (DEF 14A)**: Analyze [executive compensation, governance]
- **Where to find**: SEC EDGAR database (sec.gov/edgar)

### Investor Relations Materials
- **Earnings Call Transcripts**: Focus on [specific topics]
- **Investor Presentations**: Look for [slides on strategy/guidance]
- **Annual Shareholder Letters**: [Why they matter]
- **Where to find**: Company IR website, Seeking Alpha transcripts

### Management Communication
- **CEO Interviews**: [Recommended sources]
- **Conference Presentations**: [Key industry conferences]
- **Social Media**: [If relevant - accounts to follow]

##  Phase 2: Market & Financial Data

### Stock & Valuation Metrics
- **Key Metrics to Track Daily/Weekly**:
  * Stock price and volume patterns
  * [Specific technical indicators]
  * Options flow (if relevant)
- **Data Sources**: Yahoo Finance, Bloomberg, TradingView

### Financial Ratios & Comparisons
- **Compare These Metrics Against Peers**:
  * [Ratio 1] - Industry average: [X]
  * [Ratio 2] - Industry average: [Y]
  * [Ratio 3] - Industry average: [Z]
- **Tools**: Finviz, Koyfin, FactSet

### Analyst Coverage
- **Consensus Estimates**: [Where to find]
- **Price Targets**: Track changes in [specific metrics]
- **Ratings Changes**: Monitor upgrades/downgrades
- **Sources**: Yahoo Finance, Seeking Alpha, TipRanks

##  Phase 3: News & Market Intelligence

### Financial News (Daily Monitoring)
- **Primary Sources**:
  * Bloomberg: [Specific sections/topics]
  * WSJ Markets: [What to watch]
  * Financial Times: [Relevant coverage]
  * Reuters Business: [Industry news]

### Industry-Specific Publications
- **For this sector**: [Name 3-5 specialized publications]
- **Key journalists/analysts to follow**: [Names + why]

### Competitive Intelligence
- **Competitor Filings**: [Which competitors to monitor]
- **Industry Reports**: [Gartner, IDC, etc.]
- **Market Share Data**: [Where to find]

##  Phase 4: Alternative Data & Indicators

### Industry Trends
- **Supply Chain Signals**: [What to monitor]
- **Technology Adoption**: [Metrics to track]
- **Regulatory Environment**: [Key developments]

### Consumer/Market Sentiment
- **App Store Rankings**: [If applicable]
- **Web Traffic Data**: SimilarWeb, Alexa
- **Social Sentiment**: [Relevant platforms]
- **Google Trends**: [Search terms to monitor]

### Channel Checks (If applicable)
- **Retail foot traffic**: [Methods]
- **Partner reports**: [Which partners matter]
- **Customer surveys**: [Sources]

##  Phase 5: Expert Analysis & Education

### Thought Leaders to Follow
1. **[Name]** - [Why/What they cover] - [Platform]
2. **[Name]** - [Why/What they cover]
3. **[Name]** - [Why/What they cover]

### Educational Resources
- **Understanding the Business Model**: [Specific resources]
- **Industry Primers**: [Reports/papers to read]
- **Accounting Deep-Dives**: [If complex accounting]

### Podcasts & Video Content
- **[Podcast Name]**: [Why relevant]
- **[YouTube Channel]**: [What they cover]
- **Earnings Call Replays**: [Where to listen]

##  Phase 6: Risk Assessment Sources

### Risk Monitoring
- **Regulatory Risks**: [Agencies/sources to monitor]
- **Legal Issues**: [Court filings, litigation trackers]
- **Short Seller Reports**: [Firms to watch]
- **Credit Ratings**: Moody's, S&P, Fitch

### Macro Factors
- **Economic Indicators**: [Relevant metrics]
- **Currency Exposure**: [If international]
- **Interest Rate Sensitivity**: [Why it matters]

##  Conviction Building Framework

### Key Questions to Answer
1. **Business Quality**: [Specific question about moat/competition]
2. **Growth Trajectory**: [Specific question about sustainability]
3. **Management Quality**: [Specific question about execution]
4. **Valuation**: [Specific question about price vs value]
5. **Risk/Reward**: [Specific question about downside protection]

### Red Flags to Watch For
- [Specific warning sign #1]
- [Specific warning sign #2]
- [Specific warning sign #3]

### Confirmation Signals
- [Positive indicator #1]
- [Positive indicator #2]
- [Positive indicator #3]

##  Research Timeline

**Week 1**: [Focus areas]
**Week 2**: [Focus areas]
**Week 3**: [Focus areas]
**Week 4**: [Synthesize and decide]

##  Pro Tips

1. **Start Here**: [Most important source to begin with]
2. **Cross-Reference**: [How to validate information across sources]
3. **Time Investment**: Expect [X] hours for thorough due diligence
4. **Update Frequency**: Review [these sources] [daily/weekly/monthly]

## 🔗 Quick Links Template

Create a bookmarks folder with:
- Company IR page: [URL structure]
- SEC EDGAR: sec.gov/cgi-bin/browse-edgar?company=[TICKER]
- Earnings transcripts: seekingalpha.com/symbol/[TICKER]/earnings
- Financial data: finance.yahoo.com/quote/[TICKER]

---

**Remember**: Building conviction takes time. Don't rush the research process. The goal is to understand the business deeply enough to make an informed decision and hold through volatility."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=4096,
                messages=[{"role": "user", "content": research_prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating research recommendations: {str(e)}"

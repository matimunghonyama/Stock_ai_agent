"""
Company Analyzer Agent
Specialized agent for company performance and stock analysis
"""

import groq
from typing import Dict, Any, Optional, List


class CompanyAnalyzerAgent:
    """Specialized agent for company performance and stock analysis"""

    def __init__(self, client: groq.Groq):
        self.client = client
        self.model = "llama-3.3-70b-versatile"
    
    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process company analysis request
        
        Args:
            query: User's question about the company
            context: Dictionary containing entities and other context
            
        Returns:
            Detailed company analysis as formatted string
        """
        companies = context.get('entities', []) if context else []
        
        analysis_prompt = f"""You are a professional equity research analyst. Analyze the company/companies based on the query.

User Query: {query}
Companies Mentioned: {', '.join(companies) if companies else 'To be determined from query'}

Provide a comprehensive investment analysis:

## Company Overview
- Business model and core operations
- Market capitalization and valuation
- Sector and industry classification

## Recent Performance
- Latest quarterly results (revenue, earnings, margins)
- Year-over-year growth rates
- Sequential growth (QoQ)
- Comparison to analyst estimates (beat/miss)

## Financial Health Score
Rate each area (1-10 scale):
- Revenue Growth: [X/10]
- Profitability: [X/10]
- Balance Sheet Strength: [X/10]
- Cash Flow Quality: [X/10]
- **Overall Score: [X/40]**

## Investment Thesis

### Bull Case (Reasons to BUY)
1. [Key strength #1]
2. [Key strength #2]
3. [Key strength #3]
4. [Growth catalyst]

### Bear Case (Reasons to be CAUTIOUS)
1. [Key risk #1]
2. [Key risk #2]
3. [Key concern #3]
4. [Headwind]

## Valuation Analysis
- Current P/E ratio vs industry average
- Price-to-Sales ratio
- EV/EBITDA multiple
- Valuation assessment: [Undervalued/Fairly Valued/Overvalued]

## Recommendation: [BUY / HOLD / SELL]

**Investment Horizon:** [Short/Medium/Long term]
**Risk Level:** [Low/Medium/High]
**Price Target:** [If applicable]

**Rationale (3-4 sentences):**
[Clear explanation of recommendation]

## Key Catalysts to Watch
- Upcoming earnings date
- Product launches
- Regulatory decisions
- Industry trends

## Risks & Considerations
1. **Market Risk:** [Description]
2. **Company-Specific Risk:** [Description]
3. **Sector Risk:** [Description]

## Peer Comparison
Compare with top 2-3 competitors on:
- Revenue growth
- Margins
- Market share
- Valuation multiples

Note: If you need current market data, real-time stock prices, or recent news to provide accurate analysis, clearly indicate what additional information would be valuable and suggest using web search or checking financial data sources."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=3500,
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error analyzing company: {str(e)}"

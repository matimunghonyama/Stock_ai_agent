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
        # State management for tracking analysis constraints
        self.analysis_state = {
            "has_market_data": False,
            "has_financial_data": False,
            "has_news_data": False,
            "last_query": None,
            "missing_info": [],
            "recovery_attempts": 0
        }
    
    def assess_information_availability(self, companies: List[str]) -> Dict[str, Any]:
        """
        Assess what information is available for analysis

        Args:
            companies: List of company names/tickers

        Returns:
            Dictionary with availability assessment
        """
        assessment = {
            "companies_found": [],
            "companies_missing": [],
            "available_data_types": [],
            "constraints": []
        }

        # This would typically check against a knowledge base or external APIs
        # For now, we'll simulate based on common knowledge
        known_companies = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX"]

        for company in companies:
            company_upper = company.upper()
            if any(known in company_upper for known in known_companies) or len(company) > 2:
                assessment["companies_found"].append(company)
                assessment["available_data_types"].extend(["basic_info", "sector_data"])
            else:
                assessment["companies_missing"].append(company)
                assessment["constraints"].append(f"No data available for {company}")

        # Update agent state
        self.analysis_state.update({
            "has_market_data": len(assessment["companies_found"]) > 0,
            "has_financial_data": len(assessment["companies_found"]) > 0,
            "missing_info": assessment["companies_missing"],
            "last_query": companies
        })

        return assessment

    def generate_recovery_response(self, query: str, assessment: Dict[str, Any]) -> str:
        """
        Generate a recovery response when information is limited

        Args:
            query: Original user query
            assessment: Information availability assessment

        Returns:
            Recovery response with clear constraints and next steps
        """
        if not assessment["companies_found"]:
            return f"""## Analysis Constraints Identified

**Current Situation:** I don't have access to current market data or financial information for the requested companies.

**What I Can Provide:**
- General investment principles and analysis frameworks
- Questions to ask when evaluating companies
- Research methodology guidance

**Recommended Next Steps:**
1. **Use Web Search**: Try searching for "{query}" to get current market data
2. **Check Financial Websites**: Visit Yahoo Finance, Seeking Alpha, or Bloomberg for the companies
3. **Provide More Context**: Share what you already know about these companies

**Would you like me to:**
- Guide you on how to research these companies manually?
- Explain general investment analysis principles?
- Help formulate specific questions for web search?

*Note: My analysis capabilities are currently limited by data availability constraints.*"""

        # Partial information available
        found = assessment["companies_found"]
        missing = assessment["companies_missing"]

        response = f"""## Partial Analysis Available

**Companies with Data:** {', '.join(found)}
**Companies without Data:** {', '.join(missing) if missing else 'None'}

**Analysis Approach:**
- I'll provide analysis for companies with available data
- For companies without data, I'll suggest research approaches
- All recommendations will clearly indicate data limitations

**Data Constraints:**
- No real-time market prices or recent financial statements
- Limited to general knowledge and analysis frameworks
- Recommendations based on historical patterns and industry knowledge

Would you like me to proceed with analysis for the available companies, or would you prefer to gather more data first?"""

        return response

    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process company analysis request with agent-aware state management

        Args:
            query: User's question about the company
            context: Dictionary containing entities and other context

        Returns:
            Detailed company analysis as formatted string
        """
        companies = context.get('entities', []) if context else []

        # Agent-aware: Assess information availability first
        if companies:
            assessment = self.assess_information_availability(companies)

            # Recovery behavior: If no information available, provide clear guidance
            if not assessment["companies_found"] and assessment["companies_missing"]:
                self.analysis_state["recovery_attempts"] += 1
                return self.generate_recovery_response(query, assessment)

            # State management: Track constraints for transparency
            if assessment["constraints"]:
                constraint_note = f"\n\n**Analysis Constraints:** {', '.join(assessment['constraints'])}"

        analysis_prompt = f"""You are a professional equity research analyst. Analyze the company/companies based on the query.

User Query: {query}
Companies Mentioned: {', '.join(companies) if companies else 'To be determined from query'}

IMPORTANT: If you don't have specific data about a company, clearly state your information limitations and focus on general analysis principles.

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

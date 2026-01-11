"""
Web Search Integration
Functions to enable web search capabilities (requires Claude API with web search)
"""

import anthropic
from typing import List, Dict, Optional


class WebSearchTool:
    """Tool for performing web searches via Claude API"""
    
    def __init__(self, client: anthropic.Anthropic):
        self.client = client
        self.model = "claude-sonnet-4-20250514"
    
    def search(self, query: str, max_results: int = 5) -> str:
        """
        Perform a web search and return results

        Args:
            query: Search query
            max_results: Maximum number of results to return

        Returns:
            Formatted search results as string
        """
        return f"Web search is currently not available with the Groq API. For real-time data and web search capabilities, consider using alternative APIs like Anthropic Claude with web search tools. Query: {query}"
    
    def get_current_stock_price(self, ticker: str) -> Optional[Dict]:
        """
        Get current stock price for a ticker
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with price information or None
        """
        query = f"current stock price {ticker}"
        result = self.search(query, max_results=1)
        
        # In a real implementation, parse the result to extract structured data
        # For now, return the raw result
        return {"raw_result": result}
    
    def get_latest_news(self, company: str, days: int = 7) -> str:
        """
        Get latest news for a company
        
        Args:
            company: Company name or ticker
            days: Number of days to look back
            
        Returns:
            Formatted news results
        """
        query = f"{company} news last {days} days"
        return self.search(query, max_results=5)
    
    def get_earnings_date(self, ticker: str) -> str:
        """
        Get next earnings date for a company
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Earnings date information
        """
        query = f"{ticker} next earnings date 2025"
        return self.search(query, max_results=1)


# Standalone functions for easy import

def search_web(client: groq.Groq, query: str) -> str:
    """
    Simple web search function

    Args:
        client: Groq client
        query: Search query

    Returns:
        Search results as string
    """
    tool = WebSearchTool(client)
    return tool.search(query)


def get_company_news(client: groq.Groq, company: str) -> str:
    """
    Get recent news for a company

    Args:
        client: Groq client
        company: Company name or ticker

    Returns:
        News results as string
    """
    tool = WebSearchTool(client)
    return tool.get_latest_news(company)

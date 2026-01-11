"""
Agent Orchestrator
Main orchestration class that routes requests to specialist agents
"""

import groq
import json
from typing import Dict, Optional

from .pdf_analyzer import PDFAnalyzerAgent
from .company_analyzer import CompanyAnalyzerAgent
from .research_recommender import ResearchRecommenderAgent


class AgentOrchestrator:
    """Main orchestration class that classifies intent and routes to specialist agents"""

    def __init__(self, client: groq.Groq):
        self.client = client
        self.model = "llama-3.3-70b-versatile"
        
        # Initialize specialist agents
        self.pdf_agent = PDFAnalyzerAgent(client)
        self.company_agent = CompanyAnalyzerAgent(client)
        self.research_agent = ResearchRecommenderAgent(client)
    
    def classify_intent(self, user_query: str) -> Dict:
        """
        Classify user intent using Claude
        
        Args:
            user_query: The user's question or request
            
        Returns:
            Dictionary with intent, entities, and confidence
        """
        classification_prompt = f"""Analyze this query and return ONLY a JSON object (no other text):

Query: "{user_query}"

Return JSON with these fields:
{{
  "intent": "<one of: pdf_analysis | company_analysis | research_recommendations | general_query>",
  "entities": ["<company tickers or names if mentioned>"],
  "requires_web_search": <boolean>,
  "requires_pdf": <boolean>,
  "confidence": <0.0 to 1.0>
}}

Classification guide:
- pdf_analysis: User wants to analyze a document they uploaded
- company_analysis: User asks about company performance, stock recommendation, valuation
- research_recommendations: User asks what to research, where to find information, how to build conviction
- general_query: General financial questions or unclear intent

Return ONLY the JSON object."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=300,
                messages=[{"role": "user", "content": classification_prompt}]
            )

            result = json.loads(response.choices[0].message.content.strip())
            return result
        except Exception as e:
            print(f"Intent classification error: {e}")
            return {
                "intent": "general_query",
                "entities": [],
                "requires_web_search": False,
                "requires_pdf": False,
                "confidence": 0.5
            }
    
    def route_and_process(self, query: str, intent_data: Dict, pdf_data: Optional[bytes] = None) -> str:
        """
        Route request to appropriate specialist agent
        
        Args:
            query: User's question
            intent_data: Intent classification result
            pdf_data: Optional PDF file data
            
        Returns:
            Agent's response as string
        """
        intent = intent_data.get("intent", "general_query")
        context = {
            "entities": intent_data.get("entities", []),
            "pdf_data": pdf_data
        }
        
        if intent == "pdf_analysis" and pdf_data:
            return self.pdf_agent.process(query, context)
        elif intent == "company_analysis":
            return self.company_agent.process(query, context)
        elif intent == "research_recommendations":
            return self.research_agent.process(query, context)
        else:
            return self._handle_general_query(query)
    
    def _handle_general_query(self, query: str) -> str:
        """Handle general financial queries"""
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"""You are a helpful financial assistant. Answer this question clearly and concisely:

{query}

If the question is about a specific analysis or research, guide the user on how to use the appropriate feature."""
            }]
        )
        return response.choices[0].message.content

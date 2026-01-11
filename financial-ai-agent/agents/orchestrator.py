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
    """Main orchestration class that classifies intent and routes to specialist agents with state management"""

    def __init__(self, client: groq.Groq):
        self.client = client
        self.model = "llama-3.3-70b-versatile"

        # Initialize specialist agents
        self.pdf_agent = PDFAnalyzerAgent(client)
        self.company_agent = CompanyAnalyzerAgent(client)
        self.research_agent = ResearchRecommenderAgent(client)

        # Agent-aware state management
        self.session_state = {
            "current_mode": None,
            "last_intent": None,
            "agent_states": {},
            "interaction_history": [],
            "constraints_identified": []
        }
    
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

    def update_session_state(self, intent_data: Dict, response: str):
        """
        Update session state based on interaction

        Args:
            intent_data: Intent classification result
            response: Agent response
        """
        self.session_state["last_intent"] = intent_data.get("intent")
        self.session_state["interaction_history"].append({
            "intent": intent_data,
            "response_length": len(response),
            "timestamp": "current"
        })

        # Update agent states
        if hasattr(self.company_agent, 'get_analysis_state'):
            self.session_state["agent_states"]["company_analyzer"] = self.company_agent.get_analysis_state()

    def get_session_context(self) -> Dict:
        """
        Get current session context for agent awareness

        Returns:
            Session context dictionary
        """
        return {
            "current_mode": self.session_state["current_mode"],
            "last_intent": self.session_state["last_intent"],
            "interaction_count": len(self.session_state["interaction_history"]),
            "constraints": self.session_state["constraints_identified"],
            "agent_states": self.session_state["agent_states"]
        }

    def handle_constraint_scenario(self, intent_data: Dict, query: str) -> str:
        """
        Handle scenarios where agents identify constraints

        Args:
            intent_data: Intent classification result
            query: Original user query

        Returns:
            Recovery response with clear guidance
        """
        intent = intent_data.get("intent", "general_query")

        if intent == "company_analysis":
            # Check if company agent has identified constraints
            if hasattr(self.company_agent, 'get_analysis_state'):
                agent_state = self.company_agent.get_analysis_state()
                if agent_state.get("missing_info"):
                    return self.company_agent.generate_recovery_response(
                        query,
                        {
                            "companies_found": [],
                            "companies_missing": agent_state["missing_info"],
                            "constraints": [f"No data available for {company}" for company in agent_state["missing_info"]]
                        }
                    )

        # Default constraint handling
        return f"""## Analysis Constraints Detected

I need additional information to provide a complete analysis for your query: "{query}"

**Possible approaches:**
1. **Provide more context** about the companies or topic
2. **Use web search** to gather current market data
3. **Upload relevant documents** (PDFs, reports) for analysis
4. **Specify the type of analysis** you need (company analysis, research guidance, etc.)

What specific information would you like me to help you find or analyze?"""

    def reset_session(self):
        """Reset session state for new conversations"""
        self.session_state = {
            "current_mode": None,
            "last_intent": None,
            "agent_states": {},
            "interaction_history": [],
            "constraints_identified": []
        }
        # Reset individual agent states
        if hasattr(self.company_agent, 'reset_state'):
            self.company_agent.reset_state()

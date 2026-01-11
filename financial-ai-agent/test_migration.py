#!/usr/bin/env python3
"""
Test script to verify the migration from Anthropic to Groq works correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")
    try:
        import groq
        import streamlit as st
        import pandas as pd
        import plotly.graph_objects as go
        from agents.orchestrator import AgentOrchestrator
        from agents.pdf_analyzer import PDFAnalyzerAgent
        from agents.company_analyzer import CompanyAnalyzerAgent
        from agents.research_recommender import ResearchRecommenderAgent
        from tools.pdf_processor import extract_json_from_response, extract_recommendation
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_client_initialization():
    """Test that Groq client can be initialized."""
    print("Testing Groq client initialization...")
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("✗ GROQ_API_KEY not found in environment")
            return False

        import groq
        client = groq.Groq(api_key=api_key)
        print("✓ Groq client initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Client initialization error: {e}")
        return False

def test_agent_initialization():
    """Test that all agents can be initialized."""
    print("Testing agent initialization...")
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("✗ GROQ_API_KEY not found, skipping agent tests")
            return False

        import groq
        from agents.orchestrator import AgentOrchestrator
        from agents.pdf_analyzer import PDFAnalyzerAgent
        from agents.company_analyzer import CompanyAnalyzerAgent
        from agents.research_recommender import ResearchRecommenderAgent

        client = groq.Groq(api_key=api_key)

        # Test orchestrator
        orchestrator = AgentOrchestrator(client)
        print("✓ AgentOrchestrator initialized")

        # Test individual agents
        pdf_agent = PDFAnalyzerAgent(client)
        print("✓ PDFAnalyzerAgent initialized")

        company_agent = CompanyAnalyzerAgent(client)
        print("✓ CompanyAnalyzerAgent initialized")

        research_agent = ResearchRecommenderAgent(client)
        print("✓ ResearchRecommenderAgent initialized")

        return True
    except Exception as e:
        print(f"✗ Agent initialization error: {e}")
        return False

def test_intent_classification():
    """Test intent classification with Groq."""
    print("Testing intent classification...")
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("✗ GROQ_API_KEY not found, skipping API tests")
            return False

        import groq
        from agents.orchestrator import AgentOrchestrator

        client = groq.Groq(api_key=api_key)

        orchestrator = AgentOrchestrator(client)

        # Test a simple query
        result = orchestrator.classify_intent("Analyze Apple's performance")
        print(f"✓ Intent classification result: {result}")

        return True
    except Exception as e:
        print(f"✗ Intent classification error: {e}")
        return False

def test_company_analysis():
    """Test company analysis agent."""
    print("Testing company analysis...")
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("✗ GROQ_API_KEY not found, skipping API tests")
            return False

        import groq
        from agents.company_analyzer import CompanyAnalyzerAgent

        client = groq.Groq(api_key=api_key)

        agent = CompanyAnalyzerAgent(client)

        # Test with a simple query (this will make an API call)
        result = agent.process("Analyze Microsoft", {"entities": ["Microsoft"]})
        print("✓ Company analysis completed (first 200 chars):")
        print(result[:200] + "...")

        return True
    except Exception as e:
        print(f"✗ Company analysis error: {e}")
        return False

def test_web_search_modification():
    """Test that web search indicates it's not available with Groq."""
    print("Testing web search modification...")
    try:
        from tools.web_search import search_web, WebSearchTool

        # Test standalone function
        result = search_web("test query")
        if "not available with Groq" in result.lower():
            print("✓ Web search function correctly indicates unavailability")
        else:
            print(f"✗ Unexpected web search result: {result}")
            return False

        # Test WebSearchTool class
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            import groq
            client = groq.Groq(api_key=api_key)
            tool = WebSearchTool(client)
            print("✓ WebSearchTool class uses groq.Groq")
        else:
            print("⚠ Skipping WebSearchTool client test (no API key)")

        return True
    except Exception as e:
        print(f"✗ Web search test error: {e}")
        return False

def test_pdf_analyzer_error_handling():
    """Test PDF analyzer error handling for empty PDFs."""
    print("Testing PDF analyzer error handling...")
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("✗ GROQ_API_KEY not found, skipping PDF tests")
            return False

        import groq
        from agents.pdf_analyzer import PDFAnalyzerAgent

        client = groq.Groq(api_key=api_key)
        agent = PDFAnalyzerAgent(client)

        # Test with no PDF data
        result = agent.process("Analyze this PDF", {})
        if "No PDF data provided" in result:
            print("✓ Correctly handles missing PDF data")
        else:
            print(f"✗ Unexpected result for missing PDF: {result}")
            return False

        # Test with empty PDF (simulated)
        from io import BytesIO
        import PyPDF2

        # Create a minimal PDF with no text
        empty_pdf = BytesIO()
        writer = PyPDF2.PdfWriter()
        writer.add_blank_page(width=612, height=792)  # Letter size
        writer.write(empty_pdf)
        empty_pdf.seek(0)

        result = agent.process("Analyze this PDF", {"pdf_data": empty_pdf.getvalue()})
        if "Could not extract readable text" in result:
            print("✓ Correctly handles PDFs with no extractable text")
        else:
            print(f"✗ Unexpected result for empty PDF: {result[:100]}...")
            return False

        return True
    except Exception as e:
        print(f"✗ PDF analyzer test error: {e}")
        return False

def main():
    """Run all tests."""
    print("=== Testing Migration from Anthropic to Groq ===\n")

    tests = [
        test_imports,
        test_client_initialization,
        test_agent_initialization,
        test_intent_classification,
        test_company_analysis,
        test_web_search_modification,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"✗ Test failed with exception: {e}\n")

    print(f"=== Test Results: {passed}/{total} tests passed ===")

    if passed == total:
        print("🎉 All tests passed! Migration appears successful.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

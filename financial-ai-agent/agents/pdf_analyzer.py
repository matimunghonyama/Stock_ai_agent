"""
PDF Analyzer Agent
Specialized agent for analyzing earnings reports and financial PDFs
"""

import groq
import PyPDF2
from io import BytesIO
from typing import Dict, Any, Optional


class PDFAnalyzerAgent:
    """Specialized agent for analyzing earnings reports and financial PDFs"""
    
    def __init__(self, client: groq.Groq):
        self.client = client
        self.model = "llama-3.3-70b-versatile"
    
    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process PDF analysis request

        Args:
            query: User's question about the PDF
            context: Dictionary containing pdf_data and other context

        Returns:
            Detailed analysis as formatted string
        """
        if not context or 'pdf_data' not in context:
            return "No PDF data provided for analysis. Please upload a PDF file."

        pdf_data = context['pdf_data']

        # Extract text from PDF
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_data))
            pdf_text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text.strip():  # Only add non-empty pages
                    pdf_text += page_text + "\n"

            # Check if we extracted meaningful text
            if not pdf_text.strip():
                return "Error: Could not extract readable text from the PDF. The PDF may be image-based, scanned, or contain no extractable text. Please try a different PDF file with text content."

            print(f"Extracted {len(pdf_text)} characters from PDF")  # Debug logging

        except Exception as e:
            return f"Error extracting text from PDF: {str(e)}"

        # Limit text to first 50,000 characters to avoid token limits
        pdf_text = pdf_text[:50000]

        analysis_prompt = f"""You are analyzing an earnings report PDF. The user has uploaded a PDF and wants you to analyze it.

IMPORTANT: You have received the actual PDF text content below. Do NOT ask the user to paste text - analyze the provided content.

Analyze this earnings report text and provide a structured analysis:

## Executive Summary
Provide a 3-4 sentence overview of the company's quarterly performance.

## Financial Performance Deep Dive

### Revenue Analysis
- Total Revenue: [Amount] ([YoY %])
- Revenue by Segment: [Break down key segments]
- Revenue Growth Trends

### Profitability Metrics
- Gross Profit Margin: [%]
- Operating Margin: [%]
- Net Profit Margin: [%]
- EPS (Actual vs Expected)

### Cash Flow & Balance Sheet
- Operating Cash Flow
- Free Cash Flow
- Cash Position
- Debt Levels

## Operational Highlights
- Key achievements this quarter
- Product/service performance
- Market share changes
- Customer metrics (if available)

## Management Commentary
- Forward guidance
- Strategic initiatives
- Market outlook
- Risk factors mentioned

## Competitive Position
- How does performance compare to peers?
- Market position changes

## Investment Analysis

### Strengths (Bull Case)
- List key positive factors
- Growth opportunities

### Concerns (Bear Case)
- List potential risks
- Challenges ahead

### Recommendation: [BUY / HOLD / SELL]
**Target Price:** [If determinable]
**Confidence Level:** [High/Medium/Low]
**Rationale:** [2-3 sentences]

## Key Metrics for Visualization
```json
{{
  "quarterly_trends": {{
    "revenue": [{{"quarter": "Q1 2023", "value": 0}}, ...],
    "net_income": [{{"quarter": "Q1 2023", "value": 0}}, ...],
    "eps": [{{"quarter": "Q1 2023", "value": 0}}, ...]
  }},
  "current_metrics": {{
    "revenue": 0,
    "revenue_growth_yoy": 0,
    "net_income": 0,
    "eps": 0,
    "profit_margin": 0
  }},
  "segment_breakdown": [
    {{"segment": "Product A", "revenue": 0, "percentage": 0}}
  ]
}}
```

## Key Takeaways
1. [Most important finding]
2. [Second most important finding]
3. [Third most important finding]

Be specific with numbers, dates, and percentages. Extract all quantitative data available.

PDF Content:
{pdf_text}

Additional context from user: {query}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=4096,
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error analyzing PDF: {str(e)}"

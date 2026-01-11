"""
PDF Processing Utilities
Helper functions for processing PDF analysis results
"""

import re
import json
from typing import Optional, Dict


def extract_json_from_response(text: str) -> Optional[Dict]:
    """
    Extract JSON data from Claude's response
    
    Args:
        text: Response text that may contain JSON in code blocks
        
    Returns:
        Parsed JSON dictionary or None if no valid JSON found
    """
    try:
        # Try to find JSON in markdown code blocks
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1).strip()
            return json.loads(json_str)
        
        # Try to find JSON without code blocks
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
            
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
    except Exception as e:
        print(f"Unexpected error extracting JSON: {e}")
    
    return None


def extract_recommendation(text: str) -> str:
    """
    Extract BUY/HOLD/SELL recommendation from response
    
    Args:
        text: Response text containing recommendation
        
    Returns:
        'BUY', 'HOLD', 'SELL', or 'N/A'
    """
    text_upper = text.upper()
    
    # Look for explicit recommendation patterns
    patterns = [
        r'RECOMMENDATION[:\s]*\*?\*?\s*(BUY|HOLD|SELL)',
        r'RECOMMENDATION:\s*\[?(BUY|HOLD|SELL)\]?',
        r'\*\*RECOMMENDATION:\*\*\s*(BUY|HOLD|SELL)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_upper)
        if match:
            return match.group(1)
    
    # If no explicit pattern found, look for first occurrence
    if 'BUY' in text_upper and text_upper.index('BUY') < text_upper.find('HOLD', 0, len(text_upper)):
        return 'BUY'
    elif 'HOLD' in text_upper:
        return 'HOLD'
    elif 'SELL' in text_upper:
        return 'SELL'
    
    return 'N/A'


def extract_metrics_from_response(text: str) -> Dict[str, float]:
    """
    Extract key financial metrics from response text
    
    Args:
        text: Response text containing financial metrics
        
    Returns:
        Dictionary of metric names to values
    """
    metrics = {}
    
    # Patterns for common metrics
    patterns = {
        'revenue': r'Revenue[:\s]*\$?([0-9,.]+)\s*([MB])?',
        'net_income': r'Net Income[:\s]*\$?([0-9,.]+)\s*([MB])?',
        'eps': r'EPS[:\s]*\$?([0-9,.]+)',
        'profit_margin': r'Profit Margin[:\s]*([0-9,.]+)%',
    }
    
    for metric_name, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                value = float(match.group(1).replace(',', ''))
                # Convert to millions if specified
                if len(match.groups()) > 1 and match.group(2):
                    if match.group(2).upper() == 'B':
                        value *= 1000
                metrics[metric_name] = value
            except (ValueError, IndexError):
                continue
    
    return metrics


def format_currency(value: float, in_millions: bool = True) -> str:
    """
    Format a number as currency
    
    Args:
        value: Numeric value
        in_millions: Whether to format in millions
        
    Returns:
        Formatted string
    """
    if in_millions:
        return f"${value:,.2f}M"
    else:
        return f"${value:,.2f}"


def format_percentage(value: float) -> str:
    """
    Format a number as percentage
    
    Args:
        value: Numeric value (0-100)
        
    Returns:
        Formatted string
    """
    return f"{value:.2f}%"
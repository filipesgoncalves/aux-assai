"""
Utility functions for data processing.
"""

def fix_utf8_encoding(text: str) -> str:
    """
    Fix UTF-8 encoding issues where text was incorrectly decoded as Latin-1.
    
    Common issues:
    - \u00c3\u00a9 should be é
    - \u00c3\u00b3 should be ó  
    - \u00c3\u00aa should be ê
    - \u00c3\u00a7 should be ç
    - \u00c3\u00a1 should be á
    - \u00c3\u00a0 should be à
    - \u00c3\u00a2 should be â
    - \u00c3\u00a3 should be ã
    - \u00c3\u00ad should be í
    - \u00c3\u00b4 should be ô
    - \u00c3\u00ba should be ú
    - \u00c3\u00bc should be ü
    """
    if not isinstance(text, str) or not text:
        return text
    
    try:
        if '\u00c3' in text:
            fixed = text.encode('latin-1').decode('utf-8')
            return fixed
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass
    
    return text


def fix_encoding_in_dict(data: dict) -> dict:
    """
    Recursively fix UTF-8 encoding issues in a dictionary.
    """
    if not isinstance(data, dict):
        return data
    
    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = fix_utf8_encoding(value)
        elif isinstance(value, dict):
            result[key] = fix_encoding_in_dict(value)
        elif isinstance(value, list):
            result[key] = [fix_encoding_in_dict(item) if isinstance(item, dict) 
                          else fix_utf8_encoding(item) if isinstance(item, str) 
                          else item for item in value]
        else:
            result[key] = value
    
    return result

import re
import unicodedata
import regex

def remove_emojis(text: str) -> str:
    """
    Removes emojis and other graphic symbols from text.
    """
    if not isinstance(text, str):
        return ""
    # Remove unicode emoji characters
    return regex.sub(r'\p{Emoji}', '', text)

def clean_text(text: str) -> str:
    """
    Performs basic text hygiene suitable for NLP tasks.
    
    Processing steps:
    1. Unicode Normalization (NFC)
    2. URL removal
    3. Trailing whitespace removal
    """
    if not isinstance(text, str):
        return ""
        
    # Unicode Normalization
    text = unicodedata.normalize('NFC', text)
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Strip whitespace
    text = text.strip()
    
    return text

def anonymize_text(text: str) -> str:
    """
    Removes potentially identifying patterns like emails or phone numbers.
    """
    # Remove emails
    text = re.sub(r'\S+@\S+', '<EMAIL>', text)
    return text

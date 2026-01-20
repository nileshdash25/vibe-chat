# chat/utils.py
import re

BAD_WORDS = [
    "madarchodwa", "behenchodwa", "randidwa", "madarchodka", "behenchodka", # Lambe words pehle
    "bhosdiwala", "randiwala", "chutiyapa", "bhosdipan", "madarchod", "behenchod",
    "chutiya", "bhosdike", "maghia", "gandu", "randi", "fuck", "hate", "sala", "mc", "bc", "bhenchod", "chod", "lund", "loda", "jhaat", "jhaantu", "gaand", "pichwada", "tatti", "bhosda", "chut", "chutiya", "chutmar", "lund", "loda", "randi", "randi ka bacha", "lund ka bacha",
    "gandu", "gand", "jhaat", "jhaantu", "pichwada", "tatti", "bhosda"
    
]

def sanitize_message(text):
    if not text:
        return ""
    
    # 🔥 Logic: Pehle lambe gali wale words ko filter karo fir chhote 
    # Taaki 'madarchodwa' pura filter ho, sirf 'madarchod' portion nahi.
    sorted_words = sorted(BAD_WORDS, key=len, reverse=True)
    
    sanitized_text = text
    for word in sorted_words:
        # Case insensitive match
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        sanitized_text = pattern.sub("*" * len(word), sanitized_text)
    
    return sanitized_text
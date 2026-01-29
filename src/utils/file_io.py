import json
import csv
import logging
from typing import List, Dict, Any

def save_jsonl(data: List[Dict[str, Any]], filepath: str):
    """
    Saves a list of dictionaries to a JSON Lines file.
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            for entry in data:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except Exception as e:
        logging.error(f"Failed to save JSONL to {filepath}: {e}")

def load_jsonl(filepath: str) -> List[Dict[str, Any]]:
    """
    Loads data from a JSON Lines file.
    """
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                data.append(json.loads(line))
    except Exception as e:
        logging.error(f"Failed to load JSONL from {filepath}: {e}")
    return data

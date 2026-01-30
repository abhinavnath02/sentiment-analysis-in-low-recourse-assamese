import pandas as pd
import logging
from collections import Counter
import regex

def generate_stats(file_paths: list):
    """
    Generates statistics for one or multiple CSV datasets.
    
    Args:
        file_paths (list): List of paths to CSV files.
    """
    logger = logging.getLogger(__name__)
    
    total_docs = 0
    total_words = 0
    total_sentences = 0
    vocab = Counter()
    
    # Assamese sentence delimiter approximation (Danda | ?)
    # standard py regex might not handle all perfectly, but we try standard split
    
    for fp in file_paths:
        try:
            df = pd.read_csv(fp)
            # Check for text column
            col = 'processed_text' if 'processed_text' in df.columns else 'text'
            
            if col not in df.columns:
                logger.warning(f"Skipping {fp}: No text column found.")
                continue
                
            logger.info(f"Analyzing {fp}...")
            
            docs = df[col].dropna().astype(str).tolist()
            total_docs += len(docs)
            
            for doc in docs:
                # Word count (splitting by whitespace is crude but effective for stats)
                words = doc.split()
                total_words += len(words)
                vocab.update(words)
                
                # Sentence count (using Danda '।' and '?')
                sentences = regex.split(r'[।?]', doc)
                total_sentences += len([s for s in sentences if s.strip()])
                
        except Exception as e:
            logger.error(f"Error processing {fp}: {e}")

    stats = {
        "Total Documents": total_docs,
        "Total Words": total_words,
        "Total Sentences (approx)": total_sentences,
        "Vocabulary Size": len(vocab),
        "Avg Words/Doc": round(total_words / total_docs, 2) if total_docs else 0
    }
    
    return stats

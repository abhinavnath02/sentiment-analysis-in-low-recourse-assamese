import pandas as pd
import logging
import regex
from .text import remove_emojis

def aggregate_and_split(file_paths: list, output_path: str):
    """
    Combines multiple datasets, splits them into sentences, and creates 
    clean versions (with and without emojis).
    
    Args:
        file_paths (list): List of paths to cleaned CSV files.
        output_path (str): Path to save the final sentence-level dataset.
    """
    logger = logging.getLogger(__name__)
    all_sentences = []
    
    # Regex for splitting sentences: Danda (।), Question Mark (?), Exclamation (!)
    # We keep the delimiter to reconstruct if needed, but for now we just split.
    # We split on the punctuation but keep it attached to the previous sentence usually needed for NLP.
    # Simple split: `[।?!|]`
    split_pattern = r'([।?!|])'
    
    for fp in file_paths:
        try:
            df = pd.read_csv(fp)
            logger.info(f"Processing {fp}, rows: {len(df)}")
            
            # Identify columns
            text_col = 'processed_text' if 'processed_text' in df.columns else 'text'
            url_col = 'source_url' if 'source_url' in df.columns else 'Video Links'
            type_col = 'source_type' if 'source_type' in df.columns else 'channel_category' # Fallback
            
            for _, row in df.iterrows():
                doc = str(row.get(text_col, ''))
                source_url = row.get(url_col, '')
                
                # Determine source type more cleanly
                s_type = 'news' if 'news' in str(row.get(type_col, '')).lower() or 'article' in str(row.get(type_col, '')).lower() else 'social_media'
                if 'youtube' in fp.lower():
                    s_type = 'youtube_comment'
                
                # Split into sentences
                # Step 1: Split keeping delimiters
                parts = regex.split(split_pattern, doc)
                
                # Step 2: Re-assemble (sent + punct)
                sentences = []
                current_sent = ""
                for part in parts:
                    if regex.match(split_pattern, part):
                        current_sent += part
                        sentences.append(current_sent.strip())
                        current_sent = ""
                    else:
                        current_sent += part
                
                # Catch any trailing text
                if current_sent.strip():
                     sentences.append(current_sent.strip())
                     
                # Process each sentence
                for sent in sentences:
                    if len(sent) < 2: # Skip single chars/noise
                        continue
                        
                    sent_no_emoji = remove_emojis(sent).strip()
                    
                    if not sent_no_emoji: # Skip if only emoji
                        continue
                        
                    all_sentences.append({
                        'sentence_original': sent,
                        'sentence_no_emoji': sent_no_emoji,
                        'source_type': s_type,
                        'source_url': source_url
                    })
                    
        except Exception as e:
            logger.error(f"Failed to process {fp}: {e}")
            
    # Save final
    if all_sentences:
        out_df = pd.DataFrame(all_sentences)
        # Final deduplication at sentence level
        before_len = len(out_df)
        out_df = out_df.drop_duplicates(subset=['sentence_no_emoji'])
        logger.info(f"Generated {len(out_df)} unique sentences (dropped {before_len - len(out_df)} duplicates).")
        
        out_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"Saved merged dataset to {output_path}")
    else:
        logger.warning("No valid sentences found.")

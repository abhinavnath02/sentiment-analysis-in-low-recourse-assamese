import pandas as pd
import logging

def deduplicate_dataset(input_path: str, output_path: str, text_column: str = 'processed_text'):
    """
    Removes duplicate entries from the dataset based on the processed text.
    
    Args:
        input_path (str): Path to the input CSV file.
        output_path (str): Path where the deduplicated CSV will be saved.
        text_column (str): The column name to check for duplicates.
        
    Returns:
        dict: Statistics about the deduplication process.
    """
    logger = logging.getLogger(__name__)
    
    try:
        df = pd.read_csv(input_path)
    except Exception as e:
        logger.error(f"Failed to read input file {input_path}: {e}")
        return None

    if text_column not in df.columns:
        logger.error(f"Column '{text_column}' not found in dataset")
        return None

    original_count = len(df)
    logger.info(f"Original dataset size: {original_count}")

    # Deduplicate
    # keep='first' retains the first occurrence.
    df_deduped = df.drop_duplicates(subset=[text_column], keep='first')
    
    final_count = len(df_deduped)
    removed_count = original_count - final_count
    
    logger.info(f"Removed {removed_count} duplicates.")
    logger.info(f"Final dataset size: {final_count}")
    
    # Save
    try:
        df_deduped.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"Saved deduplicated data to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save output file {output_path}: {e}")
        return None
        
    return {
        "original_count": original_count,
        "final_count": final_count,
        "removed_count": removed_count
    }

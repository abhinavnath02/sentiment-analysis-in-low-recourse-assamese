"""
Main entry point for the Assamese Sentiment Analysis Data Pipeline.

This script handles the command-line interface for:
1. Scraping (YouTube, News)
2. Filtering (Language detection)
3. Cleaning (Normalization, PII removal)
"""

import argparse
import logging
import pandas as pd
import os
import time
from tqdm import tqdm
from urllib.parse import urlparse, parse_qs

from src.scrapers.youtube import YoutubeScraper
from src.scrapers.news import NewsScraper
from src.processing.linguistic import LinguisticValidator
from src.processing.text import clean_text
from src.processing.deduplication import deduplicate_dataset
from src.processing.aggregation import aggregate_and_split
from src.utils.stats import generate_stats

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/pipeline.log"),
            logging.StreamHandler()
        ]
    )

def extract_video_id(url):
    """Parses YouTube URL to get video ID."""
    try:
        query = urlparse(url).query
        params = parse_qs(query)
        if "v" in params:
            return params["v"][0]
    except:
        pass
    return None

def run_scraping_job(input_csv, output_file):
    logger = logging.getLogger(__name__)
    
    if not os.path.exists(input_csv):
        logger.error(f"Input file not found: {input_csv}")
        return

    logger.info(f"Loading target videos from {input_csv}")
    try:
        df = pd.read_csv(input_csv)
    except Exception as e:
        logger.error(f"Failed to read CSV: {e}")
        return

    if "Video Links" not in df.columns:
        logger.error("CSV must have a 'Video Links' column")
        return

    scraper = YoutubeScraper()
    all_comments = []
    
    # Iterate through videos
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing Videos"):
        url = row["Video Links"]
        category = row.get("Channel Category", "Unknown")
        channel = row.get("Youtube Channel", "Unknown")
        
        video_id = extract_video_id(url)
        if not video_id:
            logger.warning(f"Could not extract ID from {url}")
            continue
            
        logger.info(f"Scraping video {video_id} ({channel})")
        
        # Scrape
        raw_comments = scraper.scrape(video_id)
        
        count = 0
        for comment in raw_comments:
            text = comment.get('text', '')
            
            # 1. Processing: Unicode Normalization & Cleaning
            processed_text = clean_text(text)
            
            # 2. Filtering: Check if Assamese
            is_assamese = LinguisticValidator.is_assamese_script(processed_text, threshold=0.4)
            
            if is_assamese:
                # Enrich record
                comment['processed_text'] = processed_text
                comment['video_id'] = video_id
                comment['source_url'] = url
                comment['channel_category'] = category
                comment['channel_name'] = channel
                comment['is_assamese'] = True
                
                all_comments.append(comment)
                count += 1
        
        logger.info(f"Found {count} valid Assamese comments for video {video_id}")
        
    # Save Results
    if all_comments:
        out_df = pd.DataFrame(all_comments)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        # Append if file exists, else create new
        if os.path.exists(output_file):
             out_df.to_csv(output_file, mode='a', header=False, index=False, encoding='utf-8-sig')
        else:
             out_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        logger.info(f"Successfully saved {len(all_comments)} comments to {output_file}")
    else:
        logger.warning("No comments collected.")

def run_news_scraping_job(input_csv, output_file):
    logger = logging.getLogger(__name__)
    
    if not os.path.exists(input_csv):
        logger.error(f"Input file not found: {input_csv}")
        return

    logger.info(f"Loading target URLs from {input_csv}")
    try:
        df = pd.read_csv(input_csv)
    except Exception as e:
        logger.error(f"Failed to read CSV: {e}")
        return
        
    # Expecting column 'News Link' or 'URL'
    url_col = next((col for col in ['News Link', 'URL', 'Link'] if col in df.columns), None)
    if not url_col:
        logger.error("CSV must have a 'News Link', 'URL', or 'Link' column")
        return

    scraper = NewsScraper()
    all_articles = []

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing News Articles"):
        url = row[url_col]
        
        # Scrape
        articles = scraper.scrape(url)
        
        for article in articles:
            text = article.get('text', '')
            
            # 1. Processing
            processed_text = clean_text(text)
            
            # 2. Filtering
            # News articles are longer, so we can be stricter with threshold
            is_assamese = LinguisticValidator.is_assamese_script(processed_text, threshold=0.6)
            
            if is_assamese:
                article['processed_text'] = processed_text
                article['is_assamese'] = True
                all_articles.append(article)
    
    # Save
    if all_articles:
        out_df = pd.DataFrame(all_articles)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        if os.path.exists(output_file):
             out_df.to_csv(output_file, mode='a', header=False, index=False, encoding='utf-8-sig')
        else:
             out_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        logger.info(f"Successfully saved {len(all_articles)} articles to {output_file}")
    else:
        logger.warning("No articles collected.")


def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Assamese Sentiment Data Pipeline")
    
    subparsers = parser.add_subparsers(dest="command", help="Available pipeline stages")
    
    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Collect data from sources")
    scrape_parser.add_argument("--source", choices=["youtube", "news", "all"], default="youtube")
    scrape_parser.add_argument("--input_csv", type=str, help="Path to CSV with links")
    scrape_parser.add_argument("--output", type=str, default="data/processed/assamese_dataset.csv")
    
    # Filter command
    filter_parser = subparsers.add_parser("filter", help="Filter non-Assamese text")
    
    # Sort/Dedup command
    dedup_parser = subparsers.add_parser("dedup", help="Deduplicate a dataset")
    dedup_parser.add_argument("--input", type=str, required=True, help="Input CSV")
    dedup_parser.add_argument("--output", type=str, required=True, help="Output CSV")
    
    # Combine command
    combine_parser = subparsers.add_parser("combine", help="Split sentences and combine datasets")
    combine_parser.add_argument("--inputs", nargs='+', required=True, help="Input CSV files")
    combine_parser.add_argument("--output", type=str, required=True, help="Final Output CSV")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Generate dataset statistics")
    stats_parser.add_argument("--inputs", nargs='+', required=True, help="List of CSV files to analyze")
    
    args = parser.parse_args()
    
    if args.command == "scrape":
        logging.info(f"Starting scrape for source: {args.source}")
        if args.source == "youtube" and args.input_csv:
            run_scraping_job(args.input_csv, args.output)
        elif args.source == "news" and args.input_csv:
             run_news_scraping_job(args.input_csv, args.output)
        else:
            logging.warning("Please provide --input_csv")
            
    elif args.command == "dedup":
        logging.info(f"Deduplicating {args.input}")
        deduplicate_dataset(args.input, args.output)
        
    elif args.command == "combine":
        logging.info(f"Combining and splitting sentences...")
        aggregate_and_split(args.inputs, args.output)
        
    elif args.command == "stats":
        logging.info("Generating Statistics...")
        stats = generate_stats(args.inputs)
        print("\n=== Dataset Statistics ===")
        for k, v in stats.items():
            print(f"{k}: {v}")
        print("==========================\n")
            
    elif args.command == "filter":
        logging.info("Starting language filtering")

        # TODO: call filter module
    elif args.command == "clean":
        logging.info("Starting text cleaning")
        # TODO: call cleaner module
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

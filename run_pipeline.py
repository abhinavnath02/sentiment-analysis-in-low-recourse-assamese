"""
Main entry point for the Assamese Sentiment Analysis Data Pipeline.

This script handles the command-line interface for:
1. Scraping (YouTube, News)
2. Filtering (Language detection)
3. Cleaning (Normalization, PII removal)
"""

import argparse
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/pipeline.log"),
            logging.StreamHandler()
        ]
    )

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Assamese Sentiment Data Pipeline")
    
    subparsers = parser.add_subparsers(dest="command", help="Available pipeline stages")
    
    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Collect data from sources")
    scrape_parser.add_argument("--source", choices=["youtube", "news", "all"], default="all")
    
    # Filter command
    filter_parser = subparsers.add_parser("filter", help="Filter non-Assamese text")
    
    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Normalize and clean text")
    
    args = parser.parse_args()
    
    if args.command == "scrape":
        logging.info(f"Starting scrape for source: {args.source}")
        # TODO: call scraper modules
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

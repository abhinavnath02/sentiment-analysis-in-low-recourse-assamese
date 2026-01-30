import logging
import itertools
from datetime import datetime
from .base import BaseScraper
try:
    from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_RECENT
except ImportError:
    # Fallback to prevent crash if dependency isn't installed yet, but logging warning
    YoutubeCommentDownloader = None
    SORT_BY_RECENT = 0

class YoutubeScraper(BaseScraper):
    """
    Scrapes comments from YouTube videos using youtube-comment-downloader.
    Does not require an API key.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        if YoutubeCommentDownloader:
            self.downloader = YoutubeCommentDownloader()
        else:
            self.logger.error("youtube-comment-downloader not installed.")
            self.downloader = None

    def scrape(self, video_id: str):
        """
        Scrapes comments for a specific video ID.
        
        Args:
            video_id (str): The 11-character YouTube video ID.
            
        Yields:
            dict: Comment data including text, anonymized author info, etc.
        """
        if not self.downloader:
            self.logger.error("Scraper not initialized properly.")
            return

        self.logger.info(f"Starting scrape for video: {video_id}")
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        try:
            # We use SORT_BY_RECENT to get the newest comments which is better for current events
            # and often yields more raw/spontaneous text.
            generator = self.downloader.get_comments_from_url(url, sort_by=SORT_BY_RECENT)
            
            for comment in generator:
                anonymized = self._anonymize(comment)
                if anonymized:
                    yield anonymized
                    
        except Exception as e:
            self.logger.error(f"Error scraping video {video_id}: {e}")

    def _anonymize(self, raw_comment):
        """
        Strips PII from the comment object before it leaves the scoping.
        Input raw_comment keys usually: cid, text, time, author, channel, votes, photo, heart, reply
        """
        if not raw_comment or 'text' not in raw_comment:
            return None
            
        # STRICT WHITELISTING of fields
        # we drop 'author', 'channel', 'photo', 'cid' (unless needed for dedup internally, but we won't store it)
        clean_obj = {
            'text': raw_comment.get('text', ''),
            'votes': raw_comment.get('votes', '0'),
            'relative_time': raw_comment.get('time', ''), # "2 hours ago" - acceptable
            'scraped_timestamp': datetime.utcnow().isoformat(),
            'source_item_id': 'youtube_' + raw_comment.get('cid', '')[0:10], # Hashed or truncated ID for dedupe only
        }
        
        # Double check: ensure text is string
        if not isinstance(clean_obj['text'], str):
            clean_obj['text'] = str(clean_obj['text'])
            
        return clean_obj

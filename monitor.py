import time
import requests
import logging
from bs4 import BeautifulSoup
import telebot
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
from darkweb_monitor.models import db, Result

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TOR_PROXY = os.getenv('TOR_PROXY', 'socks5h://127.0.0.1:9050')
MAX_THREADS = int(os.getenv('MAX_THREADS', 5))

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    logger.error("Telegram token or chat ID not set in environment variables")
    exit(1)

# Initialize Telegram bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

class DarkWebMonitor:
    def __init__(self, urls: List[str], query: str, socketio=None):
        self.urls = urls
        self.query = query.lower()
        self.session = self._create_session()
        self.failure_counts = {url: 0 for url in urls}
        self.MAX_RETRIES = 3
        self.socketio = socketio

    def _create_session(self) -> requests.Session:
        """Create a requests session with Tor proxy."""
        session = requests.Session()
        session.proxies = {
            'http': TOR_PROXY,
            'https': TOR_PROXY
        }
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        return session

    def check_tor_health(self) -> bool:
        """Check if Tor proxy is responsive."""
        try:
            response = self.session.get('https://check.torproject.org/api/ip', timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('IsTor', False)
        except Exception as e:
            logger.error("Tor health check failed: %s", e)
            return False

    def _send_notification(self, message: str) -> None:
        """Send a notification via Telegram."""
        try:
            bot.send_message(TELEGRAM_CHAT_ID, message)
            logger.info("Notification sent: %s", message)
        except Exception as e:
            logger.error("Failed to send Telegram notification: %s", e)

    def _scrape_url(self, url: str) -> Optional[Dict]:
        """Scrape a single URL for the query."""
        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                if self.query in soup.get_text().lower():
                    self.failure_counts[url] = 0
                    result = {
                        'url': url,
                        'content': soup.get_text()[:500],
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    return result
                self.failure_counts[url] = 0
                return None
            except Exception as e:
                self.failure_counts[url] += 1
                logger.warning("Attempt %d failed for %s: %s", attempt + 1, url, e)
                if self.failure_counts[url] >= self.MAX_RETRIES:
                    self._send_notification(f"Failed to access {url} after {self.MAX_RETRIES} attempts")
                    logger.error("Max retries reached for %s", url)
                    return None
                time.sleep(2 ** attempt)
        return None

    def scrape_darkweb(self) -> None:
        """Scrape all URLs concurrently."""
        if not self.urls or not self.query:
            logger.warning("No URLs or query specified, skipping scrape")
            return
        
        logger.info("Starting dark web scan for query: %s", self.query)
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            results = executor.map(self._scrape_url, self.urls)
            new_results = [r for r in results if r is not None]
        
        if new_results:
            self._send_notification(f"Found {len(new_results)} matches for '{self.query}'")
            self._save_results(new_results)
            if self.socketio:
                self.socketio.emit('new_result', new_results, namespace='/')
                logger.info("Emitted %d new results via WebSocket", len(new_results))

    def _save_results(self, results: List[Dict]) -> None:
        """Save results to database."""
        try:
            for result in results:
                db_result = Result(
                    url=result['url'],
                    content=result['content'],
                    timestamp=result['timestamp']
                )
                db.session.add(db_result)
            db.session.commit()
            logger.info("Results saved to database")
        except Exception as e:
            db.session.rollback()
            logger.error("Failed to save results to database: %s", e)

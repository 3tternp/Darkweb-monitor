import threading
import time
import logging
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)
load_dotenv()

CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 900))

class Scheduler:
    def __init__(self, monitor):
        self.monitor = monitor
        self.thread = None
        self.running = False
        self.lock = threading.Lock()

    def is_running(self):
        with self.lock:
            return self.running

    def _run(self):
        while self.is_running():
            try:
                if not self.monitor.check_tor_health():
                    logger.warning("Tor is not responding, skipping scrape")
                    time.sleep(60)
                    continue
                self.monitor.scrape_darkweb()
                time.sleep(CHECK_INTERVAL)
            except Exception as e:
                logger.error("Error in scheduled task: %s", e)
                time.sleep(60)

    def start(self):
        with self.lock:
            if not self.running:
                self.running = True
                self.thread = threading.Thread(target=self._run)
                self.thread.daemon = True
                self.thread.start()
                logger.info("Scheduler started")

    def stop(self):
        with self.lock:
            if self.running:
                self.running = False
                self.thread.join()
                logger.info("Scheduler stopped")

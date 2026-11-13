"""
scrapers/base_scraper.py
========================
Abstract base class for all SILLA data scrapers.
Every concrete scraper must inherit from BaseScraper and implement collect().
"""

import abc
import logging
import time
import urllib.robotparser
from pathlib import Path

import requests
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import (
    RAW_DIR,
    USER_AGENT,
    REQUEST_DELAY_SECONDS,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    LOG_LEVEL,
)

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)


class BaseScraper(abc.ABC):
    """
    Abstract base for all scrapers.

    Parameters
    ----------
    source_name : str
        Human-readable name of the data source.
    source_url : str
        Root URL of the data source (used for robots.txt check).
    delay : float
        Seconds to wait between successive HTTP requests.
    """

    def __init__(
        self,
        source_name: str,
        source_url: str,
        delay: float = REQUEST_DELAY_SECONDS,
    ) -> None:
        self.source_name = source_name
        self.source_url = source_url.rstrip("/")
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.logger = logging.getLogger(self.__class__.__name__)
        self._robots_allowed: bool | None = None

    # ------------------------------------------------------------------
    # robots.txt compliance
    # ------------------------------------------------------------------
    def _check_robots_txt(self) -> bool:
        """
        Parse robots.txt and return True if our User-Agent is allowed
        to crawl the site root. Logs a warning (and returns False) if
        disallowed or if the file cannot be fetched.
        """
        robots_url = f"{self.source_url}/robots.txt"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        try:
            rp.read()
            allowed = rp.can_fetch(USER_AGENT, self.source_url + "/")
            if not allowed:
                self.logger.warning(
                    "robots.txt at %s DISALLOWS our agent. "
                    "Proceeding with public API endpoints only.",
                    robots_url,
                )
            else:
                self.logger.info("robots.txt check passed for %s", self.source_url)
            self._robots_allowed = allowed
            return allowed
        except Exception as exc:  # noqa: BLE001
            self.logger.warning(
                "Could not read robots.txt from %s (%s). Assuming allowed.",
                robots_url,
                exc,
            )
            self._robots_allowed = True
            return True

    # ------------------------------------------------------------------
    # HTTP requests with retry + exponential back-off
    # ------------------------------------------------------------------
    def _make_request(
        self,
        url: str,
        retries: int = MAX_RETRIES,
        params: dict | None = None,
    ) -> requests.Response | None:
        """
        Fetch *url* with up to *retries* attempts using exponential back-off.

        Returns the Response on success, or None after all attempts fail.
        Always waits self.delay seconds before each request to be polite.
        """
        for attempt in range(1, retries + 1):
            try:
                self.logger.debug(
                    "GET %s (attempt %d/%d)", url, attempt, retries
                )
                time.sleep(self.delay)
                resp = self.session.get(
                    url, params=params, timeout=REQUEST_TIMEOUT
                )
                resp.raise_for_status()
                return resp
            except requests.exceptions.HTTPError as exc:
                status = exc.response.status_code if exc.response else "?"
                self.logger.warning(
                    "HTTP %s on %s (attempt %d/%d)", status, url, attempt, retries
                )
                if status == 404:
                    return None  # no point retrying
            except requests.exceptions.RequestException as exc:
                self.logger.warning(
                    "Request error on %s: %s (attempt %d/%d)",
                    url, exc, attempt, retries,
                )
            # exponential back-off
            if attempt < retries:
                backoff = self.delay * (2 ** (attempt - 1))
                self.logger.debug("Backing off %.1f s before retry.", backoff)
                time.sleep(backoff)

        self.logger.error("All %d attempts failed for %s", retries, url)
        return None

    # ------------------------------------------------------------------
    # Saving raw data
    # ------------------------------------------------------------------
    def _save_raw(self, df: pd.DataFrame, filename: str) -> Path:
        """
        Save *df* as a CSV to data/raw/<filename>.
        Creates the raw directory if missing.
        Returns the full path.
        """
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        out_path = RAW_DIR / filename
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
        self.logger.info(
            "Saved %d rows → %s", len(df), out_path
        )
        return out_path

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------
    @abc.abstractmethod
    def collect(self) -> None:
        """
        Run the full collection workflow for this source.
        Implementations must call _save_raw() at the end.
        """

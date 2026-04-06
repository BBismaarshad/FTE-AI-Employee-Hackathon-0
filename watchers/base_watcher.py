"""
Base Watcher - Abstract base class for all watchers.

All watchers follow this pattern:
1. Check for updates from external source
2. Create action files in Needs_Action folder
3. Orchestrator processes these files and triggers Claude
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime


class BaseWatcher(ABC):
    """Abstract base class for all AI Employee watchers."""

    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)

        # Ensure Needs_Action folder exists
        self.needs_action.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check for new items to process.

        Returns:
            list: List of new items that need action
        """
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Create a .md action file in Needs_Action folder.

        Args:
            item: The item to create an action file for

        Returns:
            Path: Path to the created action file
        """
        pass

    def run(self):
        """Main watcher loop - continuously monitor for updates."""
        self.logger.info(f'Starting {self.__class__.__name__}')
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    filepath = self.create_action_file(item)
                    self.logger.info(f'Created action file: {filepath}')
            except Exception as e:
                self.logger.error(f'Error in {self.__class__.__name__}: {e}', exc_info=True)
            time.sleep(self.check_interval)

    def run_once(self) -> int:
        """
        Run a single check cycle (useful for testing/scheduled runs).

        Returns:
            int: Number of action files created
        """
        try:
            items = self.check_for_updates()
            count = 0
            for item in items:
                filepath = self.create_action_file(item)
                self.logger.info(f'Created action file: {filepath}')
                count += 1
            return count
        except Exception as e:
            self.logger.error(f'Error in {self.__class__.__name__}: {e}', exc_info=True)
            return 0


def setup_logging(name: str, log_file: str = None):
    """
    Setup logging for a watcher.

    Args:
        name: Logger name
        log_file: Optional path to log file
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

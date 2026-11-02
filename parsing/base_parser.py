from abc import ABC, abstractmethod

class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str):
        """Abstract method for parsing report files."""
        pass

    @abstractmethod
    def score(self, raw_text: str) -> int:
        """Abstract method for scoring text match confidence."""
        pass
from abc import ABC, abstractmethod
from typing import Dict, Type
import re
from parsing.type_a_parser import TypeAParser
from parsing.type_b_parser import TypeBParser
from parsing.base_parser import BaseParser

class ReportClassifier:
    """
    Registry-based classifier that uses scoring to determine the best matching report type.
    Allows dynamic registration of new report types without modifying this class (Open/Closed Principle).
    """

    def __init__(self):
        # Internal dictionary mapping report type identifiers to their respective parser classes
        self._parsers: Dict[str, Type[BaseParser]] = {}
        self.register_parser(report_type="TYPE_A", parser_class=TypeAParser)
        self.register_parser(report_type="TYPE_B", parser_class=TypeBParser)
    def register_parser(self, report_type: str, parser_class: Type[BaseParser]) -> None:
        """
        Registers a parser class for a given report type identifier.

        Args:
            report_type (str): The unique identifier for the report type (e.g., "TYPE_A", "TYPE_B").
            parser_class (Type[BaseParser]): The parser class implementation.
        """
        self._parsers[report_type] = parser_class

    def _normalize_text(self, text: str) -> str:
        """
        Normalizes the raw OCR text by standardizing quotes, removing table pipes,
        converting to lowercase, and normalizing whitespace.

        Args:
            text (str): The raw text to normalize.

        Returns:
            str: The cleaned and normalized text.
        """
        if not text:
            return ""
        text = text.replace('”', '"').replace('“', '"').replace('״', '"').replace('׳', "'")
        text = text.replace('|', ' ')
        text = text.lower()
        text = re.sub(r'[ \t]+', ' ', text)
        return text

    def classify(self, raw_text: str) -> str:
        """
        Evaluates the raw text against all registered parsers by invoking their score method,
        and returns the report type identifier that achieves the highest confidence score.

        Args:
            raw_text (str): The raw text extracted from the PDF via OCR.

        Returns:
            str: The identified report type identifier.

        Raises:
            ValueError: If no parsers are registered or if no parser achieves a positive score.
        """
        # Ensure that parsers have been registered before attempting classification
        if not self._parsers:
            raise ValueError("No parsers are registered in the classifier.")

        # Normalize the raw text before passing it to the parsers
        normalized_text = self._normalize_text(raw_text)

        best_report_type = None
        highest_score = -1

        # Iterate through all registered parsers to evaluate scores
        for report_type, parser_cls in self._parsers.items():
            parser_instance = parser_cls()
            current_score = parser_instance.score(normalized_text)

            # Track the parser that yields the highest match score
            if current_score > highest_score:
                highest_score = current_score
                best_report_type = report_type

        # Validate that a meaningful match was found
        if highest_score <= 0 or not best_report_type:
            raise ValueError("Could not classify the raw text: all parser scores were zero or negative.")

        return best_report_type
import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from core.lead_processor import LeadProcessor


class LeadProcessorLanguageTests(unittest.TestCase):
    def setUp(self):
        self.processor = LeadProcessor.__new__(LeadProcessor)
        self.processor.llm = Mock()
        self.processor.llm.invoke.return_value = SimpleNamespace(content=json.dumps({
            "company_size": None,
            "industry": None,
            "product_interest": None,
            "use_case": "Automatizacion de documentos",
            "pain_points": None,
            "budget": None,
            "timeline": None,
            "purchase_intent": "evaluating",
            "action_requested": None,
            "missing_info": ["budget"],
            "language": "Spanish",
        }))

    def test_auto_detect_uses_language_returned_by_model(self):
        result = self.processor.extract_lead_info({
            "name": "Test User",
            "email": "test@example.test",
            "company": "Example Co",
            "job_title": "Manager",
            "message": "Buscamos automatizar documentos.",
            "language": "Auto-detect",
        })

        self.assertEqual(result.language, "Spanish")
        self.assertIn("Requested Language is Auto-detect", self.processor.llm.invoke.call_args.args[0])

    def test_explicit_language_selection_is_preserved(self):
        result = self.processor.extract_lead_info({
            "name": "Test User",
            "email": "test@example.test",
            "company": "Example Co",
            "job_title": "Manager",
            "message": "We need document automation.",
            "language": "English",
        })

        self.assertEqual(result.language, "English")


if __name__ == "__main__":
    unittest.main()
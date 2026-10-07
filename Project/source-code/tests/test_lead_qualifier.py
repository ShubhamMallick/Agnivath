import unittest

from core.lead_qualifier import LeadQualifier


class LeadQualifierFallbackTests(unittest.TestCase):
    def test_handles_missing_optional_fields(self):
        qualifier = LeadQualifier(provider="groq")
        lead = {
            "name": "Test User",
            "company": "Acme",
            "job_title": None,
            "company_size": None,
            "industry": None,
            "product_interest": None,
            "use_case": None,
            "pain_points": None,
            "budget": None,
            "timeline": None,
            "purchase_intent": None,
            "action_requested": None,
            "missing_info": ["budget"],
        }

        result = qualifier.fallback_qualification(lead, "L1")

        self.assertIn(result.priority, {"HIGH", "MEDIUM", "LOW"})
        self.assertTrue(0 <= result.score <= 100)
        self.assertIsInstance(result.reasons, list)
        self.assertEqual(result.missing_info, ["budget"])

    def test_scores_high_intent_leads_correctly(self):
        qualifier = LeadQualifier(provider="groq")
        lead = {
            "name": "CTO",
            "company": "Enterprise Co",
            "job_title": "CTO",
            "company_size": "enterprise",
            "industry": "technology",
            "product_interest": "Enterprise AI Platform",
            "use_case": "customer support automation",
            "pain_points": "slow response times",
            "budget": "approved",
            "timeline": "2 months",
            "purchase_intent": "high",
            "action_requested": "demo",
            "missing_info": ["budget"],
        }

        result = qualifier.fallback_qualification(lead, "L2")

        self.assertEqual(result.priority, "HIGH")
        self.assertGreaterEqual(result.score, 70)
        self.assertIn("Requested demo or call", result.reasons)


if __name__ == "__main__":
    unittest.main()

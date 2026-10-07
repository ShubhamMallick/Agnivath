import tempfile
import unittest
from pathlib import Path

from core.lead_store import LeadStore
from core.notifier import Notifier


class LeadStoreTests(unittest.TestCase):
    def test_lead_survives_store_recreation(self):
        lead = {
            "lead_id": "L1",
            "original_data": {"name": "Example"},
            "extracted_info": {"company": "Example Co"},
            "qualification": {"priority": "HIGH", "score": 80},
            "notification_sent": True,
            "created_at": "2026-10-07T10:00:00",
        }

        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "leads.sqlite3"
            LeadStore(database_path).save(lead)

            reopened_store = LeadStore(database_path)

            self.assertEqual(reopened_store.get_lead("L1"), lead)
            self.assertEqual(reopened_store.list_leads(), [lead])

    def test_saving_existing_id_updates_record_without_duplicate(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            store = LeadStore(Path(temporary_directory) / "leads.sqlite3")
            lead = {
                "lead_id": "L1",
                "original_data": {},
                "extracted_info": {"company": "Before"},
                "qualification": {"priority": "MEDIUM", "score": 55},
                "notification_sent": False,
                "created_at": "2026-10-07T10:00:00",
            }
            store.save(lead)
            lead["extracted_info"]["company"] = "After"
            store.save(lead)

            records = store.list_leads()
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["extracted_info"]["company"], "After")

    def test_notifications_persist_filter_and_clear_without_email(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            store = LeadStore(Path(temporary_directory) / "leads.sqlite3")
            notifier = Notifier(store)
            notifier.send_notification(
                {"lead_id": "L1", "priority": "HIGH", "score": 85, "next_action": "Schedule demo"},
                {"name": "Example", "company": "Example Co", "email": "private@example.test"},
            )

            reopened_notifier = Notifier(LeadStore(Path(temporary_directory) / "leads.sqlite3"))
            notifications = reopened_notifier.get_notifications("MEDIUM")

            self.assertEqual(len(notifications), 1)
            self.assertEqual(notifications[0]["lead_id"], "L1")
            self.assertNotIn("email", notifications[0])
            self.assertEqual(reopened_notifier.clear_notifications(), 1)
            self.assertEqual(reopened_notifier.get_notifications("LOW"), [])


if __name__ == "__main__":
    unittest.main()
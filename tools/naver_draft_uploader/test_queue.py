import tempfile
import unittest
from pathlib import Path

from queue import QueueItem, QueueStore


class QueueTests(unittest.TestCase):
    def test_enqueue_is_idempotent_by_content_id(self):
        with tempfile.TemporaryDirectory() as d:
            q = QueueStore(Path(d) / "queue.json")
            item = QueueItem("supportpick-1", "/tmp/1.json")
            self.assertEqual("ENQUEUED", q.enqueue_once(item))
            self.assertEqual("DUPLICATE_QUEUE_ITEM", q.enqueue_once(item))
            self.assertEqual(1, len(q.load()))

    def test_next_runnable_is_serial(self):
        with tempfile.TemporaryDirectory() as d:
            q = QueueStore(Path(d) / "queue.json")
            q.enqueue_once(QueueItem("supportpick-1", "/tmp/1.json"))
            q.enqueue_once(QueueItem("supportpick-2", "/tmp/2.json"))
            self.assertEqual("supportpick-1", q.next_runnable().content_id)
            q.update_state("supportpick-1", "VERIFIED")
            self.assertEqual("supportpick-2", q.next_runnable().content_id)


if __name__ == "__main__":
    unittest.main()

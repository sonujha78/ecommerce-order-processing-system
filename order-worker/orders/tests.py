from django.test import SimpleTestCase


class SanityTest(SimpleTestCase):
    def test_basic_sanity(self):
        # Placeholder sanity test — confirms the Django test runner works,
        # without requiring a live MySQL connection (SimpleTestCase skips
        # test-database creation). Full integration tests would need a
        # MySQL service configured in CI.
        self.assertEqual(1 + 1, 2)

import unittest

from app.data import str_to_pseudonym


class TestData(unittest.TestCase):
    def test_pseudonym(self) -> None:
        self.assertIsNone(str_to_pseudonym('invalid'))
        self.assertIsNone(str_to_pseudonym(''))
        self.assertIsNotNone(str_to_pseudonym('d77a2d47-9a78-4557-ab9a-c86132d1078d'))

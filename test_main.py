import unittest
from datetime import datetime
from unittest.mock import patch

from main import AddressBook, Birthday, Record, add_contact, change_contact, show_birthday


class AssistantTests(unittest.TestCase):
    def test_birthday_validation(self):
        self.assertEqual(str(Birthday("29.02.2000")), "29.02.2000")
        for value in ("29.02.2001", "31.04.2000", "1.01.2000", "2000-01-01"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                Birthday(value)

    def test_contact_errors_do_not_mutate_book(self):
        book = AddressBook()
        add_contact(["Ann", "123"], book)
        self.assertEqual(len(book), 0)
        add_contact(["Ann", "0123456789"], book)
        change_contact(["Ann", "0123456789", "invalid"], book)
        self.assertEqual(book.find("Ann").phones[0].value, "0123456789")
        self.assertEqual(show_birthday(["Missing"], book), "Contact not found.")

    def upcoming(self, today, entries):
        book = AddressBook()
        for name, birthday in entries:
            record = Record(name)
            if birthday:
                record.add_birthday(birthday)
            book.add_record(record)
        with patch("main.datetime") as clock:
            clock.today.return_value = datetime.strptime(today, "%d.%m.%Y")
            clock.strptime.side_effect = datetime.strptime
            return book.get_upcoming_birthdays()

    def test_window_and_weekend(self):
        self.assertEqual(self.upcoming("23.10.2026", [
            ("Today", "23.10.2000"), ("Saturday", "24.10.2000"),
            ("Sunday", "25.10.2000"), ("Last", "29.10.2000"),
            ("Outside", "30.10.2000"), ("Unknown", None),
        ]), [
            {"name": "Today", "birthday": "23.10.2026"},
            {"name": "Saturday", "birthday": "26.10.2026"},
            {"name": "Sunday", "birthday": "26.10.2026"},
            {"name": "Last", "birthday": "29.10.2026"},
        ])

    def test_year_boundary(self):
        self.assertEqual(self.upcoming("29.12.2026", [("New year", "02.01.2000")]),
                         [{"name": "New year", "birthday": "04.01.2027"}])

    def test_leap_day(self):
        self.assertEqual(self.upcoming("27.02.2026", [("Leap", "29.02.2000")]),
                         [{"name": "Leap", "birthday": "02.03.2026"}])


if __name__ == "__main__":
    unittest.main()

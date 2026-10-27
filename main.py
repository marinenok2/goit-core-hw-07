from collections import UserDict
from datetime import datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if len(value) != 10 or not value.isascii() or not value.isdigit():
            raise ValueError("Phone must contain exactly 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            date = datetime.strptime(value, "%d.%m.%Y")
            if date.strftime("%d.%m.%Y") != value:
                raise ValueError
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(date)

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def find_phone(self, phone):
        for item in self.phones:
            if item.value == phone:
                return item
        return None

    def remove_phone(self, phone):
        item = self.find_phone(phone)
        if item is None:
            raise ValueError("Phone not found.")
        self.phones.remove(item)

    def edit_phone(self, old_phone, new_phone):
        item = self.find_phone(old_phone)
        if item is None:
            raise ValueError("Phone not found.")
        new_item = Phone(new_phone)
        index = self.phones.index(item)
        self.phones[index] = new_item

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = []
        for phone in self.phones:
            phones.append(str(phone))
        result = f"Contact name: {self.name}, phones: {', '.join(phones)}"
        if self.birthday is not None:
            result += f", birthday: {self.birthday}"
        return result


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming = []

        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday = record.birthday.value.date()
            year = today.year
            # Якщо день народження вже минув, беремо наступний рік.
            if (birthday.month, birthday.day) < (today.month, today.day):
                year += 1

            try:
                next_birthday = birthday.replace(year=year)
            except ValueError:
                # 29 лютого у невисокосному році замінюємо на 28 лютого.
                next_birthday = birthday.replace(year=year, day=28)

            days_left = (next_birthday - today).days
            if 0 <= days_left < 7:
                if next_birthday.weekday() == 5:
                    next_birthday += timedelta(days=2)
                elif next_birthday.weekday() == 6:
                    next_birthday += timedelta(days=1)

                upcoming.append({
                    "name": record.name.value,
                    "birthday": next_birthday.strftime("%d.%m.%Y")
                })

        return upcoming


# Декоратор обробляє помилки введення, щоб бот продовжував працювати.
def input_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except KeyError:
            return "Contact not found."
        except ValueError as error:
            return str(error)
        except IndexError:
            return "Enter the required arguments."
    return wrapper


def parse_input(user_input):
    parts = user_input.split()
    if not parts:
        return "", []
    command = parts[0].lower()
    args = parts[1:]
    return command, args


@input_error
def add_contact(args, book):
    if len(args) != 2:
        return "Usage: add <name> <phone>"
    name, phone = args
    record = book.find(name)
    if record is None:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return "Contact added."
    record.add_phone(phone)
    return "Contact updated."


@input_error
def change_contact(args, book):
    if len(args) != 3:
        return "Usage: change <name> <old_phone> <new_phone>"
    name, old_phone, new_phone = args
    record = book[name]
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args, book):
    if len(args) != 1:
        return "Usage: phone <name>"
    record = book[args[0]]
    phones = []
    for phone in record.phones:
        phones.append(str(phone))
    return ", ".join(phones)


@input_error
def show_all(args, book):
    if args:
        return "Usage: all"
    if not book:
        return "Address book is empty."
    contacts = []
    for record in book.values():
        contacts.append(str(record))
    return "\n".join(contacts)


@input_error
def add_birthday(args, book):
    if len(args) != 2:
        return "Usage: add-birthday <name> <DD.MM.YYYY>"
    name, birthday = args
    record = book[name]
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    if len(args) != 1:
        return "Usage: show-birthday <name>"
    record = book[args[0]]
    if record.birthday is None:
        return "Birthday is not set."
    return str(record.birthday)


@input_error
def birthdays(args, book):
    if args:
        return "Usage: birthdays"
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays."
    result = []
    for person in upcoming:
        result.append(f"{person['name']}: {person['birthday']}")
    return "\n".join(result)


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        try:
            user_input = input("Enter a command: ")
        except (EOFError, KeyboardInterrupt):
            print("\nGood bye!")
            break
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        elif command:
            print("Invalid command.")


if __name__ == "__main__":
    main()

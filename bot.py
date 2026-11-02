from collections import UserDict
from datetime import datetime, date, timedelta
from functools import wraps

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
	pass

class Phone(Field):
    def __init__(self, value):         
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain 10 digits.")
        super().__init__(value)
        
class Birthday(Field):
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        phone = Phone(phone)
        self.phones.append(phone)
        
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None
        
    def remove_phone(self, phone):
         self.phones = [p for p in self.phones if p.value != phone]
         
    def edit_phone(self, old, new):
        new = Phone(new)
        for p in self.phones:
            if p.value == old:
                p.value = new.value
                return
        raise ValueError("Old phone number not found.")
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
        
    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        birthday = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones}{birthday}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        self.data.pop(name, None)
    
    def get_upcoming_birthdays(self):
        today = date.today()
        upcoming = []

        for record in self.data.values():
            if record.birthday is None:
                continue

            bd = record.birthday.date
            try:
                bd_this_year = bd.replace(year=today.year)
            except ValueError:
                bd_this_year = date(today.year, 2, 28)

            if bd_this_year < today:
                try:
                    bd_this_year = bd.replace(year=today.year + 1)
                except ValueError:
                    bd_this_year = date(today.year + 1, 2, 28)

            if 0 <= (bd_this_year - today).days <= 7:
                congrats = bd_this_year
                if congrats.weekday() == 5: 
                    congrats += timedelta(days=2)
                elif congrats.weekday() == 6: 
                    congrats += timedelta(days=1)
                upcoming.append({
                    "name": record.name.value,
                    "birthday": congrats.strftime("%d.%m.%Y"),
                })

        return upcoming    
    
    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())
    

def input_error(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Write your name"

    return inner

def input_data(user_input):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    cmd, *args = parts
    return cmd.lower(), args

@input_error
def add_contact(args, book: AddressBook): 
    if len(args) < 2:
        raise ValueError("Give me name and phone please.")
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    if len(args) < 3:
        raise ValueError("Give me name, old phone and new phone please.")
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError(name)
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError(name)
    if not record.phones:
        return "No phones saved for this contact."
    return "; ".join(p.value for p in record.phones)

@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "No contacts saved."
    return str(book)

@input_error
def add_birthday(args, book: AddressBook):  
    if len(args) < 2:
        raise ValueError("Give me name and birthday (DD.MM.YYYY) please.")
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError(name)
    record.add_birthday(birthday)
    return "Birthday added."

@input_error
def show_birthday(args, book: AddressBook):  
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError(name)
    if record.birthday is None:
        return "Birthday is not set for this contact."
    return record.birthday.value


@input_error
def birthdays(args, book: AddressBook):  
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    return "\n".join(f"{item['name']}: {item['birthday']}" for item in upcoming)


def main():
    book = AddressBook() 
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = input_data(user_input)

        if command in ("close", "exit"):
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
            print(show_all(book))
        elif command == "add-birthday":  
            print(add_birthday(args, book))
        elif command == "show-birthday":  
            print(show_birthday(args, book))
        elif command == "birthdays":  
            print(birthdays(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
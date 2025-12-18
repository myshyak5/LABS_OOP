from typing import Any
from abc import ABC, abstractmethod


class EventHandler(ABC):
    @abstractmethod
    def handle(self, sender: Any, args: Any) -> None:
        ...


class Event:
    def __init__(self) -> None:
        self._handlers = []

    def __iadd__(self, handler: EventHandler) -> 'Event':
        if handler not in self._handlers:
            self._handlers.append(handler)
        return self
    
    def __isub__(self, handler: EventHandler) -> 'Event':
        if handler in self._handlers:
            self._handlers.remove(handler)
        return self
    
    def __call__(self, sender: Any, args: Any) -> None:
        for handler in self._handlers:
            handler.handle(sender, args)


class PropertyChangedEventArgs:
    def __init__(self, property_name: str) -> None:
        self.property_name = property_name

    def __str__(self) -> str:
        return f"PropertyChanged: {self.property_name}"
    

class PropertyChangedEvent(EventHandler):
    def handle(self, sender: Any, args: PropertyChangedEventArgs) -> None:
        print(f"[PropertyChangedHandler] {sender.__class__.__name__}: {args}")


class PropertyChangingEventArgs:
    def __init__(self, property_name: str,
                 old_value: Any,
                 new_value: Any) -> None:
        self.property_name = property_name
        self.old_value = old_value
        self.new_value = new_value
        self.can_change = True

    def __str__(self) -> str:
        return f"PropertyChanging: {self.property_name} from {self.old_value} to {self.new_value}"
    

class ForIntValidator(EventHandler):
    def __init__(self,
            min_value: int,
            max_value: int,
            property_names: list) -> None:
        self.min_value = min_value
        self.max_value = max_value
        self.property_names = property_names
    
    def handle(self, sender: Any, args: PropertyChangingEventArgs) -> None:
        if (args.property_name in self.property_names and 
            isinstance(args.new_value, int) and 
            (args.new_value < self.min_value or args.new_value > self.max_value)):

            print(f"[ForIntValidator] {args.property_name} должно быть от {self.min_value} до {self.max_value}! \
Изменение {args.property_name} отменено.")
            args.can_change = False

        elif args.property_name in self.property_names:
            print(f"[ForIntValidator] Изменение {args.property_name} разрешено")


class PropertyChangingEvent(EventHandler):
    def handle(self, sender: Any, args: PropertyChangingEventArgs) -> None:
        if args.property_name == "email" and "@" not in str(args.new_value):
            print(f"[PropertyChangingEvent] {args.property_name} должен содержать @! \
Изменение {args.property_name} отменено.")
            args.can_change = False
        elif args.property_name == "name" and len(str(args.new_value).strip()) == 0:
            print(f"[PropertyChangingEvent] {args.property_name} не может быть пустым! \
Изменение {args.property_name} отменено.")
            args.can_change = False
        elif args.property_name == "nickname" and len(str(args.new_value).strip()) == 0:
            print(f"[PropertyChangingEvent] {args.property_name} не может быть пустым! \
Изменение {args.property_name} отменено.")
            args.can_change = False
        elif args.property_name in ["email", "name", "nickname"]:
            print(f"[PropertyChangingEvent] Изменение {args.property_name} разрешено")


class PropertyBase:
    def __init__(self) -> None:
        self.property_changing = Event()
        self.property_changed = Event()


class User(PropertyBase):
    def __init__(self, name: str, age: int, email: str) -> None:
        super().__init__()
        self._name = name
        self._age = age
        self._email = email

    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        if self._name != value:
            changing_args = PropertyChangingEventArgs("name", self._name, value)
            self.property_changing(self, changing_args)
            if changing_args.can_change:
                self._name = value
                self.property_changed(self, PropertyChangedEventArgs("name"))

    @property
    def age(self) -> int:
        return self._age
    
    @age.setter
    def age(self, value: int) -> None:
        if self._age != value:
            changing_args = PropertyChangingEventArgs("age", self._age, value)
            self.property_changing(self, changing_args)
            if changing_args.can_change:
                self._age = value
                self.property_changed(self, PropertyChangedEventArgs("age"))

    @property
    def email(self) -> str:
        return self._email
    
    @email.setter
    def email(self, value: str) -> None:
        if self._email != value:
            changing_args = PropertyChangingEventArgs("email", self._email, value)
            self.property_changing(self, changing_args)
            if changing_args.can_change:
                self._email = value
                self.property_changed(self, PropertyChangedEventArgs("email"))
    
    def __str__(self) -> str:
        return f"User(name='{self.name}', age={self.age}, email='{self.email}')"


class Player(PropertyBase):
    def __init__(self, nickname: str, health: int, death: int) -> None:
        super().__init__()
        self._nickname = nickname
        self._health = health
        self._death = death

    @property
    def nickname(self) -> str:
        return self._nickname
    
    @nickname.setter
    def nickname(self, value: str) -> None:
        if self._nickname != value:
            changing_args = PropertyChangingEventArgs("nickname", self._nickname, value)
            self.property_changing(self, changing_args)
            if changing_args.can_change:
                self._nickname = value
                self.property_changed(self, PropertyChangedEventArgs("nickname"))

    @property
    def health(self) -> int:
        return self._health
    
    @health.setter
    def health(self, value: int) -> None:
        if self._health != value:
            changing_args = PropertyChangingEventArgs("health", self._health, value)
            self.property_changing(self, changing_args)
            if changing_args.can_change:
                self._health = value
                self.property_changed(self, PropertyChangedEventArgs("health"))

    @property
    def death(self) -> int:
        return self._death
    
    @death.setter
    def death(self, value: int) -> None:
        if self._death != value:
            changing_args = PropertyChangingEventArgs("death", self._death, value)
            self.property_changing(self, changing_args)
            if changing_args.can_change:
                self._death = value
                self.property_changed(self, PropertyChangedEventArgs("death"))
    
    def __str__(self) -> str:
        return f"Player(nickname='{self.nickname}', health={self.health}, death={self.death})"


def main():
    changed_handler = PropertyChangedEvent()
    validator = PropertyChangingEvent()
    
    age_validator = ForIntValidator(min_value=0, max_value=150, property_names=["age"])
    health_death_validator = ForIntValidator(min_value=0, max_value=100, property_names=["health", "death"])
    
    print("=== ТЕСТ USER ===")
    user = User("NewUser", 18, "NewUser@mail.com")
    user.property_changed += changed_handler
    user.property_changing += validator
    user.property_changing += age_validator
    print(f"Начальное состояние: {user}")
    
    user.name = input("Введите новое имя: ")
    try:
        user.age = int(input("Введите новый возраст: "))
    except ValueError as e:
        print(f"Age error: Неверный формат числа")
    user.email = input("Введите новый email: ")
    print(f"\nФинальное состояние: {user}")
    
    print("\n=== ТЕСТ PLAYER ===")
    player = Player("NewPlayer", 100, 0)
    player.property_changed += changed_handler
    player.property_changing += validator
    player.property_changing += health_death_validator
    print(f"Начальное состояние: {player}")
    
    player.nickname = input("Введите новый никнейм: ")
    try:
        player.health = int(input("Введите новое значение здоровья: "))
    except ValueError as e:
        print(f"Health error: Неверный формат числа")
    try:
        player.death = int(input("Введите новое количество смертей: "))
    except ValueError as e:
        print(f"Death error: Неверный формат числа")
    
    print(f"\nФинальное состояние: {player}")


if __name__ == '__main__':
    main()
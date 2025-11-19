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
                 new_value: Any,
                 can_change: bool) -> None:
        self.property_name = property_name
        self.old_value = old_value
        self.new_value = new_value
        self.can_change = can_change

    def __str__(self) -> str:
        return f"PropertyChanging: {self.property_name} from {self.old_value}\
              to {self.new_value}"
    

class PropertyChangingEvent(EventHandler):
    def handle(self, sender: Any, args: PropertyChangingEventArgs) -> None:
        if args.property_name == "age" and args.new_value < 0:
            print(f"[Validator] {args.property_name} не может быть отрицательным! Отмена изменения.")
            args.can_change = False
        elif args.property_name == "email" and "@" not in str(args.new_value):
            print(f"[Validator] {args.property_name} должен содержать @! Отмена изменения.")
            args.can_change = False
        elif args.property_name == "health" and (args.new_value < 0 or args.new_value > 100):
            print(f"[Validator] {args.property_name} должно быть от 0 до 100! Отмена изменения.")
            args.can_change = False
        elif args.property_name == "death" and args.new_value < 0:
            print(f"[Validator] {args.property_name} не может быть отрицательным! Отмена изменения.")
            args.can_change = False
        elif args.property_name == "name" and len(str(args.new_value).strip()) == 0:
            print(f"[Validator] {args.property_name} не может быть пустым! Отмена изменения.")
            args.can_change = False
        elif args.property_name == "nickname" and len(str(args.new_value).strip()) == 0:
            print(f"[Validator] {args.property_name} не может быть пустым! Отмена изменения.")
            args.can_change = False
        else:
            print(f"[Validator] Изменение {args.property_name} разрешено")


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
            changing_args = PropertyChangingEventArgs("name", self._name, value, True)
            self.property_changing(self, changing_args)
            if changing_args.can_change:
                self._name = value
                self.property_changed(self, PropertyChangedEventArgs("name"))
            else:
                print(f"Изменение имени отменено")

    @property
    def age(self) -> int:
        return self._age
    
    @age.setter
    def age(self, value: int) -> None:
        if self._age != value:
            changing_args = PropertyChangingEventArgs("age", self._age, value, True)
            self.property_changing(self, changing_args)
            if changing_args.can_change:
                self._age = value
                self.property_changed(self, PropertyChangedEventArgs("age"))
            else:
                print(f"Изменение возраста отменено")

    @property
    def email(self) -> str:
        return self._email
    
    @email.setter
    def email(self, value: str) -> None:
        if self._email != value:
            changing_args = PropertyChangingEventArgs("email", self._email, value, True)
            self.property_changing(self, changing_args)
            if changing_args.can_change:
                self._email = value
                self.property_changed(self, PropertyChangedEventArgs("email"))
            else:
                print(f"Изменение почты отменено")
    
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
            changing_args = PropertyChangingEventArgs("nickname", self._nickname, value, True)
            self.property_changing(self, changing_args)
            if changing_args.can_change:
                self._nickname = value
                self.property_changed(self, PropertyChangedEventArgs("nickname"))
            else:
                print(f"Изменение никнейма отменено")

    @property
    def health(self) -> int:
        return self._health
    
    @health.setter
    def health(self, value: int) -> None:
        if self._health != value:
            changing_args = PropertyChangingEventArgs("health", self._health, value, True)
            self.property_changing(self, changing_args)
            if changing_args.can_change:
                self._health = value
                self.property_changed(self, PropertyChangedEventArgs("health"))
            else:
                print(f"Изменение здоровья отменено")

    @property
    def death(self) -> int:
        return self._death
    
    @death.setter
    def death(self, value: int) -> None:
        if self._death != value:
            changing_args = PropertyChangingEventArgs("death", self._death, value, True)
            self.property_changing(self, changing_args)
            if changing_args.can_change:
                self._death = value
                self.property_changed(self, PropertyChangedEventArgs("death"))
            else:
                print(f"Изменение количества смертей отменено")
    
    def __str__(self) -> str:
        return f"Player(nickname='{self.nickname}', health={self.health}, death={self.death})"


def main():
    changed_handler = PropertyChangedEvent()
    validator = PropertyChangingEvent()
    
    # Создаем объекты
    user = User("Иван", 25, "ivan@example.com")
    player = Player("SuperPlayer", 80, 3)
    
    # Подписываемся на события
    user.property_changed += changed_handler
    user.property_changing += validator
    
    player.property_changed += changed_handler
    player.property_changing += validator
    
    print("=== ТЕСТ USER ===")
    print(f"Начальное состояние: {user}")
    
    # ИСПРАВЛЕНО: используем сеттеры вместо прямого вызова событий
    print("\n--- Корректные изменения User ---")
    user.name = "Петр"  # Это вызовет сеттер и изменит значение
    user.age = 30       # Это вызовет сеттер и изменит значение
    user.email = "petr@example.com"  # Это вызовет сеттер и изменит значение
    
    print("\n--- Некорректные значения User ---")
    user.age = -5           # Должно быть отклонено валидатором
    user.email = "invalid-email"  # Должно быть отклонено валидатором
    user.name = ""          # Должно быть отклонено валидатором
    
    print(f"\nФинальное состояние: {user}")
    
    print("\n=== ТЕСТ PLAYER ===")
    print(f"Начальное состояние: {player}")
    
    # ИСПРАВЛЕНО: используем сеттеры вместо прямого вызова событий
    print("\n--- Корректные изменения Player ---")
    player.nickname = "ProPlayer"  # Это вызовет сеттер и изменит значение
    player.health = 90             # Это вызовет сеттер и изменит значение
    player.death = 5               # Это вызовет сеттер и изменит значение
    
    print("\n--- Некорректные значения Player ---")
    player.health = 150     # Должно быть отклонено валидатором
    player.health = -10     # Должно быть отклонено валидатором
    player.death = -1       # Должно быть отклонено валидатором
    player.nickname = ""    # Должно быть отклонено валидатором
    
    print(f"\nФинальное состояние: {player}")


if __name__ == '__main__':
    main()

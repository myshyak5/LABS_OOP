import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Sequence, Optional, List, TypeVar, Generic
import os
from datetime import datetime


@dataclass(order=True)
class User:
    name: str = field(compare=True)
    login: str = field(compare=False)
    password: str = field(repr=False, compare=False)
    email: Optional[str] = field(default=None, compare=False)
    address: Optional[str] = field(default=None, compare=False)
    id: Optional[int] = field(default=None, compare=False)
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'login': self.login,
            'password': self.password,
            'email': self.email,
            'address': self.address
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        return cls(
            id=data.get('id'),
            name=data['name'],
            login=data['login'],
            password=data['password'],
            email=data.get('email'),
            address=data.get('address')
        )


T = TypeVar('T')

class IDataRepository(ABC, Generic[T]):
    @abstractmethod
    def get_all(self) -> Sequence[T]:
        ...
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        ...
    
    @abstractmethod
    def add(self, item: T) -> None:
        ...
    
    @abstractmethod
    def update(self, item: T) -> None:
        ...
    
    @abstractmethod
    def delete(self, item: T) -> None:
        ...


class IUserRepository(IDataRepository[User]):
    @abstractmethod
    def get_by_login(self, login: str) -> Optional[User]:
        ...


class DataRepository(IDataRepository[T]):
    def __init__(self, file_path: str, from_dict_func, to_dict_func):
        self.file_path = file_path
        self.from_dict_func = from_dict_func
        self.to_dict_func = to_dict_func
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def _read_data(self) -> List[dict]:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _write_data(self, data: List[dict]):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            return
    
    def get_all(self) -> Sequence[T]:
        data = self._read_data()
        return [self.from_dict_func(item) for item in data]
    
    def get_by_id(self, id: int) -> Optional[T]:
        data = self._read_data()
        for item in data:
            if item.get('id') == id:
                return self.from_dict_func(item)
        return None
    
    def add(self, item: T) -> None:
        data = self._read_data()
        if hasattr(item, 'id') and getattr(item, 'id') is None:
            max_id = max([d.get('id', 0) for d in data]) if data else 0
            setattr(item, 'id', max_id + 1)
        data.append(self.to_dict_func(item))
        self._write_data(data)
    
    def update(self, item: T) -> None:
        data = self._read_data()
        item_id = getattr(item, 'id')
        for i, existing_item in enumerate(data):
            if existing_item.get('id') == item_id:
                data[i] = self.to_dict_func(item)
                self._write_data(data)
                return
        raise ValueError(f"id {item_id} не найден")
    
    def delete(self, item: T) -> None:
        data = self._read_data()
        item_id = getattr(item, 'id')
        data = [d for d in data if d.get('id') != item_id]
        self._write_data(data)


class UserRepository(IUserRepository):
    def __init__(self, file_path: str):
        self._repo = DataRepository(
            file_path=file_path,
            from_dict_func=User.from_dict,
            to_dict_func=lambda user: user.to_dict()
        )
    
    def get_all(self) -> Sequence[User]:
        return sorted(self._repo.get_all())
    
    def get_by_id(self, id: int) -> Optional[User]:
        return self._repo.get_by_id(id)
    
    def get_by_login(self, login: str) -> Optional[User]:
        users = self.get_all()
        for user in users:
            if user.login == login:
                return user
        return None
    
    def add(self, user: User) -> None:
        self._repo.add(user)
    
    def update(self, user: User) -> None:
        self._repo.update(user)
    
    def delete(self, user: User) -> None:
        self._repo.delete(user)


class IAuthService(ABC):
    @abstractmethod
    def sign_in(self, login: str, password: str) -> None:
        ...
    
    @abstractmethod
    def sign_out(self) -> None:
        ...
    
    @property
    @abstractmethod
    def is_authorized(self) -> bool:
        ...
    
    @property
    @abstractmethod
    def current_user(self) -> User:
        ...


class AuthService(IAuthService):
    def __init__(self,
                 user_repository: IUserRepository,
                 session_file: str):
        self.user_repository = user_repository
        self.session_file = session_file
        self._current_user = None
        self._auto_sign_in()
    
    def _auto_sign_in(self):
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                user = self.user_repository.get_by_login(session_data['login'])
                if user:
                    self._current_user = user
                    print(f"Автоматически авторизован пользователь: {user.name}\n")
                else:
                    print("Требуется авторизация")
                    self._clear_session()
        except Exception as e:
            print(f"Ошибка автоматической авторизации: {e}")
            self._clear_session()
    
    def _save_session(self):
        if self._current_user:
            session_data = {
                'login': self._current_user.login,
                'timestamp': datetime.now().isoformat()
            }
            try:
                with open(self.session_file, 'w', encoding='utf-8') as f:
                    json.dump(session_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Ошибка сохранения сессии: {e}")
    
    def _clear_session(self):
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
        except Exception as e:
            print(f"Ошибка удаления сессии: {e}")
    
    def sign_in(self, login: str, password: str) -> None:
        user = self.user_repository.get_by_login(login)
        if user and user.password == password:
            self._current_user = user
            self._save_session() 
            print(f"Успешная авторизация: {user.name}")
        else:
            print("Неверный логин или пароль")
    
    def sign_out(self) -> None:
        if self._current_user:
            print(f"Выход пользователя: {self._current_user.name}")
            self._current_user = None
        self._clear_session()
    
    @property
    def is_authorized(self) -> bool:
        return self._current_user is not None
    
    @property
    def current_user(self) -> User:
        return self._current_user


def main():
    print("=== ДЕМОНСТРАЦИЯ СИСТЕМЫ АВТОРИЗАЦИИ ===\n")
    user_repo = UserRepository('users.json')
    auth_service = AuthService(user_repo, 'session.json')

    print("1. ДОБАВЛЕНИЕ ПОЛЬЗОВАТЕЛЕЙ")
    count = int(input("Введите количество пользователей: "))
    for i in range(count):
        name = input("Введите имя: ")
        login = input("Введите логин: ")
        password = input("Введите пароль: ")
        email = input("Введите email (необязательно): ") or None
        address = input("Введите адрес (необязательно): ") or None
        id_user = input("Введите айди (необзяательно): ") or None
        id_user = int(id_user) if id_user else None
        user1 = User(name, login, password, email, address, id_user)
        if user_repo.get_by_login(login):
            print(f"   Пользователь {user1.name} уже существует")
        else:
            user_repo.add(user1)
            print(f"   Добавлен: {user1.name} (логин: {user1.login})")
    
    print(f"   Всего пользователей: {len(user_repo.get_all())}\n")

    print("2. РЕДАКТИРОВАНИЕ ПОЛЬЗОВАТЕЛЯ (name, email)")
    user2_login = input("Введите логин пользователя: ")
    user2 = user_repo.get_by_login(user2_login)
    if user2:
        new_name = input("Введите новое имя: ")
        new_email = input("Введите новый email: ")
        user2.email = new_email
        user2_old_name = user2.name
        user2.name = new_name
        user_repo.update(user2)
        print(f"   Обновлено имя пользователя {user2_old_name}: {user2.name}")
        print(f"   Обновлен email пользователя {user2.name}: {user2.email}\n")

    if not auth_service.is_authorized:
        print("3. АВТОРИЗАЦИЯ ПОЛЬЗОВАТЕЛЯ")
        user3_login = input("Введите логин: ")
        user3_password = input("Введите пароль: ")
        auth_service.sign_in(user3_login, user3_password)
        print(f"   Авторизован: {auth_service.is_authorized}")
        print(f"   Текущий пользователь: {auth_service.current_user}\n")

    if auth_service.is_authorized:
        print("4. СМЕНА ПОЛЬЗОВАТЕЛЯ")
        auth_service.sign_out()
        user4_login = input("Введите логин нового пользователя: ")
        user4_password = input("Введите пароль нового пользователя: ")
        auth_service.sign_in(user4_login, user4_password)
        print(f"   Новый пользователь: {auth_service.current_user}\n")


if __name__ == "__main__":
    main()
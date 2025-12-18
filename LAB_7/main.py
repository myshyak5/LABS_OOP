from abc import ABC, abstractmethod
from typing import Dict, Any, Type, Callable
from contextlib import contextmanager
from enum import Enum


class LifeStyle(Enum):
    PER_REQUEST = "PerRequest"
    SCOPED = "Scoped"
    SINGLETON = "Singleton"


class Injector:
    def __init__(self):
        self._registrations: Dict[Type, Dict] = {}
        self._singletons: Dict[Type, Any] = {}
        self._scoped_instances: Dict[Type, Any] = None
    
    def register(self, interface_type: Type,
                 class_type: Type = None, 
                 life_style: str = LifeStyle.PER_REQUEST, 
                 params: Dict[str, Any] = None,
                 fabric_method: Callable = None):
        if class_type is None and fabric_method is None:
            raise ValueError("Должен быть указан class_type или fabric_method")
        self._registrations[interface_type] = {
            'class_type': class_type,
            'life_style': life_style,
            'params': params or {},
            'fabric_method': fabric_method
        }
    
    @contextmanager
    def scope(self):
        old_scope = self._scoped_instances
        self._scoped_instances = {}
        try:
            yield
        finally:
            self._scoped_instances = old_scope
    
    def get_instance(self, interface_type: Type) -> Any:
        if interface_type not in self._registrations:
            raise ValueError(f"Тип {interface_type} не зарегистрирован")
        reg = self._registrations[interface_type]
        life_style = reg['life_style']

        if life_style == LifeStyle.SINGLETON:
            if interface_type in self._singletons:
                return self._singletons[interface_type]
            instance = self._create_instance(interface_type)
            self._singletons[interface_type] = instance
            return instance
        
        elif life_style == LifeStyle.SCOPED:
            if self._scoped_instances is None:
                raise RuntimeError("Нет активного scope")
            if interface_type in self._scoped_instances:
                return self._scoped_instances[interface_type]
            instance = self._create_instance(interface_type)
            self._scoped_instances[interface_type] = instance
            return instance
        
        elif life_style == LifeStyle.PER_REQUEST:
            return self._create_instance(interface_type)
    
    def _create_instance(self, interface_type: Type) -> Any:
        reg = self._registrations[interface_type]
        if reg['fabric_method']:
            return reg['fabric_method']()
        cls = reg['class_type']
        params = reg['params'].copy()
        constructor_args = {}
        if hasattr(cls.__init__, '__annotations__'):
            for param_name, param_type in cls.__init__.__annotations__.items():
                if param_name != 'return' and param_type in self._registrations:
                    constructor_args[param_name] = self.get_instance(param_type)
                elif param_name in params:
                    constructor_args[param_name] = params[param_name]
        for key, value in params.items():
            if key not in constructor_args:
                constructor_args[key] = value
        return cls(**constructor_args)


class IInterface1(ABC):
    @abstractmethod
    def execute(self) -> str:
        pass


class IInterface2(ABC):
    @abstractmethod
    def process(self) -> str:
        pass


class IInterface3(ABC):
    @abstractmethod
    def run(self) -> str:
        pass


class Class1Debug(IInterface1):
    def __init__(self, mode: str = "debug",
                 version: str = "1.0"):
        self.mode = mode
        self.version = version
    
    def execute(self) -> str:
        return f"Debug1: {self.mode} v{self.version}"

class Class1Release(IInterface1):
    def __init__(self, env: str = "prod"):
        self.env = env
    
    def execute(self) -> str:
        return f"Release1: {self.env}"


class Class2Debug(IInterface2):
    def __init__(self, service1: IInterface1,
                 level: str = "debug"):
        self.service1 = service1
        self.level = level
    
    def process(self) -> str:
        return f"Debug2[{self.level}]: {self.service1.execute()}"

class Class2Release(IInterface2):
    def __init__(self, service1: IInterface1,
                 config: Dict = None):
        self.service1 = service1
        self.config = config or {}
    
    def process(self) -> str:
        return f"Release2: {self.service1.execute()}"


class Class3Debug(IInterface3):
    def __init__(self, service1: IInterface1,
                 service2: IInterface2,
                 tag: str = "DEBUG"):
        self.service1 = service1
        self.service2 = service2
        self.tag = tag
    
    def run(self) -> str:
        return f"Debug3[{self.tag}]: {self.service1.execute()} -> {self.service2.process()}"

class Class3Release(IInterface3):
    def __init__(self, service1: IInterface1,
                 service2: IInterface2):
        self.service1 = service1
        self.service2 = service2
    
    def run(self) -> str:
        return f"Release3: {self.service1.execute()} | {self.service2.process()}"


def create_debug_config(injector: Injector):
    injector.register(IInterface1, Class1Debug, LifeStyle.SINGLETON,
                      {"mode": "debug", "version": "2.0"})
    injector.register(IInterface2, Class2Debug, LifeStyle.PER_REQUEST,
                      {"level": "verbose"})
    injector.register(IInterface3, Class3Debug, LifeStyle.SCOPED,
                      {"tag": "TEST"})

def create_release_config(injector: Injector):
    injector.register(IInterface1, Class1Release, LifeStyle.SINGLETON,
                      {"env": "production"})
    injector.register(IInterface2, Class2Release, LifeStyle.SINGLETON)
    
    def create_release_service3():
        service1 = injector.get_instance(IInterface1)
        service2 = injector.get_instance(IInterface2)
        return Class3Release(service1, service2)
    
    injector.register(IInterface3,
                      fabric_method=create_release_service3,
                      life_style=LifeStyle.PER_REQUEST)


class IA(ABC):
    @abstractmethod
    def do_something(self) -> str:
        pass


class A(IA):
    def __init__(self, name: str):
        self.name = name

    def do_something(self) -> str:
        return self.name
    

class IB(ABC):
    @abstractmethod
    def execute(self) -> str:
        pass


class B(IB):
    def __init__(self, a: IA):
        self.a = a

    def execute(self) -> str:
        return "123"

def main():
    # print("\n(☞ﾟヮﾟ)☞  КОНФИГУРАЦИЯ DEBUG ☜(ﾟヮﾟ☜)\n")
    
    injector1 = Injector()
    injector1.register(IB, B)
    try:
        result1 = injector1.get_instance(IB)
        print(f"TEST 1: {result1.execute()}")
    except Exception as e:
        print(f"Error 1: {e}")

    injector2 = Injector()
    injector2.register(IA, A, params={"name": "323"})
    injector2.register(IB, B)
    try:
        result2 = injector2.get_instance(IB)
        result3 = injector2.get_instance(IA)
        print(f"TEST 2: {result2.execute()}")
        print(f"TEST A: {result3.do_something()}")
    except Exception as e:
        print(f"Error 2: {e}")
    # create_debug_config(injector1)
    
    # # Singleton - один экземпляр
    # s1 = injector1.get_instance(IInterface1)
    # s2 = injector1.get_instance(IInterface1)
    # print(f"Singleton одинаковые: {s1 is s2}")
    # print(f"I1: {s1.execute()}\n")
    
    # # PerRequest - разные экземпляры
    # p1 = injector1.get_instance(IInterface2)
    # p2 = injector1.get_instance(IInterface2)
    # print(f"PerRequest разные: {p1 is not p2}")
    # print(f"I2: {p1.process()}\n")
    
    # # Scoped - один в пределах scope
    # with injector1.scope():
    #     sc1 = injector1.get_instance(IInterface3)
    #     sc2 = injector1.get_instance(IInterface3)
    #     print(f"Scoped в одном scope одинаковые: {sc1 is sc2}")
    #     print(f"I3: {sc1.run()}\n")
    
    # # Новый scope - новый экземпляр
    # with injector1.scope():
    #     sc3 = injector1.get_instance(IInterface3)
    #     print(f"Новый scope - новый экземпляр: {sc3.run()}\n")
    
    # print("\n(☞ﾟヮﾟ)☞  КОНФИГУРАЦИЯ RELEASE ☜(ﾟヮﾟ☜)\n")
    
    # injector2 = Injector()
    # create_release_config(injector2)
    
    # # Все Singleton
    # rs1 = injector2.get_instance(IInterface1)
    # rs2 = injector2.get_instance(IInterface1)
    # print(f"Release Singleton I1: {rs1.execute()}")
    # print(f"Одинаковые: {rs1 is rs2}\n")
    
    # # I2 тоже Singleton
    # rs3 = injector2.get_instance(IInterface2)
    # print(f"Release I2: {rs3.process()}\n")
    
    # # I3 через фабричный метод (PerRequest)
    # rs4 = injector2.get_instance(IInterface3)
    # rs5 = injector2.get_instance(IInterface3)
    # print(f"Release I3 (фабричный): {rs4.run()}")
    # print(f"PerRequest разные: {rs4 is not rs5}\n")


# Interface IA

# class A(IA)
#    ....

# interface IB:

# class B(IB):
#      def __init__(a: IA):
#           pass

# register(IB, B) -> failed

# register(IA, A)
# re3gister(IB, B)


if __name__ == "__main__":
    main()
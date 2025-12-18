import json
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class Command(ABC):
    @abstractmethod
    def execute(self) -> str:
        pass
    
    @abstractmethod
    def undo(self) -> str:
        pass
    
    @abstractmethod
    def redo(self) -> str:
        pass


class KeyCommand(Command):
    def __init__(self, char: str) -> None:
        self.char = char
        
    def execute(self) -> str:
        return self.char
    
    def undo(self) -> str:
        return "undo"
    
    def redo(self) -> str:
        return self.execute()


class VolumeUpCommand(Command):
    def __init__(self, step: int) -> None:
        self.step = step
    
    def execute(self) -> str:
        return f"volume increased +{self.step}%"
    
    def undo(self) -> str:
        return f"volume decreased -{self.step}%"
    
    def redo(self) -> str:
        return self.execute()


class VolumeDownCommand(Command):
    def __init__(self, step: int) -> None:
        self.step = step
    
    def execute(self) -> str:
        return f"volume decreased -{self.step}%"
    
    def undo(self) -> str:
        return f"volume increased +{self.step}%"
    
    def redo(self) -> str:
        return self.execute()


class MediaPlayerCommand(Command):
    def execute(self) -> str:
        return "media player launched"
    
    def undo(self) -> str:
        return "media player closed"
    
    def redo(self) -> str:
        return self.execute()
            

class DictRepresentation:
    _COMMAND_CLASSES = {
        "KeyCommand": KeyCommand,
        "VolumeUpCommand": VolumeUpCommand,
        "VolumeDownCommand": VolumeDownCommand,
        "MediaPlayerCommand": MediaPlayerCommand,
    }       
    
    @staticmethod
    def command_to_dict(command: Command) -> Dict[str, Any]:
        result = {"type": command.__class__.__name__}
        attrs = {k: v for k, v in command.__dict__.items() if not k.startswith('_')}
        result.update(attrs)
        return result
    
    @classmethod
    def dict_to_command(cls, data: Dict[str, Any]) -> Command:
        command_type = data["type"]
        command_class = cls._COMMAND_CLASSES[command_type]
        params = {k: v for k, v in data.items() if k != "type"}
        return command_class(**params)   


class CommandSerializer:
    @staticmethod
    def serialize(command: Command) -> Dict[str, Any]:
        return DictRepresentation.command_to_dict(command)
    
    @staticmethod
    def deserialize(data: Dict[str, Any]) -> Command:
        return DictRepresentation.dict_to_command(data)


class KeyboardStateSaver:
    def __init__(self, filename: str = "keyboard_state.json") -> None:
        self.filename = filename
    
    def save_state(self, key_bindings: Dict[str, Command]) -> None:
        serializable_state = {}
        for key, command in key_bindings.items():
            serializable_state[key] = CommandSerializer.serialize(command)
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(serializable_state, f, indent=2)
        except Exception as e:
            print(f"File error: {e}")
    
    def load_state(self) -> Dict[str, Command]:
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            restored_state = {}
            for key, command_data in data.items():
                try:
                    restored_state[key] = CommandSerializer.deserialize(command_data)
                except Exception as e:
                    print(f"Deserialize error: {e}")
            return restored_state
        except FileNotFoundError:
            return {}


class Keyboard:
    def __init__(self) -> None:
        self.key_bindings: Dict[str, Command] = {}
        self.command_history: List[Command] = []
        self.current_position = -1
        self.text_content: str = ""
        self.state_saver = KeyboardStateSaver()
        saved_state = self.state_saver.load_state()
        if saved_state:
            self.key_bindings = saved_state
    
    def bind_key(self, key_combo: str, command: Command) -> None:
        self.key_bindings[key_combo] = command
        self.state_saver.save_state(self.key_bindings)
    
    def press_key(self, key_combo: str) -> str:
        if key_combo in self.key_bindings:
            command = self.key_bindings[key_combo]
            result = command.execute()
            if isinstance(command, KeyCommand):
                self.text_content += command.char
            if self.current_position < len(self.command_history) - 1:
                self.command_history = self.command_history[:self.current_position + 1]
            self.command_history.append(command)
            self.current_position += 1
            return result
        return f"No binding for: {key_combo}"
    
    def undo(self) -> Optional[str]:
        if not self.command_history:
            return None
        command = self.command_history[self.current_position]
        result = command.undo()
        if isinstance(command, KeyCommand) and self.text_content:
            self.text_content = self.text_content[:-1]
        self.current_position -= 1
        return result
    
    def redo(self) -> Optional[str]:
        if self.current_position >= len(self.command_history) - 1:
            return None
        self.current_position += 1
        command = self.command_history[self.current_position]
        result = command.redo()
        if isinstance(command, KeyCommand):
            self.text_content += command.char
        return result
    
    def get_text(self) -> str:
        return self.text_content


def main():
    keyboard = Keyboard()

    if not keyboard.key_bindings:
        keyboard.bind_key("a", KeyCommand("a"))
        keyboard.bind_key("b", KeyCommand("b"))
        keyboard.bind_key("c", KeyCommand("c"))
        keyboard.bind_key("ctrl++", VolumeUpCommand(20))
        keyboard.bind_key("ctrl+-", VolumeDownCommand(20))
        keyboard.bind_key("ctrl+p", MediaPlayerCommand())
        keyboard.bind_key("d", KeyCommand("d"))
    
    print(keyboard.press_key("a"))
    print(keyboard.press_key("b"))
    print(keyboard.press_key("c"))
    print(keyboard.undo())
    print(keyboard.undo())
    print(keyboard.redo())
    print(keyboard.press_key("ctrl++"))
    print(keyboard.press_key("ctrl+-"))
    print(keyboard.press_key("ctrl+p"))
    print(keyboard.press_key("d"))
    print(keyboard.undo())
    print(keyboard.undo())
    print(f"Текст: {keyboard.get_text()}")


if __name__ == "__main__":
    main()
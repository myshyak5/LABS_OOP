from abc import ABC, abstractmethod
import re
import datetime
import socket
import sys
import ftplib
from enum import Enum
from typing import List


class LogLevel(Enum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


class ILogFilter(ABC):
    @abstractmethod
    def match(self, log_level: LogLevel, text: str) -> bool:
        ...


class SimpleLogFilter(ILogFilter):
    def __init__(self, pattern: str) -> None:
        try:
            self.pattern = pattern.lower()
        except Exception as e:
            print(f"Pattern error: {e}")

    def match(self, log_level: LogLevel, text: str) -> bool:
        return self.pattern in text.lower()
    

class ReLogFilter(ILogFilter):
    def __init__(self, pattern: str) -> None:
        self.pattern = re.compile(pattern)

    def match(self, log_level: LogLevel, text: str) -> bool:
        return bool(self.pattern.search(text.lower()))
    

class LevelFilter(ILogFilter):
    def __init__(self, min_level: LogLevel) -> None:
        self.min_level = min_level
        self.levels_order = {LogLevel.INFO: 1, LogLevel.WARN: 2, LogLevel.ERROR: 3}

    def match(self, log_level: LogLevel, text: str) -> bool:
        return self.levels_order[log_level] >= self.levels_order[self.min_level]
    

class ILogHandler(ABC):
    @abstractmethod
    def handle(self, log_level: LogLevel, text: str) -> None:
        ...


class ConsoleHandler(ILogHandler):
    def handle(self, log_level: LogLevel, text: str) -> None:
        print(text)


class FileHandler(ILogHandler):
    def __init__(self, filename: str):
        self.filename = filename

    def handle(self, log_level: LogLevel, text: str) -> None:
        try:
            with open(self.filename, 'a', encoding='utf-8') as f:
                f.write(text + '\n')
        except Exception as e:
            print(f"File error: {e}")


class SocketHandler(ILogHandler):
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    def handle(self, log_level: LogLevel, text: str) -> None:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.host, self.port))
                sock.sendall((text + '\n').encode('utf-8'))
        except Exception as e:
            print(f"Socket error: {e}")


class SyslogHandler(ILogHandler):
    def __init__(self, ident: str) -> None:
        self.ident = ident

    def handle(self, log_level: LogLevel, text: str) -> None:
        sys.stderr.write(f"[{self.ident}] {text}\n")


class FtpHandler(ILogHandler):
    def __init__(self, host: str,
                 username: str,
                 password: str,
                 remote_path: str) -> None:
        self.host = host
        self.username = username
        self.password = password
        self.remote_path = remote_path
        self.buffer = []

    def handle(self, log_level: LogLevel, text: str) -> None:
        self.buffer.append(text)

    def flush(self):
        try:
            with ftplib.FTP(self.host) as ftp:
                ftp.login(self.username, self.password)
                temp_content = '\n'.join(self.buffer)
                ftp.storbinary(f'STOR {self.remote_path}', temp_content.encode('utf-8'))
                self.buffer.clear()
        except Exception as e:
            print(f"FTP error: {e}")


class ILogFormatter(ABC):
    @abstractmethod
    def format(self, log_level: LogLevel, text: str) -> str:
        ...


class StandardFormatter(ILogFormatter):
    def __init__(self, data_format: str = "%Y.%m.%d %H:%M:%S"):
        self.data_format = data_format

    def format(self, log_level: LogLevel, text: str) -> str:
        data = datetime.datetime.now().strftime(self.data_format)
        return f"[{log_level.value}] [{data}] {text}"
    

class Logger:
    def __init__(self, filters: List[ILogFilter],
                 formatters: List[ILogFormatter],
                 handlers: List[ILogHandler]) -> None:
        self.filters = filters
        self.formatters = formatters
        self.handlers = handlers

    def log(self, log_level: LogLevel, text: str) -> None:
        for filter_obj in self.filters:
            if not filter_obj.match(log_level, text):
                return
        formatted_text = text
        for formatter in self.formatters:
            formatted_text = formatter.format(log_level, formatted_text)
        for handler in self.handlers:
            handler.handle(log_level, formatted_text)

    def log_info(self, text: str) -> None:
        self.log(LogLevel.INFO, text)

    def log_warn(self, text: str) -> None:
        self.log(LogLevel.WARN, text)

    def log_error(self, text: str) -> None:
        self.log(LogLevel.ERROR, text)

def main():
    formatter = StandardFormatter("%d.%m.%Y %H:%M:%S")
    console_handler = ConsoleHandler()
    file_handler = FileHandler("app.log")
    simple_filter = SimpleLogFilter("important")
    regex_filter = ReLogFilter(r"error|warning")
    level_filter = LevelFilter(LogLevel.WARN)  # Только WARN и ERROR

    print("1. Простой логгер (только консоль):")
    simple_logger = Logger(filters=[],
                           formatters=[formatter],
                           handlers=[console_handler])
    simple_logger.log_info("Это информационное сообщение")
    simple_logger.log_warn("Это предупреждение")
    simple_logger.log_error("Это ошибка")
    
    print("\n2. Логгер с фильтром по уровню (только WARN и ERROR):")
    level_logger = Logger(filters=[level_filter],
                          formatters=[formatter],
                          handlers=[console_handler])
    level_logger.log_info("Это сообщение не должно появиться")
    level_logger.log_warn("Это предупреждение должно появиться")
    level_logger.log_error("Эта ошибка должна появиться")
    
    print("\n3. Логгер с фильтром по тексту (только 'important'):")
    text_logger = Logger(filters=[simple_filter],
                         formatters=[formatter],
                         handlers=[console_handler])
    text_logger.log_info("Обычное сообщение")
    text_logger.log_info("Важное important сообщение")
    
    print("\n4. Логгер с фильтром по регулярному выражению:")
    regex_logger = Logger(filters=[regex_filter],
                          formatters=[formatter],
                          handlers=[console_handler])
    regex_logger.log_info("Обычное сообщение")
    regex_logger.log_warn("Сообщение с warning")
    regex_logger.log_error("Сообщение с Error")
    
    print("\n5. Логгер в файл и консоль:")
    multi_handler_logger = Logger(filters=[],
                                  formatters=[formatter],
                                  handlers=[console_handler, file_handler])
    multi_handler_logger.log_info("Сообщение в консоль и файл")
    
    print("\n6. Комбинированные фильтры (уровень + текст):")
    combined_logger = Logger(filters=[level_filter, simple_filter],
                             formatters=[formatter],
                             handlers=[console_handler])
    combined_logger.log_info("info: не должно появиться")
    combined_logger.log_warn("warning: не должно появиться") 
    combined_logger.log_warn("warning: important - должно появиться")
    combined_logger.log_error("error: important - должно появиться")
    
    print("\n7. Демонстрация FTP handler (буферизация):")
    ftp_handler = FtpHandler("example.com", "user", "pass", "/logs/app.log")
    ftp_logger = Logger(filters=[],
                        formatters=[formatter],
                        handlers=[console_handler, ftp_handler])
    ftp_logger.log_info("Сообщение для FTP")
    print(f"В буфере FTP: {len(ftp_handler.buffer)} сообщений")

    
if __name__ == "__main__":
    main()
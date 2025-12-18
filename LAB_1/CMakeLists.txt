cmake_minimum_required(VERSION 3.15) # Проверка версии CMake



set(PROJECT_NAME example) # задать значение PROJECT_NAME
project("${PROJECT_NAME}") # Установить имя проекта


set(CMAKE_CXX_STANDARD 17) # Устанавливаем 17 стандарт
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD_REQUIRED TRUE)

# Сказать программе, что должен быть исполняемый файл
add_executable("${PROJECT_NAME}" main.cpp)
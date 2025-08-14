cmake_minimum_required(VERSION 3.15)
project(evw LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Library with your CSVReader
add_library(evw_lib
    src/CSVReader.cpp
)
target_include_directories(evw_lib PUBLIC include)

# Executable
add_executable(evw
    src/main.cpp
)
target_link_libraries(evw PRIVATE evw_lib)

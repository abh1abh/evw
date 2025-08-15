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


# After add_executable(evw ...)
set_target_properties(evw PROPERTIES
  RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
  RUNTIME_OUTPUT_DIRECTORY_DEBUG ${CMAKE_BINARY_DIR}
  RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_BINARY_DIR}
  RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO ${CMAKE_BINARY_DIR}
  RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL ${CMAKE_BINARY_DIR}
)
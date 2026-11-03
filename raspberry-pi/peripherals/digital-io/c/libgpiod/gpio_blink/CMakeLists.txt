cmake_minimum_required(VERSION 3.10)

project(blink LANGUAGES C)

# Match `-Wall`
add_compile_options(-Wall)

# Check for libgpiod
find_library(GPIOD_LIB gpiod REQUIRED)

add_executable(blink blink.c)

# Link against libgpiod (equivalent to -lgpiod)
target_link_libraries(blink PRIVATE ${GPIOD_LIB})

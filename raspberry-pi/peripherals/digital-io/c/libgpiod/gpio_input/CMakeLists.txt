cmake_minimum_required(VERSION 3.10)

project(gpio_input LANGUAGES C)

# Match `-Wall`
add_compile_options(-Wall)

# Check for libgpiod
find_library(GPIOD_LIB gpiod REQUIRED)

add_executable(gpio_input gpio_input.c)

# Link against libgpiod (equivalent to -lgpiod)
target_link_libraries(gpio_input PRIVATE ${GPIOD_LIB})

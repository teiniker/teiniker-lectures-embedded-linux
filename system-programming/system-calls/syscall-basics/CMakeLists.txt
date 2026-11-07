cmake_minimum_required(VERSION 3.10)

project(syscall-basics LANGUAGES C)

# Match `-Wall`
add_compile_options(-Wall)

add_executable(syscall syscall.c)
add_executable(errors errors.c)

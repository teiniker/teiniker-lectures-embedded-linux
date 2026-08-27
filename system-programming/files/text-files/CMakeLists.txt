cmake_minimum_required(VERSION 3.10)

project(text-files LANGUAGES C)

# Match `-Wall`
add_compile_options(-Wall)

add_executable(write write.c)
add_executable(read read.c)

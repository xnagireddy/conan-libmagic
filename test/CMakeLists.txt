PROJECT(MyHello)
cmake_minimum_required(VERSION 2.8)

include(conanbuildinfo.cmake)
CONAN_BASIC_SETUP()
SET(VERBOSE 1)
SET(CMAKE_VERBOSE_MAKEFILE 1)
ADD_EXECUTABLE(example example.c)
include_directories(${CONAN_INCLUDE_DIRS})
MESSAGE(STATUS ${CONAN_LIBS})
target_link_libraries(example ${CONAN_LIBS})


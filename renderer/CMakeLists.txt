cmake_minimum_required(VERSION 3.28)
project(Renderer
    LANGUAGES C CXX
    VERSION 1.0.0
)

set(BUILD_MODE "CLI" CACHE STRING "Build mode: CLI, WORKER, BOTH or CORE")
option(BUILD_TESTS "Building tests" OFF)

if(BUILD_MODE STREQUAL "BOTH")
    set(BUILD_CLI ON)
    set(BUILD_WORKER ON)
    message(STATUS "Building BOTH CLI and worker versions")
elseif(BUILD_MODE STREQUAL "WORKER")
    set(BUILD_CLI OFF)
    set(BUILD_WORKER ON)
    message(STATUS "Building worker version")
elseif(BUILD_MODE STREQUAL "CLI")
    set(BUILD_CLI ON)
    set(BUILD_WORKER OFF)
    message(STATUS "Building CLI version")
else()
    set(BUILD_CLI OFF)
    set(BUILD_WORKER OFF)
    message(STATUS "Building core only")
endif()

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})

find_program(CCACHE_PROGRAM ccache)
if(CCACHE_PROGRAM)
    set(CMAKE_CXX_COMPILER_LAUNCHER ${CCACHE_PROGRAM})
    set(CMAKE_C_COMPILER_LAUNCHER ${CCACHE_PROGRAM})
endif()
set(CMAKE_BUILD_PARALLEL_LEVEL 4)

add_subdirectory(common)
add_subdirectory(core)

if(BUILD_CLI)
    add_subdirectory(cli)
endif() 

if(BUILD_WORKER)
    add_subdirectory(worker)
endif() 

if(BUILD_TESTS)
    message(STATUS "Building tests")
    add_subdirectory(tests)
endif()
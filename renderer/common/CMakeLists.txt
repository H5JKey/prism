add_library(common_deps STATIC
    src/logger.cpp
)

target_include_directories(common_deps PUBLIC
    include
)
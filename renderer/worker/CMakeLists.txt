add_subdirectory(lib)

add_executable(renderer
    src/renderer.cpp
)

target_include_directories(renderer PRIVATE
    include
)

target_link_libraries(renderer PRIVATE
    renderer_core
    common_deps
)

target_compile_options(renderer PRIVATE 
    -O3 
    -ffast-math 
    -march=native
    -fno-trapping-math
    -fno-signed-zeros
    -fno-math-errno
    -fassociative-math
    -frename-registers
    -fomit-frame-pointer
    -ftree-vectorize 
    -funroll-loops
    -flto=auto
)

add_executable(service
    src/service.cpp
    src/kafka-consumer.cpp
    src/kafka-producer.cpp
    src/s3-client.cpp
    src/dotenv.cpp
    src/config.cpp
)

target_include_directories(service PRIVATE
    include
)

target_link_libraries(service PRIVATE
    renderer_worker_deps
    common_deps
)

if(EXISTS ${CMAKE_SOURCE_DIR}/.env)
    set(ENV_FILE_EXISTS TRUE)
    message(STATUS ".env file found, will create symlink")
else()
    set(ENV_FILE_EXISTS FALSE)
    message(STATUS ".env file not found, skipping symlink")
endif()

if(ENV_FILE_EXISTS)
    add_custom_command(
        TARGET service POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E create_symlink 
            ${CMAKE_SOURCE_DIR}/.env
            ${CMAKE_BINARY_DIR}/.env
        COMMENT "Creating symlink for .env"
    )
endif()
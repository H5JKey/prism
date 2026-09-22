add_subdirectory(cppkafka)
add_subdirectory(json)
add_subdirectory(prometheus)

find_package(aws-sdk-cpp)

add_library(renderer_worker_deps INTERFACE)
target_link_libraries(renderer_worker_deps INTERFACE 
    cppkafka
    nlohmann_json::nlohmann_json
    aws-cpp-sdk-core
    aws-cpp-sdk-s3
    prometheus-cpp::core
    prometheus-cpp::pull
)

target_include_directories(renderer_worker_deps INTERFACE
    ${cppkafka_SOURCE_DIR}/include
)
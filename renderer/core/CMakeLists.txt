add_subdirectory(lib)

add_library(renderer_core STATIC
    src/scene.cpp
    src/scene-loader.cpp
    src/render-engine.cpp
    src/render-target.cpp
    src/target-manager.cpp
    src/denoiser.cpp
    src/bvh.cpp
    src/bvh-builder.cpp
    src/utils.cpp
    src/stb-implementation.cpp
    src/context-guard.cpp
)

target_link_libraries(renderer_core PUBLIC
    renderer_core_deps
    common_deps
)

target_include_directories(renderer_core PUBLIC
    include
)

add_custom_command(
    TARGET renderer_core POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E create_symlink
        ${CMAKE_SOURCE_DIR}/shaders
        ${CMAKE_BINARY_DIR}/shaders
    COMMENT "Symlinking shaders to build directory"
)
include(FetchContent)

add_subdirectory(glad)
add_subdirectory(stb)
add_subdirectory(glm)
add_subdirectory(fastgltf)

find_package(OpenGL REQUIRED COMPONENTS OpenGL EGL)
find_package(OpenImageDenoise REQUIRED)

add_library(renderer_core_deps INTERFACE)
target_include_directories(renderer_core_deps INTERFACE ${stb_SOURCE_DIR})
target_link_libraries(renderer_core_deps INTERFACE
    OpenGL::OpenGL 
    OpenGL::EGL
    glm::glm
    OpenImageDenoise
    glad
    fastgltf::fastgltf
)
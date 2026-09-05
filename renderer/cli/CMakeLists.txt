add_executable(renderer_cli
    src/main.cpp
)

target_link_libraries(renderer_cli PRIVATE
    renderer_core
    common_deps
)

target_compile_options(renderer_cli PRIVATE 
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
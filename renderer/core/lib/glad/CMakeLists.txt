FetchContent_Declare(
    glad
    GIT_REPOSITORY https://github.com/Dav1dde/glad.git
    GIT_TAG        v2.0.8
    SOURCE_SUBDIR  cmake 
)

FetchContent_MakeAvailable(glad)
glad_add_library(glad REPRODUCIBLE API gl:core=4.6)
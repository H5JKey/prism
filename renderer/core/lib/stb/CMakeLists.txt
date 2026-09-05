include(FetchContent)

FetchContent_Declare(
    stb
    GIT_REPOSITORY https://github.com/nothings/stb.git
    GIT_TAG        master
)

FetchContent_MakeAvailable(stb)

set(stb_SOURCE_DIR ${stb_SOURCE_DIR} PARENT_SCOPE)
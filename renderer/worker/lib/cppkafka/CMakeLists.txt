include(FetchContent)

FetchContent_Declare(
    cppkafka
    GIT_REPOSITORY https://github.com/mfontanini/cppkafka.git
    GIT_TAG v0.4.1
)

FetchContent_MakeAvailable(cppkafka)

set(cppkafka_SOURCE_DIR ${cppkafka_SOURCE_DIR} PARENT_SCOPE)

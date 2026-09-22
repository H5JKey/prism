FetchContent_Declare(
  prometheus-cpp
  GIT_REPOSITORY https://github.com/jupp0r/prometheus-cpp.git
  GIT_TAG v1.0.2
)

set(BUILD_TESTS OFF)
set(ENABLE_TESTING OFF)
FetchContent_MakeAvailable(prometheus-cpp)
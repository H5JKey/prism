#pragma once
#include <chrono>

struct Metrics {
    std::optional<std::chrono::milliseconds> pathTracingTime;
    std::optional<std::chrono::milliseconds> gbufferFillingTime;
    std::optional<std::chrono::milliseconds> postProcessingTime;
    std::optional<std::chrono::milliseconds> BVHBuildingTime;
    std::optional<std::chrono::milliseconds> upscalingTime;
    std::optional<std::chrono::milliseconds> denoisingTime;
    std::optional<std::chrono::milliseconds> totalTime;
    std::optional<size_t> polygonsCount;
    std::optional<size_t> texturesCount;
    std::optional<size_t> width;
    std::optional<size_t> height;
    std::optional<size_t> samples;
    std::optional<bool> renderingSuccess;
};
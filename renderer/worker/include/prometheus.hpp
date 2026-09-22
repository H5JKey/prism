#pragma once

#include <prometheus/counter.h>
#include <prometheus/exposer.h>
#include <prometheus/gauge.h>
#include <prometheus/histogram.h>
#include <prometheus/registry.h>

#include <memory>
#include <string>

#include "logger.hpp"
#include "metrics.hpp"

class Prometheus {
    Logger logger;

   public:
    explicit Prometheus(const std::string& address);

    void onRenderStarted();
    void onRenderFinished(const Metrics& metrics);

   private:
    std::unique_ptr<prometheus::Exposer> exposer;
    std::shared_ptr<prometheus::Registry> registry;

    prometheus::Counter* rendersTotal;
    prometheus::Counter* failedRenders;

    prometheus::Gauge* activeRenders;

    prometheus::Histogram* renderDuration;
    prometheus::Histogram* bvhBuildDuration;
    prometheus::Histogram* pathTracingDuration;
    prometheus::Histogram* denoisingDuration;
    prometheus::Histogram* upscalingDuration;
};
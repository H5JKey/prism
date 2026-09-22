#include "prometheus.hpp"

#include <prometheus/counter.h>
#include <prometheus/gauge.h>
#include <prometheus/histogram.h>
Prometheus::Prometheus(const std::string& address)
    : exposer(std::make_unique<prometheus::Exposer>(address)),
      registry(std::make_shared<prometheus::Registry>()),
      logger("PROMETHEUS") {
    rendersTotal =
        &prometheus::BuildCounter().Name("renders_total").Help("Total number of renders.").Register(*registry).Add({});

    activeRenders =
        &prometheus::BuildGauge().Name("active_renders").Help("Number of active renders.").Register(*registry).Add({});

    failedRenders = &prometheus::BuildCounter()
                         .Name("failed_renders_total")
                         .Help("Total number of failed renders.")
                         .Register(*registry)
                         .Add({});

    const prometheus::Histogram::BucketBoundaries buckets{0.01, 0.1,  0.5,   1.0,   5.0,   10.0,
                                                          30.0, 60.0, 120.0, 180.0, 240.0, 300.0};

    renderDuration = &prometheus::BuildHistogram()
                          .Name("render_duration_seconds")
                          .Help("Render duration in seconds.")
                          .Register(*registry)
                          .Add({}, buckets);

    bvhBuildDuration = &prometheus::BuildHistogram()
                            .Name("bvh_build_duration_seconds")
                            .Help("BVH building duration in seconds.")
                            .Register(*registry)
                            .Add({}, buckets);

    pathTracingDuration = &prometheus::BuildHistogram()
                               .Name("path_tracing_duration_seconds")
                               .Help("Path tracing duration in seconds.")
                               .Register(*registry)
                               .Add({}, buckets);

    denoisingDuration = &prometheus::BuildHistogram()
                             .Name("denoising_duration_seconds")
                             .Help("Denoising duration in seconds.")
                             .Register(*registry)
                             .Add({}, buckets);

    upscalingDuration = &prometheus::BuildHistogram()
                             .Name("upscaling_duration_seconds")
                             .Help("Preview upscaling duration in seconds.")
                             .Register(*registry)
                             .Add({}, buckets);

    exposer->RegisterCollectable(registry);

    logger.debug(std::format("Prometheus metrics server started on {}", address));
}

void Prometheus::onRenderStarted() { activeRenders->Increment(); }

void Prometheus::onRenderFinished(const Metrics& metrics) {
    activeRenders->Decrement();
    rendersTotal->Increment();

    if (metrics.renderingSuccess && !*metrics.renderingSuccess) failedRenders->Increment();

    if (metrics.totalTime) renderDuration->Observe(metrics.totalTime->count() / 1000.0);

    if (metrics.BVHBuildingTime) bvhBuildDuration->Observe(metrics.BVHBuildingTime->count() / 1000.0);

    if (metrics.pathTracingTime) pathTracingDuration->Observe(metrics.pathTracingTime->count() / 1000.0);

    if (metrics.denoisingTime) denoisingDuration->Observe(metrics.denoisingTime->count() / 1000.0);

    if (metrics.upscalingTime) upscalingDuration->Observe(metrics.upscalingTime->count() / 1000.0);
}
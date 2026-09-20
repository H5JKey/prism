#include <errno.h>
#include <unistd.h>

#include <atomic>
#include <cerrno>
#include <csignal>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <exception>
#include <format>
#include <memory>
#include <stdexcept>

#include "context-guard.hpp"
#include "contract.hpp"
#include "logger.hpp"
#include "render-engine.hpp"
#include "scene-loader.hpp"
#include "target-manager.hpp"
#include "utils.hpp"

std::string getEnv(const std::string& name) {
    const char* value = std::getenv(name.c_str());
    return value ? std::string(value) : "";
}

Logger logger("RENDERER");
std::unique_ptr<RenderEngine> engine;

std::atomic<bool> running{true};
std::atomic<bool> stopRequested{false};

void termSignalHandler(int signal) {
    if (signal == SIGTERM) {
        running = false;
        if (engine) engine->stopRequested = true;
        stopRequested = true;
    }
}

void intSignalHandler(int signal) {
    if (signal == SIGINT) {
        if (engine) engine->stopRequested = true;
        stopRequested = true;
    }
}

void setLoggerFromEnv() {
    std::string logDebugEnv = getEnv("RENDERER_LOG_DEBUG");
    std::string logLevelEnv = getEnv("RENDERER_LOG_LEVEL");

    if (!logDebugEnv.empty()) {
        logger.showDebug = (logDebugEnv == "true");
    }

    if (!logLevelEnv.empty()) {
        logger.setMinLevel(logger.getLevelFromString(logLevelEnv));
    }
}

struct PreviewInfo {
    bool enabled = false;
    int maxSize = 256;
    int upscaleFactor = 1;
};

PreviewInfo setPreviewSettingsFromEnv() {
    std::string rendererPreviewEnv = getEnv("RENDERER_PREVIEW");
    std::string rendererPreviewMaxSizeEnv = getEnv("RENDERER_PREVIEW_MAX_SIZE");
    std::string rendererPreviewUpscaleFactorEnv = getEnv("RENDERER_PREVIEW_UPSCALE_FACTOR");

    PreviewInfo previewInfo;

    if (!rendererPreviewEnv.empty()) {
        previewInfo.enabled = (rendererPreviewEnv == "true");
    }
    try {
        if (!rendererPreviewMaxSizeEnv.empty()) {
            previewInfo.maxSize = std::stoi(rendererPreviewMaxSizeEnv);
        }
    } catch (const std::exception& e) {
        logger.debug(std::format("RENDERER_PREVIEW_MAX_SIZE is not a integer. Set default value"));
    }
    try {
        if (!rendererPreviewUpscaleFactorEnv.empty()) {
            previewInfo.upscaleFactor = std::stoi(rendererPreviewUpscaleFactorEnv);
        }
    } catch (const std::exception& e) {
        logger.debug(std::format("RENDERER_PREVIEW_UPSCALE_FACTOR is not a integer. Set default value"));
    }
    return previewInfo;
}

int main() try {
    struct sigaction sa;
    sa.sa_handler = termSignalHandler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    sigaction(SIGTERM, &sa, nullptr);

    setLoggerFromEnv();
    PreviewInfo previewInfo = setPreviewSettingsFromEnv();
    TargetManager::init();
    SceneLoader sceneLoader;
    try {
        engine = std::make_unique<RenderEngine>();
        logger.debug("RenderEngine created successfully");
    } catch (const std::exception& e) {
        logger.fatal(std::format("Failed to create RenderEngine: {}", e.what()));
        throw;
    }

    sa.sa_handler = intSignalHandler;
    sigaction(SIGINT, &sa, nullptr);

    logger.info(std::format("Renderer worker started (PID: {})", getpid()));
    errno = 0;
    while (running) {
        TaskHeader task;
        ssize_t size;
        if ((size = ::read(STDIN_FILENO, &task, sizeof(task))) < 0) {
            if (errno == EINTR) {
                errno = 0;
            } else {
                throw std::runtime_error(std::format("Reading task from pipe failed: {}", std::strerror(errno)));
            }
        } else if (size > 0) {
            logger.debug(std::format("Read {} bytes from pipe for taskHeader", size));
            std::vector<uint8_t> sceneData(task.sceneDataSize);
            size_t total_read = 0;
            while (total_read < sceneData.size()) {
                ssize_t bytes_read = read(STDIN_FILENO, sceneData.data() + total_read, sceneData.size() - total_read);
                if (bytes_read == -1) {
                    if (errno == EINTR) continue;
                    throw std::runtime_error(std::format("Failed to read scene from pipe: {}", std::strerror(errno)));
                }
                if (bytes_read == 0) {
                    throw std::runtime_error("Pipe closed unexpectedly");
                }
                total_read += bytes_read;
            }
            logger.debug(std::format("Read {} bytes from pipe for scene", total_read));

            if (previewInfo.enabled) {
                float scale = std::min(512.0f / task.width, 512.0f / task.height);
                task.width = std::max(1, int(task.width * scale));
                task.height = std::max(1, int(task.height * scale));
                task.samples = 5;
            }

            auto egl = TargetManager::getInstance().createEGLTarget(task.width, task.height);
            Scene scene = sceneLoader.loadGltfFromMemory(sceneData);
            scene.setBackground(glm::vec3(task.background[0], task.background[1], task.background[2]));
            Scene::Sun sun;
            sun.color = glm::vec3(task.sun.color[0], task.sun.color[1], task.sun.color[2]);
            sun.direction = glm::vec3(task.sun.direction[0], task.sun.direction[1], task.sun.direction[2]);
            sun.exponent = task.sun.exponent;
            scene.setSun(sun);

            engine->renderFrame(*egl, scene, task.samples);
            if (!stopRequested) {
                ContextGuard guard(*egl);
                auto data = egl->getBufferData<uint8_t>(egl->getOutputTexture());
                std::vector<uint8_t> result = utils::writeToPng(data, task.width, task.height, 4);
                ResultHeader resultHeader;
                resultHeader.resultDataSize = result.size();
                write(STDOUT_FILENO, &resultHeader, sizeof(resultHeader));
                logger.debug(std::format("Written {} bytes in pipe for resultHeader", sizeof(resultHeader)));
                write(STDOUT_FILENO, result.data(), result.size());
                logger.debug(std::format("Written {} bytes in pipe for result", result.size()));
            } else {
                stopRequested = false;
                ResultHeader resultHeader;
                resultHeader.resultDataSize = 0;
                write(STDOUT_FILENO, &resultHeader, sizeof(resultHeader));
                logger.debug(std::format("Write {} bytes in pipe for resultHeader", sizeof(resultHeader)));
            }
        }
    }
    logger.info("Renderer worker stopped successfully");
    return EXIT_SUCCESS;
} catch (const std::exception& e) {
    logger.fatal(std::format("Renderer worker terminated due to error: {}", e.what()));
    return EXIT_FAILURE;
}

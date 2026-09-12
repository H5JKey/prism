#include <aws/core/Aws.h>
#include <fcntl.h>
#include <librdkafka/rdkafka.h>
#include <sys/wait.h>
#include <unistd.h>

#include <chrono>
#include <csignal>
#include <cstdlib>
#include <exception>
#include <filesystem>
#include <nlohmann/json.hpp>
#include <stdexcept>

#include "config.hpp"
#include "contract.hpp"
#include "dotenv.hpp"
#include "kafka-consumer.hpp"
#include "kafka-producer.hpp"
#include "logger.hpp"
#include "s3-client.hpp"

using json = nlohmann::json;

struct PipeDescriptor {
    int read_fd = -1;
    int write_fd = -1;

    PipeDescriptor() = default;

    void create() {
        int fds[2];
        if (pipe(fds) == -1) {
            throw std::runtime_error("Failed to create pipe");
        }
        read_fd = fds[0];
        write_fd = fds[1];
    }

    void close_read() {
        if (read_fd >= 0) {
            ::close(read_fd);
            read_fd = -1;
        }
    }

    void close_write() {
        if (write_fd >= 0) {
            ::close(write_fd);
            write_fd = -1;
        }
    }

    ~PipeDescriptor() {
        close_read();
        close_write();
    }

    PipeDescriptor(const PipeDescriptor&) = delete;
    PipeDescriptor& operator=(const PipeDescriptor&) = delete;

    PipeDescriptor(PipeDescriptor&& other) noexcept : read_fd(other.read_fd), write_fd(other.write_fd) {
        other.read_fd = -1;
        other.write_fd = -1;
    }

    PipeDescriptor& operator=(PipeDescriptor&& other) noexcept {
        if (this != &other) {
            close_read();
            close_write();
            read_fd = other.read_fd;
            write_fd = other.write_fd;
            other.read_fd = -1;
            other.write_fd = -1;
        }
        return *this;
    }
};

Aws::SDKOptions options;
int renderer_pid = -1;
std::atomic<bool> running{true};

void signalHandler(int signal) {
    if (signal == SIGINT || signal == SIGTERM) {
        running = false;
        if (renderer_pid > 0) {
            ::kill(renderer_pid, SIGTERM);
        }
    }
}

Logger logger("SERVICE");
int main() try {
    struct sigaction sa;
    sa.sa_handler = signalHandler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    sigaction(SIGTERM, &sa, nullptr);
    sigaction(SIGINT, &sa, nullptr);
    sa.sa_handler = SIG_IGN;
    sigaction(SIGPIPE, &sa, nullptr);

    env::dotenv dotenv(".env");
    Config config;
    config.apply(dotenv);
    config.fromEnvironment();

    Logger::showDebug = config.logDebug();
    Logger::setMinLevel(config.logLevel());

    PipeDescriptor tasksPipe;
    PipeDescriptor resultPipe;
    tasksPipe.create();
    resultPipe.create();

    renderer_pid = fork();
    /* Child (renderer)*/
    if (renderer_pid == 0) {
        tasksPipe.close_write();
        resultPipe.close_read();
        ::dup2(tasksPipe.read_fd, STDIN_FILENO);
        ::dup2(resultPipe.write_fd, STDOUT_FILENO);
        tasksPipe.close_read();
        resultPipe.close_write();
        std::string debugEnv = "RENDERER_LOG_DEBUG=" + std::string(config.logDebug() ? "true" : "false");
        std::string logLevelEnv = "RENDERER_LOG_LEVEL=" + Logger::getStringFromLevel(config.logLevel());
        const char* envp[] = {debugEnv.c_str(), logLevelEnv.c_str(), nullptr};

        std::filesystem::path rendererPath = std::filesystem::read_symlink("/proc/self/exe").parent_path() / "renderer";
        execle(rendererPath.c_str(), "renderer", nullptr, envp);
        throw std::runtime_error(std::format("Failed to start renderer. Exec failed: ", strerror(errno)));
    }
    /* Error*/
    else if (renderer_pid < 0) {
        throw std::runtime_error("Failed to fork renderer process");
    }
    /* Parent (Service) */
    tasksPipe.close_read();
    resultPipe.close_write();
    ::dup2(resultPipe.read_fd, STDIN_FILENO);
    ::dup2(tasksPipe.write_fd, STDOUT_FILENO);
    resultPipe.close_read();
    tasksPipe.close_write();

    Aws::InitAPI(options);
    logger.debug(std::format("Aws initialized"));
    logger.info("Renderer service started");
    S3Client s3client(config.s3Host(), Aws::Auth::AWSCredentials(config.s3AccessKey(), config.s3SecretKey()));
    KafkaConsumer taskConsumer(config.kafkaHost(), config.kafkaTasksGroupID(), config.kafkaTopicTasks());
    KafkaConsumer commandConsumer(config.kafkaHost(), config.kafkaCommandsGroupId(), config.kafkaTopicCommands());
    KafkaProducer producer(config.kafkaHost());

    logger.info(std::format("Listening for messages..."));
    while (running) {
        json inputJson;
        int project_id = -1;
        std::string inputBucket, outputBucket, inputKey, outputKey;
        std::string modelName;
        TaskHeader task;
        std::string message;
        do {
            message = taskConsumer.consume(std::chrono::milliseconds(100));
        } while (running && message.empty());
        if (!running) break;

        logger.info(std::format("Message processing started"));
        try {
            inputJson = json::parse(message);
            task.width = inputJson["render"]["width"];
            task.height = inputJson["render"]["height"];
            task.samples = inputJson["render"]["samples"];
            project_id = inputJson["project_id"];

            inputBucket = inputJson["input"]["bucket"];
            inputKey = inputJson["input"]["key"];

            outputBucket = inputJson["output"]["bucket"];
            outputKey = inputJson["output"]["key"];

            task.background[0] = inputJson["render"]["background"].at(0);
            task.background[1] = inputJson["render"]["background"].at(1);
            task.background[2] = inputJson["render"]["background"].at(2);
            task.sun.direction[0] = inputJson["render"]["sun"]["direction"].at(0);
            task.sun.direction[1] = inputJson["render"]["sun"]["direction"].at(1);
            task.sun.direction[2] = inputJson["render"]["sun"]["direction"].at(2);
            task.sun.color[0] = inputJson["render"]["sun"]["color"].at(0);
            task.sun.color[1] = inputJson["render"]["sun"]["color"].at(1);
            task.sun.color[2] = inputJson["render"]["sun"]["color"].at(2);

            task.sun.exponent = inputJson["render"]["sun"]["exponent"];
        } catch (const std::exception& e) {
            logger.error(std::format("Failed to parse json from string: {}. Error: {}", message, e.what()));
            throw;
        }
        if (config.preview()) {
            task.height = 200 * (static_cast<float>(task.height) / task.width);
            task.width = 200;
            task.samples = 5;
        }
        try {
            std::vector<uint8_t> glbData;
            glbData = s3client.getData(inputBucket, inputKey);
            task.sceneDataSize = glbData.size();

            write(STDOUT_FILENO, &task, sizeof(task));
            logger.debug(std::format("Written {} bytes in pipe for taskHeader", sizeof(task)));
            write(STDOUT_FILENO, glbData.data(), glbData.size());
            logger.debug(std::format("Written {} bytes in pipe for scene", glbData.size()));

            while (running) {
                std::string cmdMsg = commandConsumer.consume(std::chrono::milliseconds(0));

                if (!cmdMsg.empty()) {
                    commandConsumer.commit();
                    try {
                        json command = json::parse(cmdMsg);
                        int target_id = command["project_id"];
                        if (target_id == project_id && command["command"] == "stop") {
                            logger.info(std::format("Stop command received for project {}", project_id));
                            ::kill(renderer_pid, SIGINT);
                        }
                    } catch (const std::exception& e) {
                        logger.error(std::format("Failed to parse command: {}", e.what()));
                    }
                }
                fd_set readfds;
                FD_ZERO(&readfds);
                FD_SET(STDIN_FILENO, &readfds);

                struct timeval tv = {0, 100000};
                int ret = select(STDIN_FILENO + 1, &readfds, nullptr, nullptr, &tv);

                if (ret > 0 && FD_ISSET(STDIN_FILENO, &readfds)) {
                    ResultHeader resultHeader;
                    read(STDIN_FILENO, &resultHeader, sizeof(resultHeader));
                    logger.debug(std::format("Read {} bytes from pipe for resultHeader", sizeof(resultHeader)));
                    if (resultHeader.resultDataSize > 0) {
                        std::vector<uint8_t> result(resultHeader.resultDataSize);
                        size_t total_read = 0;
                        while (total_read < result.size()) {
                            ssize_t bytes_read =
                                read(STDIN_FILENO, result.data() + total_read, result.size() - total_read);
                            if (bytes_read == -1) {
                                if (errno == EINTR) continue;
                                throw std::runtime_error(
                                    std::format("Failed to read result from pipe: {}", std::strerror(errno)));
                            }
                            if (bytes_read == 0) {
                                throw std::runtime_error("Pipe closed unexpectedly");
                            }
                            total_read += bytes_read;
                        }
                        if (total_read == result.size()) {
                            logger.debug(std::format("Read {} bytes from pipe for result", result.size()));

                            s3client.putData(result, outputBucket, outputKey);

                            json outputJson;
                            try {
                                outputJson["project_id"] = project_id;
                                outputJson["output"] = {
                                    {"bucket", outputBucket},
                                    {"key", outputKey},
                                };
                            } catch (const std::exception& e) {
                                logger.error(std::format("Failed to generate output json: {}", e.what()));
                                throw;
                            }

                            producer.produce(config.kafkaTopicOutput(), outputJson.dump());
                        } else {
                            throw std::runtime_error(
                                std::format("Reading from pipe truncates image (read only {}/{} bytes)", total_read,
                                            result.size()));
                        }
                    }
                    taskConsumer.commit();
                    logger.info(std::format("Current message processing finished successfully. Listening..."));
                    break;
                }
                int status;
                pid_t result = waitpid(renderer_pid, &status, WNOHANG);
                if (result == renderer_pid) {
                    throw std::runtime_error("Renderer died");
                }
            }
        } catch (std::exception& e) {
            logger.error(std::format("Processing message: (offset = {}, partition = {}) failed. Reason: {}",
                                     taskConsumer.lastMessage.value().get_offset(),
                                     taskConsumer.lastMessage.value().get_partition(), e.what()));
            int retries = 0;
            if (inputJson.contains("retry_count")) {
                retries = inputJson["retry_count"];
            }
            if (retries < config.maxRetries()) {
                inputJson["retry_count"] = ++retries;
                producer.produce(config.kafkaTopicTasks(), inputJson.dump());
            } else {
                json deadLetter;
                deadLetter["project_id"] = project_id;
                deadLetter["reason"] = e.what();
                producer.produce(config.kafkaTopicDLQ(), deadLetter.dump());
            }
            taskConsumer.commit();
            logger.info(std::format("Failed to process message. Listening..."));
            continue;
        }
    }

    Aws::ShutdownAPI(options);
    ::kill(renderer_pid, SIGTERM);
    waitpid(renderer_pid, nullptr, 0);
    logger.info("Renderer service stopped successfully");

    return EXIT_SUCCESS;
} catch (const env::dotenv::ParseError& e) {
    if (renderer_pid > 0) {
        ::kill(renderer_pid, SIGTERM);
        waitpid(renderer_pid, nullptr, 0);
    }
    logger.error(std::format("Failed to parse .env file '{}' at line {}. Error: {}", e.filename, e.line, e.what()));

    return EXIT_FAILURE;
} catch (const std::exception& e) {
    Aws::ShutdownAPI(options);
    if (renderer_pid > 0) {
        ::kill(renderer_pid, SIGTERM);
        waitpid(renderer_pid, nullptr, 0);
    }
    logger.fatal(std::format("Renderer service terminated due to error: {}", e.what()));

    return EXIT_FAILURE;
}
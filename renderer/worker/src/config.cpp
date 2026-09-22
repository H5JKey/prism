#include "config.hpp"

#include <stdexcept>

void Config::apply(env::dotenv dotenv) {
    try {
        if (dotenv.hasVariable("KAFKA_HOST")) kafkaHost_ = dotenv["KAFKA_HOST"];
        if (dotenv.hasVariable("KAFKA_TASKS_GROUP_ID")) kafkaTasksGroupID_ = dotenv["KAFKA_TASKS_GROUP_ID"];
        if (dotenv.hasVariable("KAFKA_COMMANDS_GROUP_ID")) kafkaCommandsGroupId_ = dotenv["KAFKA_COMMANDS_GROUP_ID"];
        if (dotenv.hasVariable("KAFKA_TOPIC_TASKS")) kafkaTopicTasks_ = dotenv["KAFKA_TOPIC_TASKS"];
        if (dotenv.hasVariable("KAFKA_TOPIC_OUTPUT")) kafkaTopicOutput_ = dotenv["KAFKA_TOPIC_OUTPUT"];
        if (dotenv.hasVariable("KAFKA_TOPIC_DLQ")) kafkaTopicDLQ_ = dotenv["KAFKA_TOPIC_DLQ"];
        if (dotenv.hasVariable("KAFKA_TOPIC_COMMANDS")) kafkaTopicCommands_ = dotenv["KAFKA_TOPIC_COMMANDS"];
        if (dotenv.hasVariable("MAX_RETRIES")) maxRetries_ = dotenv["MAX_RETRIES"];
        if (dotenv.hasVariable("S3_HOST")) s3Host_ = dotenv["S3_HOST"];
        if (dotenv.hasVariable("S3_ACCESS_KEY")) s3AccessKey_ = dotenv["S3_ACCESS_KEY"];
        if (dotenv.hasVariable("S3_SECRET_KEY")) s3SecretKey_ = dotenv["S3_SECRET_KEY"];
        if (dotenv.hasVariable("LOG_LEVEL")) logLevel_ = Logger::getLevelFromString(dotenv["LOG_LEVEL"]);
        if (dotenv.hasVariable("LOG_DEBUG")) logDebug_ = dotenv["LOG_DEBUG"];
        if (dotenv.hasVariable("RENDERER_PREVIEW")) rendererPreview_ = dotenv["RENDERER_PREVIEW"];
        if (dotenv.hasVariable("RENDERER_PREVIEW_MAX_SIZE"))
            rendererPreviewMaxSize_ = dotenv["RENDERER_PREVIEW_MAX_SIZE"];
        if (dotenv.hasVariable("RENDERER_PREVIEW_UPSCALE_FACTOR"))
            rendererPreviewUpscaleFactor_ = dotenv["RENDERER_PREVIEW_UPSCALE_FACTOR"];
        if (dotenv.hasVariable("PROMETHEUS_HOST")) prometheusHost_ = dotenv["PROMETHEUS_HOST"];
    } catch (const env::Value::ValueError& e) {
        throw std::runtime_error(std::format("Invalid value format in .env file. Error: {}.", e.what()));
    }
}

void Config::fromEnvironment() {
    try {
        if (char* ptr = std::getenv("KAFKA_HOST")) kafkaHost_ = env::Value(ptr);
        if (char* ptr = std::getenv("KAFKA_TASKS_GROUP_ID")) kafkaTasksGroupID_ = env::Value(ptr);
        if (char* ptr = std::getenv("KAFKA_COMMANDS_GROUP_ID")) kafkaCommandsGroupId_ = env::Value(ptr);
        if (char* ptr = std::getenv("KAFKA_TOPIC_TASKS")) kafkaTopicTasks_ = env::Value(ptr);
        if (char* ptr = std::getenv("KAFKA_TOPIC_OUTPUT")) kafkaTopicOutput_ = env::Value(ptr);
        if (char* ptr = std::getenv("KAFKA_TOPIC_DLQ")) kafkaTopicDLQ_ = env::Value(ptr);
        if (char* ptr = std::getenv("KAFKA_TOPIC_COMMANDS")) kafkaTopicCommands_ = env::Value(ptr);
        if (char* ptr = std::getenv("MAX_RETRIES")) maxRetries_ = env::Value(ptr);
        if (char* ptr = std::getenv("S3_HOST")) s3Host_ = env::Value(ptr);
        if (char* ptr = std::getenv("S3_ACCESS_KEY")) s3AccessKey_ = env::Value(ptr);
        if (char* ptr = std::getenv("S3_SECRET_KEY")) s3SecretKey_ = env::Value(ptr);
        if (char* ptr = std::getenv("LOG_LEVEL")) logLevel_ = Logger::getLevelFromString(env::Value(ptr));
        if (char* ptr = std::getenv("LOG_DEBUG")) logDebug_ = env::Value(ptr);
        if (char* ptr = std::getenv("RENDERER_PREVIEW")) rendererPreview_ = env::Value(ptr);
        if (char* ptr = std::getenv("RENDERER_PREVIEW_MAX_SIZE")) rendererPreviewMaxSize_ = env::Value(ptr);
        if (char* ptr = std::getenv("RENDERER_PREVIEW_UPSCALE_FACTOR")) rendererPreviewUpscaleFactor_ = env::Value(ptr);
        if (char* ptr = std::getenv("PROMETHEUS_HOST")) prometheusHost_ = env::Value(ptr);
    } catch (const env::Value::ValueError& e) {
        throw std::runtime_error(std::format("Invalid environment variable value format. Error: {}.", e.what()));
    }
}

std::string Config::kafkaHost() const {
    if (!kafkaHost_.has_value()) {
        throw std::runtime_error("KAFKA_HOST not configured");
    }
    return kafkaHost_.value();
}

std::string Config::kafkaTasksGroupID() const {
    if (!kafkaTasksGroupID_.has_value()) {
        throw std::runtime_error("KAFKA_TASKS_GROUP_ID not configured");
    }
    return kafkaTasksGroupID_.value();
}

std::string Config::kafkaCommandsGroupId() const {
    if (!kafkaCommandsGroupId_.has_value()) {
        throw std::runtime_error("KAFKA_COMMANDS_GROUP_ID not configured");
    }
    return kafkaCommandsGroupId_.value();
}

std::string Config::kafkaTopicTasks() const {
    if (!kafkaTopicTasks_.has_value()) {
        throw std::runtime_error("KAFKA_TOPIC_TASKS not configured");
    }
    return kafkaTopicTasks_.value();
}
std::string Config::kafkaTopicOutput() const {
    if (!kafkaTopicOutput_.has_value()) {
        throw std::runtime_error("KAFKA_TOPIC_OUTPUT not configured");
    }
    return kafkaTopicOutput_.value();
}

std::string Config::kafkaTopicDLQ() const {
    if (!kafkaTopicDLQ_.has_value()) {
        throw std::runtime_error("KAFKA_TOPIC_DLQ not configured");
    }
    return kafkaTopicDLQ_.value();
}

std::string Config::kafkaTopicCommands() const {
    if (!kafkaTopicCommands_.has_value()) {
        throw std::runtime_error("KAFKA_TOPIC_COMMANDS not configured");
    }
    return kafkaTopicCommands_.value();
}

int Config::maxRetries() const { return maxRetries_; }

std::string Config::s3Host() const {
    if (!s3Host_.has_value()) {
        throw std::runtime_error("S3_HOST not configured");
    }
    return s3Host_.value();
}
std::string Config::s3AccessKey() const {
    if (!s3AccessKey_.has_value()) {
        throw std::runtime_error("S3_ACCESS_KEY not configured");
    }
    return s3AccessKey_.value();
}
std::string Config::s3SecretKey() const {
    if (!s3SecretKey_.has_value()) {
        throw std::runtime_error("S3_SECRET_KEY not configured");
    }
    return s3SecretKey_.value();
}

std::string Config::prometheusHost() const {
    if (!prometheusHost_.has_value()) {
        throw std::runtime_error("PROMETHEUS_HOST not configured");
    }
    return prometheusHost_.value();
}

Logger::Level Config::logLevel() const { return logLevel_; }
bool Config::logDebug() const { return logDebug_; }
bool Config::rendererPreview() const { return rendererPreview_; }
int Config::rendererPreviewMaxSize() const { return rendererPreviewMaxSize_; }
int Config::rendererPreviewUpscaleFactor() const { return rendererPreviewUpscaleFactor_; }
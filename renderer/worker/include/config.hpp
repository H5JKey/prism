#pragma once
#include <optional>

#include "dotenv.hpp"
#include "logger.hpp"

class Config {
    std::optional<std::string> kafkaHost_;
    std::optional<std::string> kafkaTasksGroupID_;
    std::optional<std::string> kafkaCommandsGroupId_;
    std::optional<std::string> kafkaTopicTasks_;
    std::optional<std::string> kafkaTopicOutput_;
    std::optional<std::string> kafkaTopicDLQ_;
    std::optional<std::string> kafkaTopicCommands_;
    int maxRetries_ = 5;  // default
    std::optional<std::string> s3Host_;
    std::optional<std::string> s3AccessKey_;
    std::optional<std::string> s3SecretKey_;
    Logger::Level logLevel_ = Logger::Level::INFO;  // default
    bool logDebug_ = false;                         // default
    bool preview_ = false;                          // default

   public:
    Config() = default;

    void apply(env::dotenv dotenv);
    void fromEnvironment();

    std::string kafkaHost() const;
    std::string kafkaTasksGroupID() const;
    std::string kafkaCommandsGroupId() const;
    std::string kafkaTopicTasks() const;
    std::string kafkaTopicOutput() const;
    std::string kafkaTopicDLQ() const;
    std::string kafkaTopicCommands() const;
    int maxRetries() const;
    std::string s3Host() const;
    std::string s3AccessKey() const;
    std::string s3SecretKey() const;
    Logger::Level logLevel() const;
    bool logDebug() const;
    bool preview() const;
};
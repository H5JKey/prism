#pragma once
#include <cppkafka.h>
#include <librdkafka/rdkafka.h>

#include <chrono>
#include <string>

#include "logger.hpp"

class KafkaConsumer {
    Logger logger;
    std::string topicName;
    std::string groupId;
    std::string brokerList;
    cppkafka::Configuration config;

    cppkafka::Consumer consumer;

   public:
    std::optional<cppkafka::Message> lastMessage;
    int getEventFd();
    KafkaConsumer(const std::string& brokerList, const std::string& groupId, const std::string& topicName);
    std::string consume(std::chrono::milliseconds timeout = std::chrono::milliseconds(0));
    void commit();
    ~KafkaConsumer();
};
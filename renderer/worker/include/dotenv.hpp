#pragma once
#include <filesystem>
#include <fstream>
#include <map>
#include <stdexcept>
#include <string>

namespace env {
class Value {
   public:
    Value() = default;
    Value(const std::string& str) : rawValue(str) {}
    std::string rawValue;

    operator int() const;
    operator std::string() const;
    operator bool() const;
    operator float() const;

    struct ValueError : public std::runtime_error {
        std::string rawValue;
        ValueError(const std::string& message, const std::string& rawValue)
            : std::runtime_error(message), rawValue(rawValue) {}
    };
};

class dotenv {
    std::string filename;
    struct FileGuard {
        std::fstream& file;

        FileGuard(std::fstream& file) : file(file) {}

        ~FileGuard() { file.close(); }
    };

   public:
    struct ParseError : public std::runtime_error {
        std::string filename;
        size_t line;
        ParseError(const std::string& message, std::string filename, size_t line)
            : std::runtime_error(message), filename(filename), line(line) {}
    };

    struct VariableError : public std::runtime_error {
        std::string variable;
        std::string filename;
        VariableError(const std::string& message, const std::string& filename, const std::string& variable)
            : std::runtime_error(message), variable(variable), filename(filename) {}
    };

    dotenv(std::filesystem::path filename);

    const Value& operator[](const std::string& key) const;

    bool hasVariable(const std::string& key) const;

   private:
    std::map<std::string, Value> variables;
};
}  // namespace env
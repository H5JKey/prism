#include "dotenv.hpp"

env::dotenv::dotenv(std::filesystem::path filename) : filename(filename.string()) {
    std::fstream file(filename);
    FileGuard guard(file);
    std::string line;
    size_t lineCnt = 1;
    while (file >> line) {
        lineCnt++;
        if (line.empty() || line[0] == '#') continue;
        if (line[0] == '=') throw ParseError("Missing key before '='", filename.string(), lineCnt);
        std::string key, strValue;
        auto equal = line.find('=');
        if (equal == std::string::npos) throw ParseError("Missing '='", filename.string(), lineCnt);
        key = line.substr(0, equal);
        strValue = line.substr(equal + 1, line.length() - equal - 1);
        if (strValue.empty()) throw ParseError("Missing value after '='", filename.string(), lineCnt);
        if (strValue[0] == '"') {
            if (strValue[strValue.size() - 1] != '"')
                throw ParseError("Missing closing \"", filename.string(), lineCnt);
            strValue = strValue.substr(1, strValue.length() - 2);
            variables[key] = Value(strValue);
        } else {
            if (strValue.find(' ') != std::string::npos)
                throw ParseError(std::format("invalid space at line {}", lineCnt), filename.string(), lineCnt);
            variables[key] = Value(strValue);
        }
    }
}

const env::Value& env::dotenv::operator[](const std::string& key) const {
    auto it = variables.find(key);
    if (it == variables.end()) throw VariableError(std::format("variable {} doesn't exist", key), filename, key);
    return it->second;
}

bool env::dotenv::hasVariable(const std::string& key) const { return variables.find(key) != variables.end(); }

env::Value::operator std::string() const { return rawValue; }
env::Value::operator int() const {
    try {
        return std::stoi(rawValue);
    } catch (std::exception& e) {
        throw ValueError(std::format("{} is not an integer", rawValue), rawValue);
    }
}
env::Value::operator float() const {
    try {
        return std::stof(rawValue);
    } catch (std::exception& e) {
        throw ValueError(std::format("{} is not a float", rawValue), rawValue);
    }
}
env::Value::operator bool() const {
    if (rawValue == "true") return true;
    if (rawValue == "false") return false;
    throw ValueError(std::format("{} is not a boolean value", rawValue), rawValue);
}

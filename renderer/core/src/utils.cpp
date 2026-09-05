#include "utils.hpp"

#include <stb_image.h>
#include <stb_image_write.h>

#include <cstddef>
#include <filesystem>
#include <format>
#include <fstream>
#include <sstream>

std::string utils::readFromFile(const std::filesystem::path& path) {
    std::string source;
    std::fstream file(path);
    if (!file.is_open()) {
        throw std::runtime_error(std::format("failed to open file {}", path.string()));
    }
    std::stringstream buffer;
    buffer << file.rdbuf();
    source = buffer.str();
    file.close();
    return source;
}

void utils::rgbaToRgb(const std::vector<float>& rgba, std::vector<float>& rgb) {
    if (rgba.size() % 4 != 0) {
        throw std::runtime_error("RGBA buffer size must be multiple of 4");
    }
    rgb.resize((rgba.size() / 4) * 3);
    size_t pixels = rgba.size() / 4;
    for (int i = 0; i < pixels; i++) {
        rgb[i * 3] = rgba[i * 4];
        rgb[i * 3 + 1] = rgba[i * 4 + 1];
        rgb[i * 3 + 2] = rgba[i * 4 + 2];
    }
}

void utils::rgbToRgba(const std::vector<float>& rgb, std::vector<float>& rgba) {
    if (rgb.size() % 3 != 0) {
        throw std::runtime_error("RGB buffer size must be multiple of 3");
    }
    rgba.resize((rgb.size() / 3) * 4);
    size_t pixels = rgb.size() / 3;
    for (int i = 0; i < pixels; i++) {
        rgba[i * 4] = rgb[i * 3];
        rgba[i * 4 + 1] = rgb[i * 3 + 1];
        rgba[i * 4 + 2] = rgb[i * 3 + 2];
        rgba[i * 4 + 3] = 1;
    }
}

void utils::rgbaToRgb(const std::vector<uint8_t>& rgba, std::vector<uint8_t>& rgb) {
    if (rgba.size() % 4 != 0) {
        throw std::runtime_error("RGBA buffer size must be multiple of 4");
    }
    rgb.resize((rgba.size() / 4) * 3);
    size_t pixels = rgba.size() / 4;
    for (int i = 0; i < pixels; i++) {
        rgb[i * 3] = rgba[i * 4];
        rgb[i * 3 + 1] = rgba[i * 4 + 1];
        rgb[i * 3 + 2] = rgba[i * 4 + 2];
    }
}

void utils::rgbToRgba(const std::vector<uint8_t>& rgb, std::vector<uint8_t>& rgba) {
    if (rgb.size() % 3 != 0) {
        throw std::runtime_error("RGB buffer size must be multiple of 3");
    }
    rgba.resize((rgb.size() / 3) * 4);
    size_t pixels = rgb.size() / 3;
    for (int i = 0; i < pixels; i++) {
        rgba[i * 4] = rgb[i * 3];
        rgba[i * 4 + 1] = rgb[i * 3 + 1];
        rgba[i * 4 + 2] = rgb[i * 3 + 2];
        rgba[i * 4 + 3] = 255;
    }
}

std::vector<std::uint8_t> utils::writeToPng(const std::vector<uint8_t>& pixels, int width, int height, int channels) {
    if (pixels.size() == 0) throw std::runtime_error("Writing empty image");

    if (pixels.size() != static_cast<size_t>(width * height * channels)) {
        throw std::runtime_error("Pixel data size mismatch");
    }

    int outputSize = 0;
    std::vector<std::uint8_t> result;
    stbi_write_png_to_func(
        [](void* context, void* data, int size) {
            auto* vec = static_cast<std::vector<std::uint8_t>*>(context);
            uint8_t* bytes = static_cast<std::uint8_t*>(data);
            vec->insert(vec->end(), bytes, bytes + size);
        },
        &result, width, height, channels, pixels.data(), width * channels);
    return result;
}

std::vector<std::uint8_t> utils::writeToPng(const std::vector<float>& pixels, int width, int height, int channels) {
    if (pixels.size() == 0) throw std::runtime_error("Writing empty image");

    if (pixels.size() != static_cast<size_t>(width * height * channels)) {
        throw std::runtime_error("Pixel data size mismatch");
    }
    std::vector<unsigned char> normalizedPixels(width * height * channels);
    for (int i = 0; i < pixels.size(); i++)
        normalizedPixels[i] = static_cast<unsigned char>(std::min(std::max(pixels[i], 0.0f), 1.0f) * 255);

    int outputSize = 0;
    std::vector<std::uint8_t> result;
    stbi_write_png_to_func(
        [](void* context, void* data, int size) {
            auto* vec = static_cast<std::vector<std::uint8_t>*>(context);
            std::uint8_t* bytes = static_cast<std::uint8_t*>(data);
            vec->insert(vec->end(), bytes, bytes + size);
        },
        &result, width, height, channels, normalizedPixels.data(), width * channels);
    return result;
}

void utils::writeToPng(const std::vector<float>& pixels, int width, int height, int channels,
                       const std::filesystem::path& path) {
    if (pixels.size() == 0) throw std::runtime_error("Writing empty image");

    if (pixels.size() != static_cast<size_t>(width * height * channels)) {
        throw std::runtime_error("Pixel data size mismatch");
    }
    std::vector<unsigned char> normalizedPixels(width * height * channels);
    for (int i = 0; i < pixels.size(); i++)
        normalizedPixels[i] = static_cast<unsigned char>(std::min(std::max(pixels[i], 0.0f), 1.0f) * 255);
    stbi_write_png(path.c_str(), width, height, channels, normalizedPixels.data(), width * channels);
}

void utils::writeToPng(const std::vector<uint8_t>& pixels, int width, int height, int channels,
                       const std::filesystem::path& path) {
    if (pixels.size() == 0) throw std::runtime_error("Writing empty image");

    if (pixels.size() != static_cast<size_t>(width * height * channels)) {
        throw std::runtime_error("Pixel data size mismatch");
    }
    stbi_write_png(path.c_str(), width, height, channels, pixels.data(), width * channels);
}

void utils::readImage(const std::filesystem::path& filename, int& width, int& height, int& channels,
                      std::vector<uint8_t>& result) {
    if (!std::filesystem::exists(filename))
        throw std::runtime_error(std::format("Failed to find {} ", filename.string()));
    uint8_t* data = stbi_load(filename.c_str(), &width, &height, &channels, STBI_rgb_alpha);
    if (!data) throw std::runtime_error(std::format("Failed to load file {}", filename.string()));
    result.assign(data, data + width * height * channels);
    stbi_image_free(data);
}

void utils::readImageFromMemory(const std::byte* memoryBuffer, size_t size, int& width, int& height, int& channels,
                                std::vector<uint8_t>& result) {
    if (!memoryBuffer || size == 0) throw std::runtime_error("Data buffer is empty");
    const unsigned char* buffer = reinterpret_cast<const unsigned char*>(memoryBuffer);
    unsigned char* data =
        stbi_load_from_memory(buffer, static_cast<int>(size), &width, &height, &channels, STBI_rgb_alpha);
    channels = 4;

    if (!data) throw std::runtime_error(std::format("Failed to load image from memory"));

    result.assign(data, data + static_cast<size_t>(width) * height * channels);

    stbi_image_free(data);
}

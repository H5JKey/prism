#include "upscaler.hpp"

#include <cmath>
#include <stdexcept>
#include <vector>

void Upscaler::upscale(std::vector<uint8_t>& pixels, int& width, int& height, int channels, int factor) {
    if (factor == 1) return;
    if (factor < 1) {
        throw std::invalid_argument("Upscale factor cannot be less than one");
    }
    if (pixels.size() != static_cast<size_t>(width * height * channels)) {
        throw std::invalid_argument("Pixel data size mismatch");
    }
    int newWidth = width * factor;
    int newHeight = height * factor;
    std::vector<uint8_t> newPixels(newWidth * newHeight * channels);

    for (int y = 0; y < newHeight; ++y) {
        float srcY = (y + 0.5f) / factor - 0.5f;
        int y0 = static_cast<int>(std::floor(srcY));
        int y1 = y0 + 1;
        float wy = srcY - y0;

        if (y0 < 0) {
            y0 = 0;
            wy = 0.0f;
        }
        if (y1 >= height) {
            y1 = height - 1;
        }
        if (y0 >= height) {
            y0 = height - 1;
        }

        for (int x = 0; x < newWidth; ++x) {
            float srcX = (x + 0.5f) / factor - 0.5f;
            int x0 = static_cast<int>(std::floor(srcX));
            int x1 = x0 + 1;
            float wx = srcX - x0;

            if (x0 < 0) {
                x0 = 0;
                wx = 0.0f;
            }
            if (x1 >= width) {
                x1 = width - 1;
            }
            if (x0 >= width) {
                x0 = width - 1;
            }

            for (int c = 0; c < channels; ++c) {
                float p00 = pixels[(y0 * width + x0) * channels + c];
                float p10 = pixels[(y0 * width + x1) * channels + c];
                float p01 = pixels[(y1 * width + x0) * channels + c];
                float p11 = pixels[(y1 * width + x1) * channels + c];

                float top = p00 + (p10 - p00) * wx;
                float bottom = p01 + (p11 - p01) * wx;
                float value = top + (bottom - top) * wy;

                if (value < 0.0f) value = 0.0f;
                if (value > 255.0f) value = 255.0f;

                newPixels[(y * newWidth + x) * channels + c] = static_cast<uint8_t>(value + 0.5f);
            }
        }
    }

    pixels = std::move(newPixels);
    width = newWidth;
    height = newHeight;
}
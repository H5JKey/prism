#pragma once
#include <stdint.h>

#include <vector>

class Upscaler {
   public:
    void upscale(std::vector<uint8_t>& pixels, int& width, int& height, int channels, int factor);
};
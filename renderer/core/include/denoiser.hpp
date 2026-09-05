#pragma once
#include <OpenImageDenoise/oidn.hpp>

#include "render-target.hpp"

class Denoiser {
   public:
    Denoiser();
    void denoise(RenderTarget& target);

   private:
    oidn::DeviceRef device;
};
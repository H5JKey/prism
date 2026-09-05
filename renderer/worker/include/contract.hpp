#pragma once

struct TaskHeader {
    int width;
    int height;
    int samples;
    float background[3];
    struct Sun {
        float color[3];
        float direction[3];
        float exponent;
    } sun;
    unsigned long long sceneDataSize;
};

struct ResultHeader {
    unsigned long long resultDataSize;
};
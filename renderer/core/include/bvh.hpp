#pragma once
#include <glm/glm.hpp>
#include <vector>

class BVH {
    friend class MedianBuilder;

   public:
    BVH();
    struct Node {
        glm::vec4 min, max;
        int left, right;
        int start;
        int count;
        Node() : min(0), max(0), left(-1), right(-1) {}
        void expandToFitTriangle(glm::vec4 v0, glm::vec4 v1, glm::vec4 v2);
    };
    const std::vector<Node>& getNodes() const noexcept;
    const std::vector<int>& getTriangles() const noexcept;
    int getDepth() const noexcept;

   private:
    std::vector<Node> nodes;
    std::vector<int> trianglesIndices;
    int depth;
};
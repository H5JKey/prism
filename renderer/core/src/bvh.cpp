#include "bvh.hpp"

#include <algorithm>
#include <stdexcept>

BVH::BVH() : depth(0) {
    nodes.reserve(128);
    trianglesIndices.reserve(128);
}

void BVH::Node::expandToFitTriangle(glm::vec4 v0, glm::vec4 v1, glm::vec4 v2) {
    max.x = std::max(max.x, std::max(v0.x, std::max(v1.x, v2.x)));
    max.y = std::max(max.y, std::max(v0.y, std::max(v1.y, v2.y)));
    max.z = std::max(max.z, std::max(v0.z, std::max(v1.z, v2.z)));

    min.x = std::min(min.x, std::min(v0.x, std::min(v1.x, v2.x)));
    min.y = std::min(min.y, std::min(v0.y, std::min(v1.y, v2.y)));
    min.z = std::min(min.z, std::min(v0.z, std::min(v1.z, v2.z)));
}

const std::vector<BVH::Node>& BVH::getNodes() const noexcept { return nodes; }

const std::vector<int>& BVH::getTriangles() const noexcept { return trianglesIndices; }

int BVH::getDepth() const noexcept { return depth; }
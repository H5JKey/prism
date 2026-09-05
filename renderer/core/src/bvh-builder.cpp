#include "bvh-builder.hpp"

#include <algorithm>
#include <stdexcept>

BVHBuilder::BVHBuilder(int depthLimit, int trianglesLimit) {
    setDepthLimit(depthLimit);
    setTrianglesLimit(trianglesLimit);
}

void BVHBuilder::setDepthLimit(int limit) {
    if (limit < -1) {
        throw std::runtime_error("Depth limit should be greater than zero or -1 for unlimit");
    }
    depthLimit = limit;
}

void BVHBuilder::setTrianglesLimit(int limit) {
    if (limit < -1) {
        throw std::runtime_error("Triangles limit should be greater than zero -1 for unlimit");
    }
    trianglesLimit = limit;
}

MedianBuilder::MedianBuilder(int depthLimit, int trianglesLimit) : BVHBuilder(depthLimit, trianglesLimit) {}

int MedianBuilder::split(BVH& bvh, int nodeIdx, const std::vector<glm::vec4>& vertices,
                         const std::vector<int>& vertexIndices, std::vector<int>::iterator begin,
                         std::vector<int>::iterator end, int depth) const {
    BVH::Node& node = bvh.nodes[nodeIdx];
    if ((depthLimit == -1 && trianglesLimit == -1 && end - begin <= 1) ||
        (trianglesLimit != -1 && end - begin <= trianglesLimit) || (depthLimit != -1 && depth >= depthLimit)) {
        node.start = begin - bvh.trianglesIndices.begin();
        node.count = end - begin;
        node.left = -1;
        node.right = -1;
        bvh.depth = std::max(depth, bvh.depth);
        return nodeIdx;
    }
    BVH::Node leftNode, rightNode;
    float offsetX = node.max.x - node.min.x;
    float offsetY = node.max.y - node.min.y;
    float offsetZ = node.max.z - node.min.z;

    int axis;
    if (offsetX >= offsetY && offsetX >= offsetZ)
        axis = 0;
    else if (offsetY >= offsetX && offsetY >= offsetZ)
        axis = 1;
    else
        axis = 2;
    std::nth_element(begin, begin + (end - begin) / 2, end, [&](int i, int j) {
        auto v0_i = vertices[vertexIndices[3 * i]];
        auto v1_i = vertices[vertexIndices[3 * i + 1]];
        auto v2_i = vertices[vertexIndices[3 * i + 2]];

        auto v0_j = vertices[vertexIndices[3 * j]];
        auto v1_j = vertices[vertexIndices[3 * j + 1]];
        auto v2_j = vertices[vertexIndices[3 * j + 2]];
        if (axis == 0)
            return v0_i.x + v1_i.x + v2_i.x < v0_j.x + v1_j.x + v2_j.x;
        else if (axis == 1)
            return v0_i.y + v1_i.y + v2_i.y < v0_j.y + v1_j.y + v2_j.y;
        else
            return v0_i.z + v1_i.z + v2_i.z < v0_j.z + v1_j.z + v2_j.z;
    });
    auto median = begin + (end - begin) / 2;
    int medianIdx = *median;
    auto v0 = vertices[vertexIndices[3 * medianIdx]];
    auto v1 = vertices[vertexIndices[3 * medianIdx + 1]];
    auto v2 = vertices[vertexIndices[3 * medianIdx + 2]];

    float splitPos;
    if (axis == 0)
        splitPos = (v0.x + v1.x + v2.x) / 3.0f;
    else if (axis == 1)
        splitPos = (v0.y + v1.y + v2.y) / 3.0f;
    else
        splitPos = (v0.z + v1.z + v2.z) / 3.0f;
    if (axis == 0) {
        leftNode.min = node.min;
        leftNode.max.x = splitPos;
        leftNode.max.y = node.max.y;
        leftNode.max.z = node.max.z;

        rightNode.max = node.max;
        rightNode.min.x = splitPos;
        rightNode.min.y = node.min.y;
        rightNode.min.z = node.min.z;
    } else if (axis == 1) {
        leftNode.min = node.min;
        leftNode.max.y = splitPos;
        leftNode.max.z = node.max.z;
        leftNode.max.x = node.max.x;

        rightNode.max = node.max;
        rightNode.min.y = splitPos;
        rightNode.min.z = node.min.z;
        rightNode.min.x = node.min.x;
    } else {
        leftNode.min = node.min;
        leftNode.max.z = splitPos;
        leftNode.max.x = node.max.x;
        leftNode.max.y = node.max.y;

        rightNode.max = node.max;
        rightNode.min.z = splitPos;
        rightNode.min.y = node.min.y;
        rightNode.min.x = node.min.x;
    }
    for (auto it = begin; it != median; ++it) {
        int triangleIdx = *it;
        auto v0 = vertices[vertexIndices[3 * triangleIdx]];
        auto v1 = vertices[vertexIndices[3 * triangleIdx + 1]];
        auto v2 = vertices[vertexIndices[3 * triangleIdx + 2]];
        leftNode.expandToFitTriangle(v0, v1, v2);
    }

    for (auto it = median; it != end; ++it) {
        int triangleIdx = *it;
        auto v0 = vertices[vertexIndices[3 * triangleIdx]];
        auto v1 = vertices[vertexIndices[3 * triangleIdx + 1]];
        auto v2 = vertices[vertexIndices[3 * triangleIdx + 2]];
        rightNode.expandToFitTriangle(v0, v1, v2);
    }
    if (begin == median || median == end) {
        node.start = begin - bvh.trianglesIndices.begin();
        node.count = end - begin;
        node.left = -1;
        node.right = -1;
        bvh.depth = std::max(depth, bvh.depth);
        return nodeIdx;
    }

    bvh.nodes.push_back(leftNode);
    bvh.nodes[nodeIdx].left = split(bvh, bvh.nodes.size() - 1, vertices, vertexIndices, begin, median, depth + 1);

    bvh.nodes.push_back(rightNode);
    bvh.nodes[nodeIdx].right = split(bvh, bvh.nodes.size() - 1, vertices, vertexIndices, median, end, depth + 1);

    bvh.nodes[nodeIdx].start = 0;
    bvh.nodes[nodeIdx].count = 0;
    return nodeIdx;
}

BVH MedianBuilder::build(const std::vector<glm::vec4>& vertices, const std::vector<int>& vertexIndices) const {
    if (vertexIndices.empty()) {
        BVH bvh;
        return bvh;
    }
    if (vertexIndices.size() % 3 != 0) {
        throw std::runtime_error("Vertex indicies array size must be multiple of 3");
    }
    BVH bvh;

    glm::vec4 max(-std::numeric_limits<float>::infinity()), min(std::numeric_limits<float>::infinity());

    BVH::Node node;
    bvh.trianglesIndices.reserve(vertexIndices.size() / 3);
    for (int triangleIdx = 0; triangleIdx < vertexIndices.size() / 3; ++triangleIdx) {
        if (vertexIndices[3 * triangleIdx] >= vertices.size() || vertexIndices[3 * triangleIdx] < 0 ||
            vertexIndices[3 * triangleIdx + 1] >= vertices.size() || vertexIndices[3 * triangleIdx + 1] < 0 ||
            vertexIndices[3 * triangleIdx + 2] >= vertices.size() || vertexIndices[3 * triangleIdx + 2] < 0) {
            throw std::runtime_error("Vertex index is out of range");
        }
        auto v1 = vertices[vertexIndices[3 * triangleIdx]];
        auto v2 = vertices[vertexIndices[3 * triangleIdx + 1]];
        auto v3 = vertices[vertexIndices[3 * triangleIdx + 2]];

        min.x = std::min(min.x, std::min(v1.x, std::min(v2.x, v3.x)));
        min.y = std::min(min.y, std::min(v1.y, std::min(v2.y, v3.y)));
        min.z = std::min(min.z, std::min(v1.z, std::min(v2.z, v3.z)));

        max.x = std::max(max.x, std::max(v1.x, std::max(v2.x, v3.x)));
        max.y = std::max(max.y, std::max(v1.y, std::max(v2.y, v3.y)));
        max.z = std::max(max.z, std::max(v1.z, std::max(v2.z, v3.z)));
        bvh.trianglesIndices.push_back(triangleIdx);
    }
    node.max = max;
    node.min = min;
    bvh.nodes.push_back(node);
    split(bvh, 0, vertices, vertexIndices, bvh.trianglesIndices.begin(), bvh.trianglesIndices.end(), 0);
    return bvh;
}
#include <gtest/gtest.h>

#include "scene-loader.hpp"
#include "scene.hpp"

TEST(SceneLoaderTest, throwsOnNonexistentFile) {
    SceneLoader loader;

    /* Failed to find non/existent/scene.gltf */
    EXPECT_THROW(loader.loadGltfFromFile("non/existent/scene.gltf"), std::runtime_error);
}

TEST(SceneLoaderTest, throwsOnInvalidFile) {
    SceneLoader loader;

    /* Failed to load data/test-image.png */
    EXPECT_THROW(loader.loadGltfFromFile("tests/data/test-image.jpg"), std::runtime_error);
}

TEST(SceneLoaderTest, loadSceneCorrectly) {
    SceneLoader loader;

    Scene scene;
    EXPECT_NO_THROW(scene = loader.loadGltfFromFile("tests/data/test-scene.glb"));

    /* Testing geometry */
    const auto& objects = scene.getObjects();
    ASSERT_EQ(objects.size(), 1);
    const auto& object = objects[0];
    const auto& mesh = object.mesh;

    std::vector<glm::vec3> expectedVertices = {
        glm::vec3(0.5, -0.5, 0.5),  glm::vec3(-0.5, -0.5, 0.5),  glm::vec3(0.5, 0.5, 0.5),
        glm::vec3(-0.5, 0.5, 0.5),  glm::vec3(-0.5, 0.5, 0.5),   glm::vec3(-0.5, -0.5, 0.5),
        glm::vec3(-0.5, 0.5, -0.5), glm::vec3(-0.5, -0.5, -0.5), glm::vec3(0.5, 0.5, 0.5),
        glm::vec3(-0.5, 0.5, 0.5),  glm::vec3(0.5, 0.5, -0.5),   glm::vec3(-0.5, 0.5, -0.5),
        glm::vec3(-0.5, -0.5, 0.5), glm::vec3(0.5, -0.5, 0.5),   glm::vec3(-0.5, -0.5, -0.5),
        glm::vec3(0.5, -0.5, -0.5), glm::vec3(0.5, -0.5, 0.5),   glm::vec3(0.5, 0.5, 0.5),
        glm::vec3(0.5, -0.5, -0.5), glm::vec3(0.5, 0.5, -0.5),   glm::vec3(0.5, -0.5, -0.5),
        glm::vec3(0.5, 0.5, -0.5),  glm::vec3(-0.5, -0.5, -0.5), glm::vec3(-0.5, 0.5, -0.5)};

    std::vector<int> expectedIndices = {0,  2,  1,  3,  1,  2,  4,  6,  5,  7,  5,  6,  8,  10, 9,  11, 9,  10,
                                        12, 14, 13, 15, 13, 14, 16, 18, 17, 19, 17, 18, 20, 22, 21, 23, 21, 22};
    ASSERT_EQ(expectedVertices.size(), mesh.vertices.size());
    for (int i = 0; i < expectedVertices.size(); i++) {
        EXPECT_NEAR(expectedVertices[i].x, mesh.vertices[i].x, 0.001);
        EXPECT_NEAR(expectedVertices[i].y, mesh.vertices[i].y, 0.001);
        EXPECT_NEAR(expectedVertices[i].z, mesh.vertices[i].z, 0.001);
    }
    EXPECT_EQ(expectedVertices, mesh.vertices);

    std::vector<glm::vec2> expectedTexCoords = {
        glm::vec2(6, 0), glm::vec2(5, 0), glm::vec2(6, 1), glm::vec2(5, 1), glm::vec2(4, 0), glm::vec2(5, 0),
        glm::vec2(4, 1), glm::vec2(5, 1), glm::vec2(2, 0), glm::vec2(1, 0), glm::vec2(2, 1), glm::vec2(1, 1),
        glm::vec2(3, 0), glm::vec2(4, 0), glm::vec2(3, 1), glm::vec2(4, 1), glm::vec2(3, 0), glm::vec2(2, 0),
        glm::vec2(3, 1), glm::vec2(2, 1), glm::vec2(0, 0), glm::vec2(0, 1), glm::vec2(1, 0), glm::vec2(1, 1)};
    ASSERT_EQ(expectedTexCoords.size(), mesh.texCoords.size());
    for (int i = 0; i < expectedVertices.size(); i++) {
        EXPECT_NEAR(expectedTexCoords[i].x, mesh.texCoords[i].x, 0.001);
        EXPECT_NEAR(expectedTexCoords[i].y, mesh.texCoords[i].y, 0.001);
    }
    std::vector<std::vector<float>> expectedTransform = {
        {0.9397, 0.6840, 0, 2}, {0, 0, 1, 0}, {0.3420, -1.8794, 0, 0}, {0, 0, 0, 1}};
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            EXPECT_NEAR(object.transform[i][j], expectedTransform[j][i], 0.001);
        }
    }

    ASSERT_EQ(mesh.primitives.size(), 1);
    EXPECT_EQ(mesh.primitives[0].startVertexIndex, 0);
    EXPECT_EQ(mesh.primitives[0].vertexIndicesCount, 36);
    EXPECT_EQ(mesh.primitives[0].materialId, 0);

    /* Testing Material */
    const auto materials = scene.getMaterials();
    ASSERT_EQ(materials.size(), 1);
    EXPECT_NEAR(materials[0].roughness, 1, 0.0001);
    EXPECT_NEAR(materials[0].metalness, 0, 0.0001);
    EXPECT_NEAR(materials[0].ior, 1.5, 0.0001);
    EXPECT_NEAR(materials[0].albedo.r, 1, 0.0001);
    EXPECT_NEAR(materials[0].albedo.g, 1, 0.0001);
    EXPECT_NEAR(materials[0].albedo.b, 1, 0.0001);
    EXPECT_NEAR(materials[0].emission.r, 0, 0.0001);
    EXPECT_NEAR(materials[0].emission.g, 0, 0.0001);
    EXPECT_NEAR(materials[0].emission.b, 0, 0.0001);
    EXPECT_EQ(materials[0].albedoTextureID, 0);

    /* Testing texture loading */
    const auto textures = scene.getTexturesData();
    ASSERT_EQ(textures.size(), 1);
    EXPECT_EQ(textures[0].width, 256);
    EXPECT_EQ(textures[0].height, 256);
    EXPECT_EQ(textures[0].id, 0);
}
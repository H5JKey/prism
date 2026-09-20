#include <gtest/gtest.h>
#include <stb_image.h>
#include <stb_image_write.h>

#include <cstddef>
#include <cstdlib>
#include <stdexcept>
#include <utils.hpp>

template <typename T>
class ImageReadWriteTest : public ::testing::Test {
   protected:
    int width, height, channels;
    int resultWidth, resultHeight, resultChannels;
    std::vector<uint8_t> result;
    std::vector<uint8_t> expected;
    std::vector<T> pixels;
    std::filesystem::path path;

    void TearDown() override { std::filesystem::remove(path); }
};

using MyTypes = ::testing::Types<uint8_t, float>;
TYPED_TEST_SUITE(ImageReadWriteTest, MyTypes);

TYPED_TEST(ImageReadWriteTest, roundTripWriteRead) {
    this->path = "test.png";
    this->width = 3;
    this->height = 1;
    this->channels = 4;
    if constexpr (std::is_same_v<TypeParam, float>) {
        this->pixels = {-0.5f, 0.0f, 0.5f, 0.0f, 1.0f, 1.5f, 2.0f, 1.0f, 0.2f, 0.5f, 0.8f, 0.5f};
        this->expected = {0, 0, 127, 0, 255, 255, 255, 255, 51, 127, 204, 127};
    } else {
        this->pixels = {0, 0, 128, 0, 255, 255, 255, 255, 51, 128, 204, 128};
        this->expected = {0, 0, 128, 0, 255, 255, 255, 255, 51, 128, 204, 128};
    }
    /* Pixel data size mismatch */
    EXPECT_THROW(utils::writeToPng(this->pixels, this->width + 1, this->height, this->channels, this->path),
                 std::invalid_argument);
    EXPECT_THROW(utils::writeToPng(this->pixels, this->width, this->height + 1, this->channels, this->path),
                 std::invalid_argument);
    EXPECT_THROW(utils::writeToPng(this->pixels, this->width, this->height, (this->channels == 3) ? 4 : 3, this->path),
                 std::invalid_argument);

    EXPECT_NO_THROW(utils::writeToPng(this->pixels, this->width, this->height, this->channels, this->path));
    ASSERT_NO_THROW(
        utils::readImage(this->path, this->resultWidth, this->resultHeight, this->resultChannels, this->result));

    ASSERT_EQ(this->resultWidth, this->width);
    ASSERT_EQ(this->resultHeight, this->height);
    ASSERT_EQ(this->resultChannels, this->channels);
    ASSERT_EQ(this->result.size(), this->expected.size());
    for (int i = 0; i < this->result.size(); i++) EXPECT_NEAR(this->result[i], this->expected[i], 1);
}

TYPED_TEST(ImageReadWriteTest, emptyImageWriteThrows) {
    this->path = "test.png";
    this->width = 0;
    this->height = 0;
    this->channels = 4;
    this->pixels = {};
    this->expected = {};

    /* Writing to empty file */
    EXPECT_THROW(utils::writeToPng(this->pixels, this->width, this->height, this->channels, this->path),
                 std::invalid_argument);
}

TEST(ImageReadWriteTest, readFromUnexistentFileThrows) {
    std::vector<uint8_t> result;
    int width, height, channels;
    EXPECT_THROW(utils::readImage("non/existent.png", width, height, channels, result), std::runtime_error);
}

TEST(ImageReadWriteTest, readRealImageWorks) {
    std::filesystem::path path = "tests/data/test-image.jpg";
    int width = 250;
    int height = 250;
    int channels = 3;
    int resultWidth, resultHeight, resultChannels;
    std::vector<uint8_t> result;

    ASSERT_NO_THROW(utils::readImage(path, resultWidth, resultHeight, resultChannels, result));

    ASSERT_EQ(resultWidth, width);
    ASSERT_EQ(resultHeight, height);
    ASSERT_EQ(resultChannels, channels);
}

TEST(ImageReadWriteTest, readImageFromMemoryWorks) {
    std::filesystem::path path = "tests/data/test-image.jpg";
    int width;
    int height;
    int channels;
    int resultWidth, resultHeight, resultChannels;
    std::vector<uint8_t> result;
    std::vector<uint8_t> resultRGB;
    std::vector<uint8_t> expected;
    int size;
    std::vector<uint8_t> memoryBuffer;

    ASSERT_NO_THROW(utils::readImage(path, width, height, channels, expected));
    ASSERT_NO_THROW(memoryBuffer = utils::writeToPng(expected, width, height, channels));

    ASSERT_NO_THROW(utils::readImageFromMemory(reinterpret_cast<std::byte*>(memoryBuffer.data()), memoryBuffer.size(),
                                               resultWidth, resultHeight, resultChannels, resultRGB));
    ASSERT_EQ(resultWidth, width);
    ASSERT_EQ(resultHeight, height);

    /*Converts result to rgb, because of utils::readImageFromMemory always return result as RGBA*/
    utils::rgbaToRgb(resultRGB, result);

    ASSERT_EQ(result.size(), expected.size());
    for (int i = 0; i < result.size(); i++) EXPECT_EQ(result[i], expected[i]);
}
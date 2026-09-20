#include <gtest/gtest.h>

#include <limits>
#include <stdexcept>
#include <utils.hpp>

template <typename T>
class RGBToRGBATest : public ::testing::Test {
   protected:
    std::vector<T> rgb;
    std::vector<T> rgba;
    std::vector<T> expected;
    void testRgbToRgba() {
        rgb.resize(100);
        rgba.resize(100);
        /* RGB buffer size must be multiple of 3 */
        EXPECT_THROW(utils::rgbToRgba(rgb, rgba), std::invalid_argument);

        rgb = {1, 2, 3, 4, 5, 6, 7, 8, 9};
        rgba.resize(12);
        if constexpr (std::is_same_v<T, float>)
            expected = {1, 2, 3, 1, 4, 5, 6, 1, 7, 8, 9, 1};
        else
            expected = {1, 2, 3, 255, 4, 5, 6, 255, 7, 8, 9, 255};
        EXPECT_NO_THROW(utils::rgbToRgba(rgb, rgba));
        EXPECT_EQ(rgba, expected);

        /* Corner cases */
        rgb = {};
        expected = {};
        rgba.resize(0);
        EXPECT_NO_THROW(utils::rgbToRgba(rgb, rgba));
        EXPECT_EQ(rgba, expected);

        rgb.assign(30, std::numeric_limits<T>().max());
        rgba.resize(40);
        expected.clear();
        expected.reserve(40);
        for (int i = 0; i < 10; ++i) {
            expected.push_back(std::numeric_limits<T>().max());
            expected.push_back(std::numeric_limits<T>().max());
            expected.push_back(std::numeric_limits<T>().max());
            if constexpr (std::is_same_v<T, float>) {
                expected.push_back(1.0f);
            } else {
                expected.push_back(255);
            }
        }
        EXPECT_NO_THROW(utils::rgbToRgba(rgb, rgba));
        EXPECT_EQ(rgba, expected);

        rgb.assign(30, std::numeric_limits<T>().min());
        expected.clear();
        expected.reserve(40);
        for (int i = 0; i < 10; ++i) {
            expected.push_back(std::numeric_limits<T>().min());
            expected.push_back(std::numeric_limits<T>().min());
            expected.push_back(std::numeric_limits<T>().min());
            if constexpr (std::is_same_v<T, float>) {
                expected.push_back(1.0f);
            } else {
                expected.push_back(255);
            }
        }
        rgba.resize(40);
        EXPECT_NO_THROW(utils::rgbToRgba(rgb, rgba));
        EXPECT_EQ(rgba, expected);
    }

    void testRgbaToRgb() {
        rgb.resize(300);
        rgba.resize(301);
        /* RGBA buffer size must be multiple of 4 */
        EXPECT_THROW(utils::rgbaToRgb(rgba, rgb), std::invalid_argument);

        rgba = {1, 2, 3, 1, 4, 5, 6, 0, 7, 8, 9, 1};
        expected = {1, 2, 3, 4, 5, 6, 7, 8, 9};
        rgb.resize(9);
        EXPECT_NO_THROW(utils::rgbaToRgb(rgba, rgb));
        EXPECT_EQ(rgb, expected);

        /* Corner cases */
        rgb = {};
        expected = {};
        rgba.resize(0);
        EXPECT_NO_THROW(utils::rgbaToRgb(rgba, rgb));
        EXPECT_EQ(rgb, expected);

        expected.assign(30, std::numeric_limits<T>().max());
        rgba.clear();
        rgba.reserve(40);
        for (int i = 0; i < 10; ++i) {
            rgba.push_back(std::numeric_limits<T>().max());
            rgba.push_back(std::numeric_limits<T>().max());
            rgba.push_back(std::numeric_limits<T>().max());
            rgba.push_back(static_cast<T>(1));
        }
        rgb.resize(30);
        EXPECT_NO_THROW(utils::rgbaToRgb(rgba, rgb));
        EXPECT_EQ(rgb, expected);

        expected.assign(30, std::numeric_limits<T>().min());
        rgba.clear();
        rgba.reserve(40);
        for (int i = 0; i < 10; ++i) {
            rgba.push_back(std::numeric_limits<T>().min());
            rgba.push_back(std::numeric_limits<T>().min());
            rgba.push_back(std::numeric_limits<T>().min());
            rgba.push_back(static_cast<T>(1));
        }
        rgb.resize(30);
        EXPECT_NO_THROW(utils::rgbaToRgb(rgba, rgb));
        EXPECT_EQ(rgb, expected);
    }

    void testRoundTrip() {
        std::vector<T> rgb_original = {std::numeric_limits<T>().max() / 2,
                                       2,
                                       std::numeric_limits<T>().max(),
                                       std::numeric_limits<T>().min() + 5,
                                       5,
                                       std::numeric_limits<T>().min() / 3,
                                       7,
                                       std::numeric_limits<T>().max() - 10,
                                       9};
        std::vector<T> rgba(12);
        std::vector<T> rgb_result(9);

        EXPECT_NO_THROW(utils::rgbToRgba(rgb_original, rgba));
        if constexpr (std::is_same_v<T, float>) {
            EXPECT_FLOAT_EQ(rgba[3], 1.0f);
            EXPECT_FLOAT_EQ(rgba[7], 1.0f);
            EXPECT_FLOAT_EQ(rgba[11], 1.0f);
        } else {
            EXPECT_EQ(rgba[3], 255);
            EXPECT_EQ(rgba[7], 255);
            EXPECT_EQ(rgba[11], 255);
        }
        EXPECT_NO_THROW(utils::rgbaToRgb(rgba, rgb_result));
        EXPECT_EQ(rgb_result, rgb_original);
    }
};

using MyTypes = ::testing::Types<uint8_t, float>;
TYPED_TEST_SUITE(RGBToRGBATest, MyTypes);

TYPED_TEST(RGBToRGBATest, convertsRGBToRGBA) { this->testRgbToRgba(); }

TYPED_TEST(RGBToRGBATest, convertsRGBAToRGB) { this->testRgbaToRgb(); }

TYPED_TEST(RGBToRGBATest, roundTripConversion) { this->testRoundTrip(); }
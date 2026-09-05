template <typename T>
    requires std::is_same_v<T, uint8_t> || std::is_same_v<T, float>
std::vector<T> RenderTarget::getBufferData(GLuint texture) const {
    if (!texture) {
        throw std::runtime_error("Failed to get texture data. Texture is not created");
    }
    std::vector<T> pixels(width * height * 4);
    glBindTexture(GL_TEXTURE_2D, texture);
    if constexpr (std::is_same_v<T, float>)
        glGetTexImage(GL_TEXTURE_2D, 0, GL_RGBA, GL_FLOAT, pixels.data());
    else
        glGetTexImage(GL_TEXTURE_2D, 0, GL_RGBA, GL_UNSIGNED_BYTE, pixels.data());
    glBindTexture(GL_TEXTURE_2D, 0);
    return pixels;
}

template <typename T>
    requires std::is_same_v<T, uint8_t> || std::is_same_v<T, float>
void RenderTarget::setBufferData(GLuint texture, const std::vector<T>& pixels) {
    if (!texture) {
        throw std::runtime_error("Failed to set texture data. Texture is not created");
    }
    glBindTexture(GL_TEXTURE_2D, texture);
    if constexpr (std::is_same_v<T, float>)
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, width, height, GL_RGBA, GL_FLOAT, pixels.data());
    else
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE, pixels.data());
    glBindTexture(GL_TEXTURE_2D, 0);
}
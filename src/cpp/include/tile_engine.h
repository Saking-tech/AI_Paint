#pragma once

#include <vector>
#include <memory>
#include <cstdint>
#include <opencv2/core.hpp>

namespace ngp {

struct Pixel {
    uint16_t r, g, b, a;
    
    Pixel() : r(0), g(0), b(0), a(65535) {}
    Pixel(uint16_t r, uint16_t g, uint16_t b, uint16_t a = 65535) 
        : r(r), g(g), b(b), a(a) {}
};

class Tile {
public:
    static constexpr int TILE_SIZE = 256;
    
    Tile();
    Tile(int x, int y);
    ~Tile() = default;
    
    // Access pixels
    Pixel& at(int x, int y);
    const Pixel& at(int x, int y) const;
    
    // Operations
    void clear();
    void fill(const Pixel& color);
    Tile clone() const;
    
    // OpenCV conversion
    cv::Mat toMat() const;
    void fromMat(const cv::Mat& mat);
    
    // Position
    int getX() const { return x_; }
    int getY() const { return y_; }
    
    // Dirty tracking
    bool isDirty() const { return dirty_; }
    void setDirty(bool dirty = true) { dirty_ = dirty; }
    
    // Arithmetic operations
    Tile& operator+=(const Tile& other);
    Tile& operator-=(const Tile& other);
    Tile& operator*=(float factor);

private:
    std::vector<Pixel> pixels_;
    int x_, y_;
    bool dirty_;
};

class TileGrid {
public:
    TileGrid(int width, int height);
    TileGrid(const TileGrid& other);  // Copy constructor
    TileGrid& operator=(const TileGrid& other);  // Copy assignment
    ~TileGrid() = default;
    
    // Tile access
    Tile& getTile(int tileX, int tileY);
    const Tile& getTile(int tileX, int tileY) const;
    
    // Pixel access (converts to tile coordinates)
    Pixel& getPixel(int x, int y);
    const Pixel& getPixel(int x, int y) const;
    
    // Dimensions
    int getWidth() const { return width_; }
    int getHeight() const { return height_; }
    int getTileCountX() const { return tileCountX_; }
    int getTileCountY() const { return tileCountY_; }
    
    // Operations
    void clear();
    void fill(const Pixel& color);
    std::vector<Tile*> getDirtyTiles();
    void clearDirtyFlags();
    
    // OpenCV conversion
    cv::Mat toMat() const;
    void fromMat(const cv::Mat& mat);

private:
    std::vector<std::unique_ptr<Tile>> tiles_;
    int width_, height_;
    int tileCountX_, tileCountY_;
};

} // namespace ngp 
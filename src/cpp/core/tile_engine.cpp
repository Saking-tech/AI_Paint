#include "tile_engine.h"
#include <algorithm>
#include <cstring>
#include <opencv2/imgproc.hpp>

namespace ngp {

// Tile implementation

// Tile implementation
Tile::Tile() : x_(0), y_(0), dirty_(false) {
    pixels_.resize(TILE_SIZE * TILE_SIZE);
}

Tile::Tile(int x, int y) : x_(x), y_(y), dirty_(false) {
    pixels_.resize(TILE_SIZE * TILE_SIZE);
}

Pixel& Tile::at(int x, int y) {
    if (x < 0 || x >= TILE_SIZE || y < 0 || y >= TILE_SIZE) {
        static Pixel dummy;
        return dummy;
    }
    dirty_ = true;
    return pixels_[y * TILE_SIZE + x];
}

const Pixel& Tile::at(int x, int y) const {
    if (x < 0 || x >= TILE_SIZE || y < 0 || y >= TILE_SIZE) {
        static const Pixel dummy;
        return dummy;
    }
    return pixels_[y * TILE_SIZE + x];
}

void Tile::clear() {
    std::fill(pixels_.begin(), pixels_.end(), Pixel());
    dirty_ = true;
}

void Tile::fill(const Pixel& color) {
    std::fill(pixels_.begin(), pixels_.end(), color);
    dirty_ = true;
}

Tile Tile::clone() const {
    Tile newTile(x_, y_);
    newTile.pixels_ = pixels_;
    newTile.dirty_ = dirty_;
    return newTile;
}

cv::Mat Tile::toMat() const {
    cv::Mat mat(TILE_SIZE, TILE_SIZE, CV_16UC4);
    for (int y = 0; y < TILE_SIZE; ++y) {
        for (int x = 0; x < TILE_SIZE; ++x) {
            const Pixel& p = at(x, y);
            cv::Vec4w& pixel = mat.at<cv::Vec4w>(y, x);
            pixel[0] = p.b;  // OpenCV uses BGR
            pixel[1] = p.g;
            pixel[2] = p.r;
            pixel[3] = p.a;
        }
    }
    return mat;
}

void Tile::fromMat(const cv::Mat& mat) {
    if (mat.rows != TILE_SIZE || mat.cols != TILE_SIZE) {
        return;
    }
    
    for (int y = 0; y < TILE_SIZE; ++y) {
        for (int x = 0; x < TILE_SIZE; ++x) {
            const cv::Vec4w& pixel = mat.at<cv::Vec4w>(y, x);
            at(x, y) = Pixel(pixel[2], pixel[1], pixel[0], pixel[3]);  // BGR to RGB
        }
    }
    dirty_ = true;
}

Tile& Tile::operator+=(const Tile& other) {
    for (size_t i = 0; i < pixels_.size(); ++i) {
        pixels_[i].r = std::min<uint16_t>(65535, pixels_[i].r + other.pixels_[i].r);
        pixels_[i].g = std::min<uint16_t>(65535, pixels_[i].g + other.pixels_[i].g);
        pixels_[i].b = std::min<uint16_t>(65535, pixels_[i].b + other.pixels_[i].b);
        pixels_[i].a = std::min<uint16_t>(65535, pixels_[i].a + other.pixels_[i].a);
    }
    dirty_ = true;
    return *this;
}

Tile& Tile::operator-=(const Tile& other) {
    for (size_t i = 0; i < pixels_.size(); ++i) {
        pixels_[i].r = std::max<uint16_t>(0, pixels_[i].r - other.pixels_[i].r);
        pixels_[i].g = std::max<uint16_t>(0, pixels_[i].g - other.pixels_[i].g);
        pixels_[i].b = std::max<uint16_t>(0, pixels_[i].b - other.pixels_[i].b);
        pixels_[i].a = std::max<uint16_t>(0, pixels_[i].a - other.pixels_[i].a);
    }
    dirty_ = true;
    return *this;
}

Tile& Tile::operator*=(float factor) {
    for (auto& pixel : pixels_) {
        pixel.r = std::min<uint16_t>(65535, static_cast<uint16_t>(pixel.r * factor));
        pixel.g = std::min<uint16_t>(65535, static_cast<uint16_t>(pixel.g * factor));
        pixel.b = std::min<uint16_t>(65535, static_cast<uint16_t>(pixel.b * factor));
        pixel.a = std::min<uint16_t>(65535, static_cast<uint16_t>(pixel.a * factor));
    }
    dirty_ = true;
    return *this;
}

// TileGrid implementation
TileGrid::TileGrid(int width, int height) : width_(width), height_(height) {
    tileCountX_ = (width + Tile::TILE_SIZE - 1) / Tile::TILE_SIZE;
    tileCountY_ = (height + Tile::TILE_SIZE - 1) / Tile::TILE_SIZE;
    
    tiles_.reserve(tileCountX_ * tileCountY_);
    for (int ty = 0; ty < tileCountY_; ++ty) {
        for (int tx = 0; tx < tileCountX_; ++tx) {
            tiles_.push_back(std::make_unique<Tile>(tx * Tile::TILE_SIZE, ty * Tile::TILE_SIZE));
        }
    }
}

TileGrid::TileGrid(const TileGrid& other) : width_(other.width_), height_(other.height_), 
                                           tileCountX_(other.tileCountX_), tileCountY_(other.tileCountY_) {
    tiles_.reserve(tileCountX_ * tileCountY_);
    for (int ty = 0; ty < tileCountY_; ++ty) {
        for (int tx = 0; tx < tileCountX_; ++tx) {
            tiles_.push_back(std::make_unique<Tile>(other.getTile(tx, ty)));
        }
    }
}

TileGrid& TileGrid::operator=(const TileGrid& other) {
    if (this != &other) {
        width_ = other.width_;
        height_ = other.height_;
        tileCountX_ = other.tileCountX_;
        tileCountY_ = other.tileCountY_;
        
        tiles_.clear();
        tiles_.reserve(tileCountX_ * tileCountY_);
        for (int ty = 0; ty < tileCountY_; ++ty) {
            for (int tx = 0; tx < tileCountX_; ++tx) {
                tiles_.push_back(std::make_unique<Tile>(other.getTile(tx, ty)));
            }
        }
    }
    return *this;
}

Tile& TileGrid::getTile(int tileX, int tileY) {
    if (tileX < 0 || tileX >= tileCountX_ || tileY < 0 || tileY >= tileCountY_) {
        static Tile dummy;
        return dummy;
    }
    return *tiles_[tileY * tileCountX_ + tileX];
}

const Tile& TileGrid::getTile(int tileX, int tileY) const {
    if (tileX < 0 || tileX >= tileCountX_ || tileY < 0 || tileY >= tileCountY_) {
        static const Tile dummy;
        return dummy;
    }
    return *tiles_[tileY * tileCountX_ + tileX];
}

Pixel& TileGrid::getPixel(int x, int y) {
    int tileX = x / Tile::TILE_SIZE;
    int tileY = y / Tile::TILE_SIZE;
    int localX = x % Tile::TILE_SIZE;
    int localY = y % Tile::TILE_SIZE;
    return getTile(tileX, tileY).at(localX, localY);
}

const Pixel& TileGrid::getPixel(int x, int y) const {
    int tileX = x / Tile::TILE_SIZE;
    int tileY = y / Tile::TILE_SIZE;
    int localX = x % Tile::TILE_SIZE;
    int localY = y % Tile::TILE_SIZE;
    return getTile(tileX, tileY).at(localX, localY);
}

void TileGrid::clear() {
    for (auto& tile : tiles_) {
        tile->clear();
    }
}

void TileGrid::fill(const Pixel& color) {
    for (auto& tile : tiles_) {
        tile->fill(color);
    }
}

std::vector<Tile*> TileGrid::getDirtyTiles() {
    std::vector<Tile*> dirtyTiles;
    for (auto& tile : tiles_) {
        if (tile->isDirty()) {
            dirtyTiles.push_back(tile.get());
        }
    }
    return dirtyTiles;
}

void TileGrid::clearDirtyFlags() {
    for (auto& tile : tiles_) {
        tile->setDirty(false);
    }
}

cv::Mat TileGrid::toMat() const {
    cv::Mat mat(height_, width_, CV_16UC4);
    
    for (int y = 0; y < height_; ++y) {
        for (int x = 0; x < width_; ++x) {
            const Pixel& p = getPixel(x, y);
            cv::Vec4w& pixel = mat.at<cv::Vec4w>(y, x);
            pixel[0] = p.b;  // OpenCV uses BGR
            pixel[1] = p.g;
            pixel[2] = p.r;
            pixel[3] = p.a;
        }
    }
    return mat;
}

void TileGrid::fromMat(const cv::Mat& mat) {
    if (mat.rows != height_ || mat.cols != width_) {
        return;
    }
    
    for (int y = 0; y < height_; ++y) {
        for (int x = 0; x < width_; ++x) {
            const cv::Vec4w& pixel = mat.at<cv::Vec4w>(y, x);
            getPixel(x, y) = Pixel(pixel[2], pixel[1], pixel[0], pixel[3]);  // BGR to RGB
        }
    }
}

} // namespace ngp 
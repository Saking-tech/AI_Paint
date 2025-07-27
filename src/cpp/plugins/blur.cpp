#include "plugin_interface.h"
#include "tile_engine.h"
#include <opencv2/imgproc.hpp>
#include <opencv2/core.hpp>
#include <vector>
#include <cmath>

namespace ngp {

// Fast Gaussian blur using box blur approximation
void fast_gaussian_blur(Tile& tile, float sigma) {
    // Convert tile to OpenCV Mat
    cv::Mat mat = tile.toMat();
    
    // Calculate box blur parameters
    int n = 3; // number of box blur passes
    std::vector<int> sizes;
    sizes.reserve(n);
    
    // Calculate box sizes for approximation
    float wIdeal = std::sqrt((12 * sigma * sigma / n) + 1);
    int wl = static_cast<int>(std::floor(wIdeal));
    if (wl % 2 == 0) wl--;
    int wu = wl + 2;
    
    float mIdeal = (12 * sigma * sigma - n * wl * wl - 4 * n * wl - 3 * n) / (-4 * wl - 4);
    int m = static_cast<int>(std::round(mIdeal));
    
    for (int i = 0; i < n; i++) {
        sizes.push_back((i < m ? wl : wu));
    }
    
    // Apply box blur passes
    cv::Mat temp;
    for (int size : sizes) {
        if (size > 1) {
            cv::boxFilter(mat, temp, -1, cv::Size(size, size), cv::Point(-1, -1), true, cv::BORDER_REFLECT);
            mat = temp;
        }
    }
    
    // Convert back to tile
    tile.fromMat(mat);
}

// Plugin interface implementation
extern "C" void process(Tile* data, int w, int h, const FilterParams& params, ProgressCallback* cb) {
    if (!data) return;
    
    // Get parameters
    float sigma = 1.0f;
    auto it = params.floatParams.find("sigma");
    if (it != params.floatParams.end()) {
        sigma = it->second;
    }
    
    // Clamp sigma to reasonable range
    sigma = std::max(0.1f, std::min(50.0f, sigma));
    
    // Process each tile
    int totalTiles = ((w + Tile::TILE_SIZE - 1) / Tile::TILE_SIZE) * 
                     ((h + Tile::TILE_SIZE - 1) / Tile::TILE_SIZE);
    int currentTile = 0;
    
    for (int ty = 0; ty < (h + Tile::TILE_SIZE - 1) / Tile::TILE_SIZE; ++ty) {
        for (int tx = 0; tx < (w + Tile::TILE_SIZE - 1) / Tile::TILE_SIZE; ++tx) {
            // Calculate tile index
            int tileIndex = ty * ((w + Tile::TILE_SIZE - 1) / Tile::TILE_SIZE) + tx;
            
            // Get tile pointer (assuming tiles are stored sequentially)
            Tile* tile = data + tileIndex;
            
            // Apply blur
            fast_gaussian_blur(*tile, sigma);
            
            // Update progress
            currentTile++;
            if (cb && cb->progress) {
                cb->progress(static_cast<float>(currentTile) / totalTiles);
            }
            
            // Check if cancelled
            if (cb && cb->cancelled && cb->cancelled()) {
                return;
            }
        }
    }
}

extern "C" const char* getPluginName() {
    return "Gaussian Blur";
}

extern "C" const char* getPluginVersion() {
    return "1.0.0";
}

extern "C" const char* getPluginDescription() {
    return "Fast Gaussian blur using box blur approximation";
}

} // namespace ngp 
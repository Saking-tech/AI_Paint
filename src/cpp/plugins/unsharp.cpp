#include "plugin_interface.h"
#include "tile_engine.h"
#include <opencv2/imgproc.hpp>
#include <opencv2/core.hpp>
#include <vector>
#include <cmath>

namespace ngp {

// Unsharp mask implementation
void unsharp_mask(Tile& tile, float radius, float amount, float threshold) {
    // Convert tile to OpenCV Mat
    cv::Mat mat = tile.toMat();
    
    // Create blurred version
    cv::Mat blurred;
    if (radius > 0.1f) {
        int kernelSize = static_cast<int>(radius * 2 + 1);
        if (kernelSize % 2 == 0) kernelSize++;
        cv::GaussianBlur(mat, blurred, cv::Size(kernelSize, kernelSize), radius);
    } else {
        blurred = mat.clone();
    }
    
    // Calculate difference
    cv::Mat diff;
    cv::subtract(mat, blurred, diff);
    
    // Apply threshold
    if (threshold > 0) {
        cv::Mat mask;
        cv::cvtColor(diff, mask, cv::COLOR_BGRA2GRAY);
        cv::threshold(mask, mask, threshold * 255, 255, cv::THRESH_BINARY);
        cv::cvtColor(mask, mask, cv::COLOR_GRAY2BGRA);
        cv::multiply(diff, mask, diff, 1.0/255.0);
    }
    
    // Apply amount and add back to original
    cv::Mat result;
    cv::addWeighted(mat, 1.0, diff, amount, 0, result);
    
    // Clamp values to valid range
    cv::Mat clamped;
    cv::threshold(result, clamped, 0, 0, cv::THRESH_TOZERO);
    cv::threshold(clamped, result, 65535, 65535, cv::THRESH_TRUNC);
    
    // Convert back to tile
    tile.fromMat(result);
}

// Plugin interface implementation
extern "C" void process(Tile* data, int w, int h, const FilterParams& params, ProgressCallback* cb) {
    if (!data) return;
    
    // Get parameters
    float radius = 1.0f;
    float amount = 1.0f;
    float threshold = 0.0f;
    
    auto it = params.floatParams.find("radius");
    if (it != params.floatParams.end()) {
        radius = it->second;
    }
    
    it = params.floatParams.find("amount");
    if (it != params.floatParams.end()) {
        amount = it->second;
    }
    
    it = params.floatParams.find("threshold");
    if (it != params.floatParams.end()) {
        threshold = it->second;
    }
    
    // Clamp parameters to reasonable ranges
    radius = std::max(0.1f, std::min(50.0f, radius));
    amount = std::max(0.0f, std::min(5.0f, amount));
    threshold = std::max(0.0f, std::min(1.0f, threshold));
    
    // Process each tile
    int totalTiles = ((w + Tile::TILE_SIZE - 1) / Tile::TILE_SIZE) * 
                     ((h + Tile::TILE_SIZE - 1) / Tile::TILE_SIZE);
    int currentTile = 0;
    
    for (int ty = 0; ty < (h + Tile::TILE_SIZE - 1) / Tile::TILE_SIZE; ++ty) {
        for (int tx = 0; tx < (w + Tile::TILE_SIZE - 1) / Tile::TILE_SIZE; ++tx) {
            // Calculate tile index
            int tileIndex = ty * ((w + Tile::TILE_SIZE - 1) / Tile::TILE_SIZE) + tx;
            
            // Get tile pointer
            Tile* tile = data + tileIndex;
            
            // Apply unsharp mask
            unsharp_mask(*tile, radius, amount, threshold);
            
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
    return "Unsharp Mask";
}

extern "C" const char* getPluginVersion() {
    return "1.0.0";
}

extern "C" const char* getPluginDescription() {
    return "Unsharp mask filter for image sharpening";
}

} // namespace ngp 
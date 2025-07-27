#include "plugin_interface.h"
#include "tile_engine.h"
#include <opencv2/imgproc.hpp>
#include <opencv2/photo.hpp>
#include <opencv2/core.hpp>
#include <vector>
#include <cmath>

namespace ngp {

// Inpainting using OpenCV Telea algorithm
void inpaint_telea(Tile& tile, const std::vector<std::pair<int, int>>& maskPoints, int radius) {
    // Convert tile to OpenCV Mat
    cv::Mat mat = tile.toMat();
    
    // Create mask from points
    cv::Mat mask = cv::Mat::zeros(mat.rows, mat.cols, CV_8UC1);
    
    // Draw mask points
    for (const auto& point : maskPoints) {
        int x = point.first;
        int y = point.second;
        
        if (x >= 0 && x < mask.cols && y >= 0 && y < mask.rows) {
            // Draw a circle around the point
            cv::circle(mask, cv::Point(x, y), radius, cv::Scalar(255), -1);
        }
    }
    
    // Dilate mask to ensure coverage
    cv::Mat dilated;
    cv::dilate(mask, dilated, cv::getStructuringElement(cv::MORPH_ELLIPSE, cv::Size(3, 3)));
    
    // Apply inpainting
    cv::Mat result;
    cv::inpaint(mat, dilated, result, radius, cv::INPAINT_TELEA);
    
    // Convert back to tile
    tile.fromMat(result);
}

// Inpainting using OpenCV Navier-Stokes algorithm
void inpaint_navier_stokes(Tile& tile, const std::vector<std::pair<int, int>>& maskPoints, int radius) {
    // Convert tile to OpenCV Mat
    cv::Mat mat = tile.toMat();
    
    // Create mask from points
    cv::Mat mask = cv::Mat::zeros(mat.rows, mat.cols, CV_8UC1);
    
    // Draw mask points
    for (const auto& point : maskPoints) {
        int x = point.first;
        int y = point.second;
        
        if (x >= 0 && x < mask.cols && y >= 0 && y < mask.rows) {
            cv::circle(mask, cv::Point(x, y), radius, cv::Scalar(255), -1);
        }
    }
    
    // Dilate mask
    cv::Mat dilated;
    cv::dilate(mask, dilated, cv::getStructuringElement(cv::MORPH_ELLIPSE, cv::Size(3, 3)));
    
    // Apply inpainting
    cv::Mat result;
    cv::inpaint(mat, dilated, result, radius, cv::INPAINT_NS);
    
    // Convert back to tile
    tile.fromMat(result);
}

// Advanced inpainting with edge preservation
void inpaint_advanced(Tile& tile, const std::vector<std::pair<int, int>>& maskPoints, int radius) {
    // Convert tile to OpenCV Mat
    cv::Mat mat = tile.toMat();
    
    // Create mask
    cv::Mat mask = cv::Mat::zeros(mat.rows, mat.cols, CV_8UC1);
    
    for (const auto& point : maskPoints) {
        int x = point.first;
        int y = point.second;
        
        if (x >= 0 && x < mask.cols && y >= 0 && y < mask.rows) {
            cv::circle(mask, cv::Point(x, y), radius, cv::Scalar(255), -1);
        }
    }
    
    // Detect edges in the original image
    cv::Mat gray, edges;
    cv::cvtColor(mat, gray, cv::COLOR_BGRA2GRAY);
    cv::Canny(gray, edges, 50, 150);
    
    // Dilate edges to create a wider boundary
    cv::Mat edgeMask;
    cv::dilate(edges, edgeMask, cv::getStructuringElement(cv::MORPH_ELLIPSE, cv::Size(2, 2)));
    
    // Combine with original mask
    cv::Mat combinedMask;
    cv::bitwise_or(mask, edgeMask, combinedMask);
    
    // Apply inpainting
    cv::Mat result;
    cv::inpaint(mat, combinedMask, result, radius, cv::INPAINT_TELEA);
    
    // Convert back to tile
    tile.fromMat(result);
}

// Plugin interface implementation
extern "C" void process(Tile* data, int w, int h, const FilterParams& params, ProgressCallback* cb) {
    if (!data) return;
    
    // Get parameters
    int radius = 3;
    std::string algorithm = "telea";
    
    auto itInt = params.intParams.find("radius");
    if (itInt != params.intParams.end()) {
        radius = itInt->second;
    }
    
    auto itStr = params.stringParams.find("algorithm");
    if (itStr != params.stringParams.end()) {
        algorithm = itStr->second;
    }
    
    // Clamp radius
    radius = std::max(1, std::min(50, radius));
    
    // Create sample mask points (in a real implementation, these would come from user selection)
    std::vector<std::pair<int, int>> maskPoints;
    int centerX = Tile::TILE_SIZE / 2;
    int centerY = Tile::TILE_SIZE / 2;
    
    // Create a circular mask
    for (int y = centerY - radius; y <= centerY + radius; ++y) {
        for (int x = centerX - radius; x <= centerX + radius; ++x) {
            float distance = std::sqrt((x - centerX) * (x - centerX) + (y - centerY) * (y - centerY));
            if (distance <= radius) {
                maskPoints.emplace_back(x, y);
            }
        }
    }
    
    // Process each tile
    int totalTiles = ((w + Tile::TILE_SIZE - 1) / Tile::TILE_SIZE) * 
                     ((h + Tile::TILE_SIZE - 1) / Tile::TILE_SIZE);
    int currentTile = 0;
    
    for (int ty = 0; ty < (h + Tile::TILE_SIZE - 1) / Tile::TILE_SIZE; ++ty) {
        for (int tx = 0; tx < (w + Tile::TILE_SIZE - 1) / Tile::TILE_SIZE; ++tx) {
            int tileIndex = ty * ((w + Tile::TILE_SIZE - 1) / Tile::TILE_SIZE) + tx;
            Tile* tile = data + tileIndex;
            
            // Apply inpainting based on algorithm
            if (algorithm == "navier_stokes") {
                inpaint_navier_stokes(*tile, maskPoints, radius);
            } else if (algorithm == "advanced") {
                inpaint_advanced(*tile, maskPoints, radius);
            } else {
                inpaint_telea(*tile, maskPoints, radius);
            }
            
            // Update progress
            currentTile++;
            if (cb && cb->progress) {
                cb->progress(static_cast<float>(currentTile) / totalTiles);
            }
            
            if (cb && cb->cancelled && cb->cancelled()) {
                return;
            }
        }
    }
}

extern "C" const char* getPluginName() {
    return "Inpaint";
}

extern "C" const char* getPluginVersion() {
    return "1.0.0";
}

extern "C" const char* getPluginDescription() {
    return "AI-powered object removal using inpainting algorithms";
}

} // namespace ngp 
#include "plugin_interface.h"
#include "tile_engine.h"
#include <opencv2/imgproc.hpp>
#include <opencv2/core.hpp>
#include <vector>
#include <cmath>

namespace ngp {

struct SmudgeState {
    std::vector<Pixel> buffer;
    int size;
    bool initialized;
    
    SmudgeState() : size(0), initialized(false) {}
};

// Global smudge state (in a real implementation, this would be per-brush instance)
static SmudgeState g_smudgeState;

// Pick up color from canvas
void pick_up_color(const Tile& tile, int x, int y, int radius) {
    if (!g_smudgeState.initialized || g_smudgeState.size != radius * 2 + 1) {
        g_smudgeState.size = radius * 2 + 1;
        g_smudgeState.buffer.resize(g_smudgeState.size * g_smudgeState.size);
        g_smudgeState.initialized = true;
    }
    
    int index = 0;
    for (int dy = -radius; dy <= radius; ++dy) {
        for (int dx = -radius; dx <= radius; ++dx) {
            int px = x + dx;
            int py = y + dy;
            
            if (px >= 0 && px < Tile::TILE_SIZE && py >= 0 && py < Tile::TILE_SIZE) {
                g_smudgeState.buffer[index] = tile.at(px, py);
            } else {
                g_smudgeState.buffer[index] = Pixel();
            }
            index++;
        }
    }
}

// Apply smudge effect
void apply_smudge(Tile& tile, int x, int y, int radius, float strength) {
    if (!g_smudgeState.initialized) {
        return;
    }
    
    int bufferRadius = (g_smudgeState.size - 1) / 2;
    int index = 0;
    
    for (int dy = -radius; dy <= radius; ++dy) {
        for (int dx = -radius; dx <= radius; ++dx) {
            int px = x + dx;
            int py = y + dy;
            
            if (px >= 0 && px < Tile::TILE_SIZE && py >= 0 && py < Tile::TILE_SIZE) {
                Pixel& dest = tile.at(px, py);
                const Pixel& src = g_smudgeState.buffer[index];
                
                // Calculate distance-based falloff
                float distance = std::sqrt(dx * dx + dy * dy);
                float falloff = 1.0f - (distance / radius);
                falloff = std::max(0.0f, falloff);
                
                // Apply smudge with strength and falloff
                float alpha = strength * falloff;
                dest.r = static_cast<uint16_t>(dest.r * (1 - alpha) + src.r * alpha);
                dest.g = static_cast<uint16_t>(dest.g * (1 - alpha) + src.g * alpha);
                dest.b = static_cast<uint16_t>(dest.b * (1 - alpha) + src.b * alpha);
                dest.a = static_cast<uint16_t>(dest.a * (1 - alpha) + src.a * alpha);
            }
            index++;
        }
    }
    
    // Pick up new colors for next stroke
    pick_up_color(tile, x, y, radius);
}

// Smart smudge with edge detection
void smart_smudge(Tile& tile, int x, int y, int radius, float strength) {
    // Convert tile to OpenCV Mat for edge detection
    cv::Mat mat = tile.toMat();
    
    // Detect edges
    cv::Mat gray, edges;
    cv::cvtColor(mat, gray, cv::COLOR_BGRA2GRAY);
    cv::Canny(gray, edges, 50, 150);
    
    // Calculate distance to nearest edge
    cv::Mat distance;
    cv::distanceTransform(edges, distance, cv::DIST_L2, 3);
    
    // Normalize distance
    double minVal, maxVal;
    cv::minMaxLoc(distance, &minVal, &maxVal);
    if (maxVal > 0) {
        distance = distance / maxVal;
    }
    
    // Apply smudge with edge-aware strength
    if (!g_smudgeState.initialized || g_smudgeState.size != radius * 2 + 1) {
        g_smudgeState.size = radius * 2 + 1;
        g_smudgeState.buffer.resize(g_smudgeState.size * g_smudgeState.size);
        g_smudgeState.initialized = true;
    }
    
    int index = 0;
    for (int dy = -radius; dy <= radius; ++dy) {
        for (int dx = -radius; dx <= radius; ++dx) {
            int px = x + dx;
            int py = y + dy;
            
            if (px >= 0 && px < Tile::TILE_SIZE && py >= 0 && py < Tile::TILE_SIZE) {
                Pixel& dest = tile.at(px, py);
                const Pixel& src = g_smudgeState.buffer[index];
                
                // Get edge distance
                float edgeDist = distance.at<float>(py, px);
                
                // Calculate adaptive strength based on edge distance
                float distance = std::sqrt(dx * dx + dy * dy);
                float falloff = 1.0f - (distance / radius);
                falloff = std::max(0.0f, falloff);
                
                // Reduce strength near edges
                float adaptiveStrength = strength * falloff * edgeDist;
                
                dest.r = static_cast<uint16_t>(dest.r * (1 - adaptiveStrength) + src.r * adaptiveStrength);
                dest.g = static_cast<uint16_t>(dest.g * (1 - adaptiveStrength) + src.g * adaptiveStrength);
                dest.b = static_cast<uint16_t>(dest.b * (1 - adaptiveStrength) + src.b * adaptiveStrength);
                dest.a = static_cast<uint16_t>(dest.a * (1 - adaptiveStrength) + src.a * adaptiveStrength);
            }
            index++;
        }
    }
    
    // Pick up new colors
    pick_up_color(tile, x, y, radius);
}

// Plugin interface implementation
extern "C" void process(Tile* data, int w, int h, const FilterParams& params, ProgressCallback* cb) {
    if (!data) return;
    
    // Get parameters
    float strength = 0.5f;
    int radius = 5;
    bool smartMode = false;
    
    auto it = params.floatParams.find("strength");
    if (it != params.floatParams.end()) {
        strength = it->second;
    }
    
    auto itInt = params.intParams.find("radius");
    if (itInt != params.intParams.end()) {
        radius = itInt->second;
    }
    
    auto itStr = params.stringParams.find("mode");
    if (itStr != params.stringParams.end()) {
        smartMode = (itStr->second == "smart");
    }
    
    // Clamp parameters
    strength = std::max(0.0f, std::min(1.0f, strength));
    radius = std::max(1, std::min(50, radius));
    
    // Process each tile
    int totalTiles = ((w + Tile::TILE_SIZE - 1) / Tile::TILE_SIZE) * 
                     ((h + Tile::TILE_SIZE - 1) / Tile::TILE_SIZE);
    int currentTile = 0;
    
    for (int ty = 0; ty < (h + Tile::TILE_SIZE - 1) / Tile::TILE_SIZE; ++ty) {
        for (int tx = 0; tx < (w + Tile::TILE_SIZE - 1) / Tile::TILE_SIZE; ++tx) {
            int tileIndex = ty * ((w + Tile::TILE_SIZE - 1) / Tile::TILE_SIZE) + tx;
            Tile* tile = data + tileIndex;
            
            // Initialize smudge state for this tile
            pick_up_color(*tile, Tile::TILE_SIZE / 2, Tile::TILE_SIZE / 2, radius);
            
            // Apply smudge effect
            if (smartMode) {
                smart_smudge(*tile, Tile::TILE_SIZE / 2, Tile::TILE_SIZE / 2, radius, strength);
            } else {
                apply_smudge(*tile, Tile::TILE_SIZE / 2, Tile::TILE_SIZE / 2, radius, strength);
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
    return "Smudge";
}

extern "C" const char* getPluginVersion() {
    return "1.0.0";
}

extern "C" const char* getPluginDescription() {
    return "Smudge tool for color blending and liquefying effects";
}

} // namespace ngp 
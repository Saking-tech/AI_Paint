#include "canvas_core.h"
#include <algorithm>
#include <cmath>
#include <opencv2/imgproc.hpp>

namespace ngp {

// Layer implementation
Layer::Layer(const std::string& name, int width, int height) 
    : name_(name), pixels_(width, height), opacity_(1.0f), 
      blendMode_(BlendMode::Normal), visible_(true) {
}

void Layer::addAdjustment(const std::string& type, const std::map<std::string, float>& params) {
    adjustments_.emplace_back(type, params);
}

void Layer::removeAdjustment(int index) {
    if (index >= 0 && index < static_cast<int>(adjustments_.size())) {
        adjustments_.erase(adjustments_.begin() + index);
    }
}

void Layer::clearAdjustments() {
    adjustments_.clear();
}

void Layer::renderTo(TileGrid& target, int x, int y) {
    if (!visible_ || opacity_ <= 0.0f) {
        return;
    }
    
    // Apply adjustments first
    CanvasCore::applyAdjustments(*this);
    
    // Render with blend mode
    for (int ty = 0; ty < pixels_.getTileCountY(); ++ty) {
        for (int tx = 0; tx < pixels_.getTileCountX(); ++tx) {
            Tile& sourceTile = pixels_.getTile(tx, ty);
            Tile& destTile = target.getTile(tx + x / Tile::TILE_SIZE, ty + y / Tile::TILE_SIZE);
            
            for (int py = 0; py < Tile::TILE_SIZE; ++py) {
                for (int px = 0; px < Tile::TILE_SIZE; ++px) {
                    Pixel& dest = destTile.at(px, py);
                    const Pixel& src = sourceTile.at(px, py);
                    
                    CanvasCore::blendPixels(dest, src, blendMode_, opacity_);
                }
            }
        }
    }
}

// CanvasCore implementation
CanvasCore::CanvasCore(int width, int height) 
    : width_(width), height_(height), undoStack_(std::make_unique<UndoStack>()) {
    // Create initial background layer
    addLayer("Background");
}

void CanvasCore::resize(int width, int height) {
    width_ = width;
    height_ = height;
    
    // Resize all layers
    for (auto& layer : layers_) {
        layer = std::make_shared<Layer>(layer->getName(), width, height);
    }
}

std::shared_ptr<Layer> CanvasCore::addLayer(const std::string& name) {
    auto layer = std::make_shared<Layer>(name, width_, height_);
    layers_.push_back(layer);
    return layer;
}

void CanvasCore::removeLayer(int index) {
    if (index >= 0 && index < static_cast<int>(layers_.size())) {
        layers_.erase(layers_.begin() + index);
    }
}

void CanvasCore::moveLayer(int fromIndex, int toIndex) {
    if (fromIndex >= 0 && fromIndex < static_cast<int>(layers_.size()) &&
        toIndex >= 0 && toIndex < static_cast<int>(layers_.size())) {
        auto layer = layers_[fromIndex];
        layers_.erase(layers_.begin() + fromIndex);
        layers_.insert(layers_.begin() + toIndex, layer);
    }
}

std::shared_ptr<Layer> CanvasCore::getLayer(int index) {
    if (index >= 0 && index < static_cast<int>(layers_.size())) {
        return layers_[index];
    }
    return nullptr;
}

void CanvasCore::renderTo(TileGrid& target) {
    target.clear();
    
    // Render layers from bottom to top
    for (auto& layer : layers_) {
        layer->renderTo(target, 0, 0);
    }
}

cv::Mat CanvasCore::getCompositedImage() {
    TileGrid composite(width_, height_);
    renderTo(composite);
    return composite.toMat();
}

void CanvasCore::beginStroke() {
    // Create snapshots of all layers for undo
    std::vector<std::unique_ptr<TileGrid>> snapshots;
    for (auto& layer : layers_) {
        snapshots.push_back(std::make_unique<TileGrid>(layer->getPixels()));
    }
    undoStack_->pushState(snapshots, "Brush Stroke");
}

void CanvasCore::endStroke() {
    // Stroke is already recorded in beginStroke
}

void CanvasCore::undo() {
    if (undoStack_->canUndo()) {
        auto snapshots = undoStack_->popState();
        for (size_t i = 0; i < layers_.size() && i < snapshots.size(); ++i) {
            layers_[i]->getPixels() = *snapshots[i];
        }
    }
}

void CanvasCore::redo() {
    if (undoStack_->canRedo()) {
        auto snapshots = undoStack_->redoState();
        for (size_t i = 0; i < layers_.size() && i < snapshots.size(); ++i) {
            layers_[i]->getPixels() = *snapshots[i];
        }
    }
}

bool CanvasCore::canUndo() const {
    return undoStack_->canUndo();
}

bool CanvasCore::canRedo() const {
    return undoStack_->canRedo();
}

void CanvasCore::drawBrushStroke(int layerIndex, const std::vector<std::pair<int, int>>& points, 
                                float size, float opacity, const Pixel& color) {
    if (layerIndex < 0 || layerIndex >= static_cast<int>(layers_.size())) {
        return;
    }
    
    auto& layer = layers_[layerIndex];
    auto& pixels = layer->getPixels();
    
    // Simple circular brush implementation
    for (const auto& point : points) {
        int x = point.first;
        int y = point.second;
        int radius = static_cast<int>(size / 2.0f);
        
        for (int dy = -radius; dy <= radius; ++dy) {
            for (int dx = -radius; dx <= radius; ++dx) {
                int px = x + dx;
                int py = y + dy;
                
                if (px >= 0 && px < width_ && py >= 0 && py < height_) {
                    float distance = std::sqrt(dx * dx + dy * dy);
                    if (distance <= radius) {
                        float alpha = 1.0f - (distance / radius);
                        alpha *= opacity;
                        
                        Pixel& dest = pixels.getPixel(px, py);
                        dest.r = static_cast<uint16_t>(dest.r * (1 - alpha) + color.r * alpha);
                        dest.g = static_cast<uint16_t>(dest.g * (1 - alpha) + color.g * alpha);
                        dest.b = static_cast<uint16_t>(dest.b * (1 - alpha) + color.b * alpha);
                        dest.a = static_cast<uint16_t>(dest.a * (1 - alpha) + color.a * alpha);
                    }
                }
            }
        }
    }
}

void CanvasCore::eraseBrushStroke(int layerIndex, const std::vector<std::pair<int, int>>& points, 
                                 float size, float opacity) {
    if (layerIndex < 0 || layerIndex >= static_cast<int>(layers_.size())) {
        return;
    }
    
    auto& layer = layers_[layerIndex];
    auto& pixels = layer->getPixels();
    
    // Eraser implementation
    for (const auto& point : points) {
        int x = point.first;
        int y = point.second;
        int radius = static_cast<int>(size / 2.0f);
        
        for (int dy = -radius; dy <= radius; ++dy) {
            for (int dx = -radius; dx <= radius; ++dx) {
                int px = x + dx;
                int py = y + dy;
                
                if (px >= 0 && px < width_ && py >= 0 && py < height_) {
                    float distance = std::sqrt(dx * dx + dy * dy);
                    if (distance <= radius) {
                        float alpha = 1.0f - (distance / radius);
                        alpha *= opacity;
                        
                        Pixel& dest = pixels.getPixel(px, py);
                        dest.a = static_cast<uint16_t>(dest.a * (1 - alpha));
                    }
                }
            }
        }
    }
}

void CanvasCore::setSelection(const std::vector<std::pair<int, int>>& points) {
    selection_ = points;
}

void CanvasCore::clearSelection() {
    selection_.clear();
}

void CanvasCore::applyFilter(int layerIndex, const std::string& filterType, 
                            const std::map<std::string, float>& params) {
    if (layerIndex < 0 || layerIndex >= static_cast<int>(layers_.size())) {
        return;
    }
    
    // This would interface with the plugin system
    // For now, just add as an adjustment
    layers_[layerIndex]->addAdjustment(filterType, params);
}

void CanvasCore::blendPixels(Pixel& dest, const Pixel& src, BlendMode mode, float opacity) {
    float srcAlpha = src.a / 65535.0f * opacity;
    float destAlpha = dest.a / 65535.0f;
    
    if (srcAlpha <= 0.0f) {
        return;
    }
    
    float srcR = src.r / 65535.0f;
    float srcG = src.g / 65535.0f;
    float srcB = src.b / 65535.0f;
    
    float destR = dest.r / 65535.0f;
    float destG = dest.g / 65535.0f;
    float destB = dest.b / 65535.0f;
    
    float resultR, resultG, resultB;
    
    switch (mode) {
        case BlendMode::Normal:
            resultR = srcR;
            resultG = srcG;
            resultB = srcB;
            break;
        case BlendMode::Multiply:
            resultR = destR * srcR;
            resultG = destG * srcG;
            resultB = destB * srcB;
            break;
        case BlendMode::Screen:
            resultR = 1.0f - (1.0f - destR) * (1.0f - srcR);
            resultG = 1.0f - (1.0f - destG) * (1.0f - srcG);
            resultB = 1.0f - (1.0f - destB) * (1.0f - srcB);
            break;
        case BlendMode::Overlay:
            resultR = destR < 0.5f ? 2.0f * destR * srcR : 1.0f - 2.0f * (1.0f - destR) * (1.0f - srcR);
            resultG = destG < 0.5f ? 2.0f * destG * srcG : 1.0f - 2.0f * (1.0f - destG) * (1.0f - srcG);
            resultB = destB < 0.5f ? 2.0f * destB * srcB : 1.0f - 2.0f * (1.0f - destB) * (1.0f - srcB);
            break;
        default:
            resultR = srcR;
            resultG = srcG;
            resultB = srcB;
            break;
    }
    
    // Blend with destination
    float finalAlpha = srcAlpha + destAlpha * (1.0f - srcAlpha);
    if (finalAlpha > 0.0f) {
        dest.r = static_cast<uint16_t>((resultR * srcAlpha + destR * destAlpha * (1.0f - srcAlpha)) / finalAlpha * 65535.0f);
        dest.g = static_cast<uint16_t>((resultG * srcAlpha + destG * destAlpha * (1.0f - srcAlpha)) / finalAlpha * 65535.0f);
        dest.b = static_cast<uint16_t>((resultB * srcAlpha + destB * destAlpha * (1.0f - srcAlpha)) / finalAlpha * 65535.0f);
        dest.a = static_cast<uint16_t>(finalAlpha * 65535.0f);
    }
}

void CanvasCore::applyAdjustments(Layer& layer) {
    // This would apply the adjustment stack
    // For now, it's a placeholder
}

} // namespace ngp 
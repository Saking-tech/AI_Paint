#pragma once

#include "tile_engine.h"
#include "undo_stack.h"
#include <vector>
#include <memory>
#include <functional>
#include <map>

namespace ngp {

enum class BlendMode {
    Normal,
    Multiply,
    Screen,
    Overlay,
    SoftLight,
    HardLight,
    ColorDodge,
    ColorBurn,
    Darken,
    Lighten,
    Difference,
    Exclusion
};

class Layer {
public:
    Layer(const std::string& name, int width, int height);
    ~Layer() = default;
    
    // Properties
    std::string getName() const { return name_; }
    void setName(const std::string& name) { name_ = name; }
    
    float getOpacity() const { return opacity_; }
    void setOpacity(float opacity) { opacity_ = std::clamp(opacity, 0.0f, 1.0f); }
    
    BlendMode getBlendMode() const { return blendMode_; }
    void setBlendMode(BlendMode mode) { blendMode_ = mode; }
    
    bool isVisible() const { return visible_; }
    void setVisible(bool visible) { visible_ = visible; }
    
    // Pixel data
    TileGrid& getPixels() { return pixels_; }
    const TileGrid& getPixels() const { return pixels_; }
    
    // Mask
    std::shared_ptr<Layer> getClipMask() const { return clipMask_; }
    void setClipMask(std::shared_ptr<Layer> mask) { clipMask_ = mask; }
    
    // Adjustment stack
    void addAdjustment(const std::string& type, const std::map<std::string, float>& params);
    void removeAdjustment(int index);
    void clearAdjustments();
    
    // Rendering
    void renderTo(TileGrid& target, int x, int y);

private:
    std::string name_;
    TileGrid pixels_;
    float opacity_;
    BlendMode blendMode_;
    bool visible_;
    std::shared_ptr<Layer> clipMask_;
    std::vector<std::pair<std::string, std::map<std::string, float>>> adjustments_;
};

class CanvasCore {
public:
    CanvasCore(int width, int height);
    ~CanvasCore() = default;
    
    // Document properties
    int getWidth() const { return width_; }
    int getHeight() const { return height_; }
    void resize(int width, int height);
    
    // Layer management
    std::shared_ptr<Layer> addLayer(const std::string& name);
    void removeLayer(int index);
    void moveLayer(int fromIndex, int toIndex);
    std::shared_ptr<Layer> getLayer(int index);
    const std::vector<std::shared_ptr<Layer>>& getLayers() const { return layers_; }
    
    // Rendering
    void renderTo(TileGrid& target);
    cv::Mat getCompositedImage();
    
    // Undo/Redo
    void beginStroke();
    void endStroke();
    void undo();
    void redo();
    bool canUndo() const;
    bool canRedo() const;
    
    // Brush operations
    void drawBrushStroke(int layerIndex, const std::vector<std::pair<int, int>>& points, 
                        float size, float opacity, const Pixel& color);
    void eraseBrushStroke(int layerIndex, const std::vector<std::pair<int, int>>& points, 
                         float size, float opacity);
    
    // Selection
    void setSelection(const std::vector<std::pair<int, int>>& points);
    void clearSelection();
    bool hasSelection() const { return !selection_.empty(); }
    
    // Filters and effects
    void applyFilter(int layerIndex, const std::string& filterType, 
                    const std::map<std::string, float>& params);

    // Helper methods
    static void blendPixels(Pixel& dest, const Pixel& src, BlendMode mode, float opacity);
    static void applyAdjustments(Layer& layer);

private:
    int width_, height_;
    std::vector<std::shared_ptr<Layer>> layers_;
    std::vector<std::pair<int, int>> selection_;
    std::unique_ptr<UndoStack> undoStack_;
};

} // namespace ngp 
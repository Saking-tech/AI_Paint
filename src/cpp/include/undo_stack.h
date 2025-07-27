#pragma once

#include "tile_engine.h"
#include <vector>
#include <memory>
#include <string>

namespace ngp {

struct UndoState {
    std::vector<std::unique_ptr<TileGrid>> layerSnapshots;
    std::string description;
    int timestamp;
    
    UndoState(const std::string& desc) : description(desc), timestamp(0) {}
};

class UndoStack {
public:
    UndoStack(size_t maxStates = 50);
    ~UndoStack() = default;
    
    // State management
    void pushState(const std::vector<std::unique_ptr<TileGrid>>& snapshots, 
                  const std::string& description);
    std::vector<std::unique_ptr<TileGrid>> popState();
    std::vector<std::unique_ptr<TileGrid>> redoState();
    
    // Status
    bool canUndo() const { return currentIndex_ > 0; }
    bool canRedo() const { return currentIndex_ < states_.size() - 1; }
    size_t getStateCount() const { return states_.size(); }
    size_t getCurrentIndex() const { return currentIndex_; }
    
    // Information
    std::string getUndoDescription() const;
    std::string getRedoDescription() const;
    
    // Management
    void clear();
    void setMaxStates(size_t maxStates) { maxStates_ = maxStates; }

private:
    std::vector<std::unique_ptr<UndoState>> states_;
    size_t currentIndex_;
    size_t maxStates_;
    
    void trimStates();
};

} // namespace ngp 
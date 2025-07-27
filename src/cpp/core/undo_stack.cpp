#include "undo_stack.h"
#include <algorithm>
#include <chrono>

namespace ngp {

UndoStack::UndoStack(size_t maxStates) : currentIndex_(0), maxStates_(maxStates) {
}

void UndoStack::pushState(const std::vector<std::unique_ptr<TileGrid>>& snapshots, 
                         const std::string& description) {
    // Remove any states after current index (when we're not at the end)
    if (currentIndex_ < states_.size()) {
        states_.erase(states_.begin() + currentIndex_, states_.end());
    }
    
    // Create new state
    auto state = std::make_unique<UndoState>(description);
    state->layerSnapshots.reserve(snapshots.size());
    
    for (const auto& snapshot : snapshots) {
        state->layerSnapshots.push_back(std::make_unique<TileGrid>(*snapshot));
    }
    
    // Add timestamp
    auto now = std::chrono::system_clock::now();
    state->timestamp = std::chrono::duration_cast<std::chrono::seconds>(
        now.time_since_epoch()).count();
    
    // Add to states
    states_.push_back(std::move(state));
    currentIndex_++;
    
    // Trim if we exceed max states
    trimStates();
}

std::vector<std::unique_ptr<TileGrid>> UndoStack::popState() {
    if (!canUndo()) {
        return {};
    }
    
    currentIndex_--;
    auto& state = states_[currentIndex_];
    
    std::vector<std::unique_ptr<TileGrid>> result;
    result.reserve(state->layerSnapshots.size());
    
    for (const auto& snapshot : state->layerSnapshots) {
        result.push_back(std::make_unique<TileGrid>(*snapshot));
    }
    
    return result;
}

std::vector<std::unique_ptr<TileGrid>> UndoStack::redoState() {
    if (!canRedo()) {
        return {};
    }
    
    auto& state = states_[currentIndex_];
    currentIndex_++;
    
    std::vector<std::unique_ptr<TileGrid>> result;
    result.reserve(state->layerSnapshots.size());
    
    for (const auto& snapshot : state->layerSnapshots) {
        result.push_back(std::make_unique<TileGrid>(*snapshot));
    }
    
    return result;
}

std::string UndoStack::getUndoDescription() const {
    if (!canUndo()) {
        return "";
    }
    return states_[currentIndex_ - 1]->description;
}

std::string UndoStack::getRedoDescription() const {
    if (!canRedo()) {
        return "";
    }
    return states_[currentIndex_]->description;
}

void UndoStack::clear() {
    states_.clear();
    currentIndex_ = 0;
}

void UndoStack::trimStates() {
    if (states_.size() <= maxStates_) {
        return;
    }
    
    // Remove oldest states, keeping the most recent ones
    size_t toRemove = states_.size() - maxStates_;
    states_.erase(states_.begin(), states_.begin() + toRemove);
    currentIndex_ = std::max<size_t>(0, currentIndex_ - toRemove);
}

} // namespace ngp 
#pragma once

#include "tile_engine.h"
#include <map>
#include <string>
#include <functional>

namespace ngp {

struct FilterParams {
    std::map<std::string, float> floatParams;
    std::map<std::string, int> intParams;
    std::map<std::string, std::string> stringParams;
};

struct ProgressCallback {
    std::function<void(float)> progress;
    std::function<bool()> cancelled;
    
    ProgressCallback() : progress([](float){}), cancelled([](){ return false; }) {}
};

// Plugin interface - all plugins must implement this
extern "C" {
    void process(Tile* data, int w, int h, const FilterParams& params, ProgressCallback* cb);
    const char* getPluginName();
    const char* getPluginVersion();
    const char* getPluginDescription();
}

// Plugin registry
class PluginRegistry {
public:
    static PluginRegistry& getInstance();
    
    void registerPlugin(const std::string& name, 
                       std::function<void(Tile*, int, int, const FilterParams&, ProgressCallback*)> func);
    bool hasPlugin(const std::string& name) const;
    void callPlugin(const std::string& name, Tile* data, int w, int h, 
                   const FilterParams& params, ProgressCallback* cb);
    
    std::vector<std::string> getPluginNames() const;

private:
    PluginRegistry() = default;
    std::map<std::string, std::function<void(Tile*, int, int, const FilterParams&, ProgressCallback*)>> plugins_;
};

} // namespace ngp 
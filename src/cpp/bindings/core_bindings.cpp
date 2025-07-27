#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include "../include/tile_engine.h"
#include "../include/canvas_core.h"
#include "../include/undo_stack.h"

namespace py = pybind11;

PYBIND11_MODULE(ngp_core_python, m) {
    m.doc() = "Next-Gen Paint Core Python Bindings";
    
    // Pixel class
    py::class_<ngp::Pixel>(m, "Pixel")
        .def(py::init<>())
        .def(py::init<uint16_t, uint16_t, uint16_t, uint16_t>())
        .def_readwrite("r", &ngp::Pixel::r)
        .def_readwrite("g", &ngp::Pixel::g)
        .def_readwrite("b", &ngp::Pixel::b)
        .def_readwrite("a", &ngp::Pixel::a);
    
    // Tile class
    py::class_<ngp::Tile>(m, "Tile")
        .def(py::init<>())
        .def(py::init<int, int>())
        .def("at", static_cast<ngp::Pixel&(ngp::Tile::*)(int, int)>(&ngp::Tile::at))
        .def("clear", &ngp::Tile::clear)
        .def("fill", &ngp::Tile::fill)
        .def("clone", &ngp::Tile::clone)
        .def("get_x", &ngp::Tile::getX)
        .def("get_y", &ngp::Tile::getY)
        .def("is_dirty", &ngp::Tile::isDirty)
        .def("set_dirty", &ngp::Tile::setDirty)
        .def_readonly_static("TILE_SIZE", &ngp::Tile::TILE_SIZE);
    
    // TileGrid class
    py::class_<ngp::TileGrid>(m, "TileGrid")
        .def(py::init<int, int>())
        .def("get_tile", static_cast<ngp::Tile&(ngp::TileGrid::*)(int, int)>(&ngp::TileGrid::getTile))
        .def("get_pixel", static_cast<ngp::Pixel&(ngp::TileGrid::*)(int, int)>(&ngp::TileGrid::getPixel))
        .def("get_width", &ngp::TileGrid::getWidth)
        .def("get_height", &ngp::TileGrid::getHeight)
        .def("get_tile_count_x", &ngp::TileGrid::getTileCountX)
        .def("get_tile_count_y", &ngp::TileGrid::getTileCountY)
        .def("clear", &ngp::TileGrid::clear)
        .def("fill", &ngp::TileGrid::fill)
        .def("get_dirty_tiles", &ngp::TileGrid::getDirtyTiles)
        .def("clear_dirty_flags", &ngp::TileGrid::clearDirtyFlags);
    
    // BlendMode enum
    py::enum_<ngp::BlendMode>(m, "BlendMode")
        .value("Normal", ngp::BlendMode::Normal)
        .value("Multiply", ngp::BlendMode::Multiply)
        .value("Screen", ngp::BlendMode::Screen)
        .value("Overlay", ngp::BlendMode::Overlay)
        .value("SoftLight", ngp::BlendMode::SoftLight)
        .value("HardLight", ngp::BlendMode::HardLight)
        .value("ColorDodge", ngp::BlendMode::ColorDodge)
        .value("ColorBurn", ngp::BlendMode::ColorBurn)
        .value("Darken", ngp::BlendMode::Darken)
        .value("Lighten", ngp::BlendMode::Lighten)
        .value("Difference", ngp::BlendMode::Difference)
        .value("Exclusion", ngp::BlendMode::Exclusion);
    
    // Layer class
    py::class_<ngp::Layer, std::shared_ptr<ngp::Layer>>(m, "Layer")
        .def(py::init<const std::string&, int, int>())
        .def("get_name", &ngp::Layer::getName)
        .def("set_name", &ngp::Layer::setName)
        .def("get_opacity", &ngp::Layer::getOpacity)
        .def("set_opacity", &ngp::Layer::setOpacity)
        .def("get_blend_mode", &ngp::Layer::getBlendMode)
        .def("set_blend_mode", &ngp::Layer::setBlendMode)
        .def("is_visible", &ngp::Layer::isVisible)
        .def("set_visible", &ngp::Layer::setVisible)
        .def("get_pixels", static_cast<ngp::TileGrid&(ngp::Layer::*)()>(&ngp::Layer::getPixels))
        .def("get_clip_mask", &ngp::Layer::getClipMask)
        .def("set_clip_mask", &ngp::Layer::setClipMask)
        .def("add_adjustment", &ngp::Layer::addAdjustment)
        .def("remove_adjustment", &ngp::Layer::removeAdjustment)
        .def("clear_adjustments", &ngp::Layer::clearAdjustments)
        .def("render_to", &ngp::Layer::renderTo);
    
    // CanvasCore class
    py::class_<ngp::CanvasCore>(m, "CanvasCore")
        .def(py::init<int, int>())
        .def("get_width", &ngp::CanvasCore::getWidth)
        .def("get_height", &ngp::CanvasCore::getHeight)
        .def("resize", &ngp::CanvasCore::resize)
        .def("add_layer", &ngp::CanvasCore::addLayer)
        .def("remove_layer", &ngp::CanvasCore::removeLayer)
        .def("move_layer", &ngp::CanvasCore::moveLayer)
        .def("get_layer", &ngp::CanvasCore::getLayer)
        .def("get_layers", &ngp::CanvasCore::getLayers)
        .def("render_to", &ngp::CanvasCore::renderTo)
        .def("get_composited_image", &ngp::CanvasCore::getCompositedImage)
        .def("begin_stroke", &ngp::CanvasCore::beginStroke)
        .def("end_stroke", &ngp::CanvasCore::endStroke)
        .def("undo", &ngp::CanvasCore::undo)
        .def("redo", &ngp::CanvasCore::redo)
        .def("can_undo", &ngp::CanvasCore::canUndo)
        .def("can_redo", &ngp::CanvasCore::canRedo)
        .def("draw_brush_stroke", &ngp::CanvasCore::drawBrushStroke)
        .def("erase_brush_stroke", &ngp::CanvasCore::eraseBrushStroke)
        .def("set_selection", &ngp::CanvasCore::setSelection)
        .def("clear_selection", &ngp::CanvasCore::clearSelection)
        .def("has_selection", &ngp::CanvasCore::hasSelection)
        .def("apply_filter", &ngp::CanvasCore::applyFilter);
    
    // UndoStack class
    py::class_<ngp::UndoStack>(m, "UndoStack")
        .def(py::init<size_t>())
        // .def("push_state", &ngp::UndoStack::pushState)  // Commented out due to unique_ptr issues
        .def("pop_state", &ngp::UndoStack::popState)
        .def("redo_state", &ngp::UndoStack::redoState)
        .def("can_undo", &ngp::UndoStack::canUndo)
        .def("can_redo", &ngp::UndoStack::canRedo)
        .def("get_state_count", &ngp::UndoStack::getStateCount)
        .def("get_current_index", &ngp::UndoStack::getCurrentIndex)
        .def("get_undo_description", &ngp::UndoStack::getUndoDescription)
        .def("get_redo_description", &ngp::UndoStack::getRedoDescription)
        .def("clear", &ngp::UndoStack::clear)
        .def("set_max_states", &ngp::UndoStack::setMaxStates);
} 
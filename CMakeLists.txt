cmake_minimum_required(VERSION 3.28)
project(NextGenPaint VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(pybind11 REQUIRED)
find_package(OpenCV REQUIRED)

# Set OpenCV include directories for MSYS2
if(OpenCV_FOUND)
    include_directories(${OpenCV_INCLUDE_DIRS})
    # Add MSYS2 specific OpenCV include path
    include_directories("C:/msys64/mingw64/include/opencv4")
endif()

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src/cpp)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src/cpp/include)

# Core library
add_library(ngp_core SHARED
    src/cpp/core/tile_engine.cpp
    src/cpp/core/canvas_core.cpp
    src/cpp/core/undo_stack.cpp
)

# Plugins (only include existing ones)
add_library(blur_plugin SHARED src/cpp/plugins/blur.cpp)
add_library(unsharp_plugin SHARED src/cpp/plugins/unsharp.cpp)
add_library(smudge_plugin SHARED src/cpp/plugins/smudge.cpp)
add_library(inpaint_plugin SHARED src/cpp/plugins/inpaint.cpp)

# Link libraries
target_link_libraries(ngp_core ${OpenCV_LIBS})
target_link_libraries(blur_plugin ngp_core)
target_link_libraries(unsharp_plugin ngp_core)
target_link_libraries(smudge_plugin ngp_core)
target_link_libraries(inpaint_plugin ngp_core)

# Python bindings (only include existing ones)
pybind11_add_module(ngp_core_python src/cpp/bindings/core_bindings.cpp)
# Link libraries using target_link_libraries with PRIVATE keyword
target_link_libraries(ngp_core_python PRIVATE ngp_core ${OpenCV_LIBS})

# Installation
install(TARGETS ngp_core_python
        LIBRARY DESTINATION ${CMAKE_INSTALL_PREFIX}/ngpaint)

# Set output directory for Python modules
set_target_properties(ngp_core_python PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/src/python/ngpaint
) 
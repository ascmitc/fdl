# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
#
# Emscripten / WASM build for the fdl_core JavaScript bindings.
#
# Invoke via emcmake:
#     emcmake cmake -S native/bindings/wasm -B native/bindings/wasm/build \
#         -DCMAKE_BUILD_TYPE=Release
#     cmake --build native/bindings/wasm/build -j
#
# The build produces fdl_module.{js,wasm} which the npm package loads from
# native/bindings/node/wasm/ at runtime (the build_wasm.py script copies the
# artifacts there).
cmake_minimum_required(VERSION 3.20)
project(fdl_wasm LANGUAGES CXX)

if(NOT EMSCRIPTEN)
  message(FATAL_ERROR
    "This CMakeLists.txt must be configured with the Emscripten toolchain.\n"
    "Use `emcmake cmake ...` instead of plain `cmake`.")
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# C++ exceptions must be enabled for BOTH fdl_core and the bindings under
# Emscripten. fdl_core's parser catches jsoncons exceptions internally and
# converts them to result.error strings; without -fexceptions on its compile
# flags those throws unwind into Embind and surface as opaque integer
# pointers instead of FDLValidationError on the JS side.
add_compile_options(-fexceptions)
add_link_options(-fexceptions)

# Force fdl_core to build as STATIC: WASM cannot resolve shared libraries the
# way native dynamic loaders do. We embed the core into the WASM module.
set(FDL_CORE_LIBRARY_TYPE "STATIC" CACHE STRING "" FORCE)

# Build fdl_core in-tree as a subproject so we get a single WASM module with
# everything linked statically.
add_subdirectory(
  ${CMAKE_CURRENT_SOURCE_DIR}/../../core
  ${CMAKE_CURRENT_BINARY_DIR}/fdl_core
  EXCLUDE_FROM_ALL
)

# The Embind bindings module
add_executable(fdl_module
  src/bindings.cpp
)

target_link_libraries(fdl_module PRIVATE fdl_core)

target_include_directories(fdl_module PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/../../core/include
)

# Emscripten link flags. Keep these on the link step only.
# Built/tested with emsdk 3.1.73 (pinned in .github/workflows/main.yml).
set(_FDL_WASM_LINK_FLAGS
  "-lembind"
  "-sMODULARIZE=1"
  "-sEXPORT_ES6=1"
  "-sEXPORT_NAME=createFdlModule"
  "-sENVIRONMENT=web,node"
  "-sALLOW_MEMORY_GROWTH=1"
  "-sINITIAL_MEMORY=33554432"     # 32 MiB starting heap; grows as needed.
  "-sSTACK_SIZE=1048576"          # 1 MiB stack.
  "-sFILESYSTEM=0"                # We don't need the FS shim.
  "-sDISABLE_EXCEPTION_CATCHING=0"
  "-sDYNAMIC_EXECUTION=0"
)
string(REPLACE ";" " " _FDL_WASM_LINK_FLAGS_STR "${_FDL_WASM_LINK_FLAGS}")
set_target_properties(fdl_module PROPERTIES
  LINK_FLAGS "${_FDL_WASM_LINK_FLAGS_STR}"
  SUFFIX ".mjs"
  RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/dist"
)

# fdl_core requires fdl_schema_data.h generated under its own binary dir.
# The subproject `add_subdirectory` above sets that up automatically.

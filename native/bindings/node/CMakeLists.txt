# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
cmake_minimum_required(VERSION 3.20)
project(fdl_addon LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# cmake-js provides these variables
include_directories(${CMAKE_JS_INC})

# Find libfdl_core — check env var, then in-tree build dir
if(DEFINED ENV{FDL_CORE_LIB_DIR})
  set(_SEARCH_PATHS $ENV{FDL_CORE_LIB_DIR})
else()
  set(_SEARCH_PATHS "${CMAKE_CURRENT_SOURCE_DIR}/../../core/build")
endif()

find_library(FDL_CORE_LIB
  NAMES fdl_core
  PATHS ${_SEARCH_PATHS}
  NO_DEFAULT_PATH
)
if(NOT FDL_CORE_LIB)
  # Fall back to system search
  find_library(FDL_CORE_LIB NAMES fdl_core)
endif()

if(NOT FDL_CORE_LIB)
  message(FATAL_ERROR
    "Could not find libfdl_core. Build it first with:\n"
    "  python scripts/build_native.py\n"
    "Or set FDL_CORE_LIB_DIR to the directory containing the library.")
endif()

message(STATUS "Using fdl_core: ${FDL_CORE_LIB}")

# node-addon-api headers
execute_process(
  COMMAND node -p "require('node-addon-api').include"
  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
  OUTPUT_VARIABLE NAPI_INCLUDE
  OUTPUT_STRIP_TRAILING_WHITESPACE
)
# Strip surrounding quotes if present
string(REPLACE "\"" "" NAPI_INCLUDE "${NAPI_INCLUDE}")

# The addon shared library
add_library(fdl_addon SHARED
  src/addon/binding.cc
)

target_include_directories(fdl_addon PRIVATE
  ${CMAKE_JS_INC}
  ${NAPI_INCLUDE}
  ${CMAKE_CURRENT_SOURCE_DIR}/../../core/include
  ${CMAKE_CURRENT_SOURCE_DIR}/../../core/build  # for fdl_export.h
  ${CMAKE_CURRENT_SOURCE_DIR}/src/addon
)

target_link_libraries(fdl_addon
  ${CMAKE_JS_LIB}
  ${FDL_CORE_LIB}
)

# N-API version
target_compile_definitions(fdl_addon PRIVATE NAPI_VERSION=8)

# Output as .node file
set_target_properties(fdl_addon PROPERTIES
  PREFIX ""
  SUFFIX ".node"
  LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/build"
)

# macOS: set rpath so the addon can find libfdl_core next to it or in standard paths
if(APPLE)
  set_target_properties(fdl_addon PROPERTIES
    INSTALL_RPATH "@loader_path;@loader_path/../../../core/build"
    BUILD_WITH_INSTALL_RPATH TRUE
  )
elseif(UNIX)
  set_target_properties(fdl_addon PROPERTIES
    INSTALL_RPATH "$ORIGIN;$ORIGIN/../../../core/build"
    BUILD_WITH_INSTALL_RPATH TRUE
  )
endif()

# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
cmake_minimum_required(VERSION 3.20)

include(cmake/FDLVersion.cmake)

project(fdl_core
  VERSION ${FDL_CORE_VERSION}
  LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Platform-specific symbol visibility
set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_VISIBILITY_INLINES_HIDDEN ON)

# Export macros
include(GenerateExportHeader)

# jsoncons — PRIVATE dependency (not exposed in C ABI)
# Provides ordered JSON (ojson) and Draft 2020-12 schema validation
include(FetchContent)
FetchContent_Declare(
  jsoncons
  GIT_REPOSITORY https://github.com/danielaparker/jsoncons.git
  GIT_TAG v1.5.0
  GIT_SHALLOW TRUE
)
# Disable jsoncons' own tests/examples
set(JSONCONS_BUILD_TESTS OFF CACHE BOOL "" FORCE)
# Use manual populate + EXCLUDE_FROM_ALL to prevent jsoncons install rules
# from polluting our install tree
FetchContent_GetProperties(jsoncons)
if(NOT jsoncons_POPULATED)
  FetchContent_Populate(jsoncons)
  add_subdirectory(${jsoncons_SOURCE_DIR} ${jsoncons_BINARY_DIR} EXCLUDE_FROM_ALL)
endif()

# Generate schema header from FDL schema files (embeds at compile time)
set(FDL_SCHEMA_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../schema")
set(FDL_SCHEMA_OUT "${CMAKE_CURRENT_BINARY_DIR}/fdl_schema_data.h")
execute_process(
  COMMAND ${CMAKE_COMMAND}
    -DFDL_SCHEMA_DIR=${FDL_SCHEMA_DIR}
    -DFDL_SCHEMA_OUT=${FDL_SCHEMA_OUT}
    -P ${CMAKE_CURRENT_SOURCE_DIR}/cmake/GenerateSchemaHeader.cmake
)

# Core shared library
add_library(fdl_core SHARED
  src/fdl_abi.cpp
  src/fdl_handles.cpp
  src/fdl_rounding.cpp
  src/fdl_value_types.cpp
  src/fdl_canonical.cpp
  src/fdl_doc.cpp
  src/fdl_doc_api.cpp
  src/fdl_validate.cpp
  src/fdl_validate_api.cpp
  src/fdl_geometry.cpp
  src/fdl_geometry_api.cpp
  src/fdl_pipeline.cpp
  src/fdl_pipeline_api.cpp
  src/fdl_collections_api.cpp
  src/fdl_accessors_api.cpp
  src/fdl_builder.cpp
  src/fdl_builder_api.cpp
  src/fdl_framing.cpp
  src/fdl_framing_api.cpp
  src/fdl_template.cpp
  src/fdl_template_api.cpp
  src/fdl_custom_attr.cpp
  src/fdl_custom_attr_api.cpp
)

target_include_directories(fdl_core
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>
    $<INSTALL_INTERFACE:include>
  PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

generate_export_header(fdl_core
  EXPORT_FILE_NAME ${CMAKE_CURRENT_BINARY_DIR}/fdl_export.h
  EXPORT_MACRO_NAME FDL_API
)

target_link_libraries(fdl_core PRIVATE jsoncons)

target_compile_definitions(fdl_core PRIVATE fdl_core_EXPORTS)

# Platform-specific compiler settings
if(MSVC)
  target_compile_definitions(fdl_core PRIVATE
    _CRT_SECURE_NO_WARNINGS
    NOMINMAX
  )
  target_compile_options(fdl_core PRIVATE /W4 /wd4251)
else()
  target_compile_options(fdl_core PRIVATE -Wall -Wextra -Wpedantic)
endif()

# Pass ABI version to source
target_compile_definitions(fdl_core PRIVATE
  FDL_ABI_VERSION_MAJOR=${FDL_ABI_VERSION_MAJOR}
  FDL_ABI_VERSION_MINOR=${FDL_ABI_VERSION_MINOR}
  FDL_ABI_VERSION_PATCH=${FDL_ABI_VERSION_PATCH}
)

# Platform-specific rpath for shared library loading
if(APPLE)
  set_target_properties(fdl_core PROPERTIES
    INSTALL_RPATH "@loader_path"
    BUILD_WITH_INSTALL_RPATH ON
  )
elseif(UNIX)
  set_target_properties(fdl_core PROPERTIES
    INSTALL_RPATH "$ORIGIN"
    BUILD_WITH_INSTALL_RPATH ON
  )
endif()

# Library version / ABI version
set_target_properties(fdl_core PROPERTIES
  VERSION   ${PROJECT_VERSION}
  SOVERSION ${FDL_ABI_VERSION_MAJOR}
)

# Header-only C++ RAII facade — depends on fdl_core
add_library(fdl_hpp INTERFACE)
target_include_directories(fdl_hpp INTERFACE
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../bindings/cpp>
  $<INSTALL_INTERFACE:include>
)
target_link_libraries(fdl_hpp INTERFACE fdl_core)
target_compile_features(fdl_hpp INTERFACE cxx_std_17)

# Namespace aliases for add_subdirectory / FetchContent consumers
add_library(FDL::fdl_core ALIAS fdl_core)
add_library(FDL::fdl_hpp  ALIAS fdl_hpp)

# Installation
include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

install(TARGETS fdl_core fdl_hpp
  EXPORT FDLTargets
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(FILES
  ${CMAKE_CURRENT_SOURCE_DIR}/include/fdl/fdl_core.h
  ${CMAKE_CURRENT_BINARY_DIR}/fdl_export.h
  ${CMAKE_CURRENT_SOURCE_DIR}/../bindings/cpp/fdl/fdl.hpp
  DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/fdl
)

install(EXPORT FDLTargets
  FILE        FDLTargets.cmake
  NAMESPACE   FDL::
  DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/FDL
)

write_basic_package_version_file(
  "${CMAKE_CURRENT_BINARY_DIR}/FDLConfigVersion.cmake"
  VERSION ${PROJECT_VERSION}
  COMPATIBILITY SameMinorVersion
)

configure_package_config_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/cmake/FDLConfig.cmake.in"
  "${CMAKE_CURRENT_BINARY_DIR}/FDLConfig.cmake"
  INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/FDL
)

install(FILES
  "${CMAKE_CURRENT_BINARY_DIR}/FDLConfig.cmake"
  "${CMAKE_CURRENT_BINARY_DIR}/FDLConfigVersion.cmake"
  DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/FDL
)

# Documentation (optional, requires Doxygen)
find_package(Doxygen QUIET)
if(DOXYGEN_FOUND)
  add_custom_target(docs
    COMMAND ${DOXYGEN_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/Doxyfile
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Generating API documentation with Doxygen"
    VERBATIM
  )
endif()

# Tests (optional, gated by BUILD_TESTING)
option(FDL_BUILD_TESTS "Build fdl_core tests" ON)
if(FDL_BUILD_TESTS)
  enable_testing()
  add_subdirectory(tests)
endif()

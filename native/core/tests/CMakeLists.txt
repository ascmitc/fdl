# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
include(FetchContent)

FetchContent_Declare(
  Catch2
  GIT_REPOSITORY https://github.com/catchorg/Catch2.git
  GIT_TAG v3.5.2
  GIT_SHALLOW TRUE
)

FetchContent_MakeAvailable(Catch2)

# Copy test vectors to build directory
file(COPY vectors DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

find_package(Threads REQUIRED)

add_executable(fdl_core_tests
  test_abi_version.cpp
  test_rounding.cpp
  test_value_types.cpp
  test_doc_lifecycle.cpp
  test_roundtrip.cpp
  test_validation.cpp
  test_schema_validation.cpp
  test_geometry.cpp
  test_pipeline.cpp
  test_accessors.cpp
  test_builder.cpp
  test_framing.cpp
  test_template.cpp
  test_raii_facade.cpp
  test_custom_attr.cpp
  test_thread_safety.cpp
  test_resolve_canvas.cpp
)

target_link_libraries(fdl_core_tests PRIVATE
  fdl_core
  jsoncons
  Catch2::Catch2WithMain
  Threads::Threads
)

# Include path for C++ RAII header (fdl.hpp)
target_include_directories(fdl_core_tests PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/../../bindings/cpp
)

target_compile_definitions(fdl_core_tests PRIVATE
  VECTORS_DIR="${CMAKE_CURRENT_BINARY_DIR}/vectors"
)

if(MSVC)
  target_compile_definitions(fdl_core_tests PRIVATE
    _CRT_SECURE_NO_WARNINGS
    NOMINMAX
  )
endif()

include(Catch)

# On Windows, ensure fdl_core.dll is findable when Catch2 runs the test exe
# for test discovery. DL_PATHS tells catch_discover_tests where to find DLLs.
catch_discover_tests(fdl_core_tests
  DL_PATHS $<TARGET_FILE_DIR:fdl_core>
)

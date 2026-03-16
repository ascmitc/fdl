// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_validate_api.cpp
 * @brief C ABI wrappers for document validation.
 */
#include "fdl/fdl_core.h"
#include "fdl_doc.h"
#include "fdl_validate.h"

#include <new>

/** @brief Concrete type backing the opaque fdl_validation_result_t handle. */
struct fdl_validation_result {
    fdl::detail::ValidationResult result; /**< Wrapped validation result. */
};

extern "C" {

fdl_validation_result_t* fdl_doc_validate(const fdl_doc_t* doc) {
    if (doc == nullptr) {
        auto* r = new (std::nothrow) fdl_validation_result{};
        return r;
    }
    const doc_lock lock(doc);
    auto vr = fdl::detail::validate(doc->doc.data());
    auto* r = new (std::nothrow) fdl_validation_result{std::move(vr)};
    return r;
}

uint32_t fdl_validation_result_error_count(const fdl_validation_result_t* result) {
    if (result == nullptr) {
        return 0;
    }
    return static_cast<uint32_t>(result->result.errors.size());
}

const char* fdl_validation_result_error_at(const fdl_validation_result_t* result, uint32_t index) {
    if (result == nullptr || index >= result->result.errors.size()) {
        return nullptr;
    }
    return result->result.errors[index].c_str();
}

void fdl_validation_result_free(fdl_validation_result_t* result) {
    delete result;
}

} // extern "C"

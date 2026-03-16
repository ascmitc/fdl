// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_template_api.cpp
 * @brief C ABI wrapper for canvas template application and result management.
 */
#include "fdl/fdl_core.h"
#include "fdl_template.h"

#include <cstdlib>

namespace {

/**
 * @brief Free a heap-allocated string owned through a const char* field.
 *
 * The @c fdl_template_result_t struct exposes @c const @c char* fields for
 * read safety at call sites, but the strings are heap-allocated by
 * fdl_strdup() and ownership transfers to the caller. This helper
 * encapsulates the necessary const_cast for freeing such strings.
 *
 * @param s  Reference to the const char* field to free and null out.
 */
void free_owned_string(const char*& s) {
    if (s != nullptr) {
        free(const_cast<char*>(s)); // NOLINT(cppcoreguidelines-no-malloc,cppcoreguidelines-pro-type-const-cast)
        s = nullptr;
    }
}

} // namespace

extern "C" {

fdl_template_result_t fdl_apply_canvas_template(
    const fdl_canvas_template_t* tmpl,
    const fdl_canvas_t* source_canvas,
    const fdl_framing_decision_t* source_framing,
    const char* new_canvas_id,
    const char* new_fd_name,
    const char* source_context_label,
    const char* context_creator) {
    return fdl::detail::apply_canvas_template(
        tmpl, source_canvas, source_framing, new_canvas_id, new_fd_name, source_context_label, context_creator);
}

void fdl_template_result_free(fdl_template_result_t* result) {
    if (result == nullptr) {
        return;
    }
    if (result->output_fdl != nullptr) {
        fdl_doc_free(result->output_fdl);
        result->output_fdl = nullptr;
    }
    free_owned_string(result->context_label);
    free_owned_string(result->canvas_id);
    free_owned_string(result->framing_decision_id);
    free_owned_string(result->error);
}

} // extern "C"

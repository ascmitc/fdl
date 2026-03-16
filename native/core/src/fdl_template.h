// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_template.h
 * @brief Internal implementation of canvas template application.
 *
 * Runs the full template pipeline: resolve geometry layers, normalize+scale,
 * round, offset, crop, and produce the output FDL document.
 */
#ifndef FDL_TEMPLATE_INTERNAL_H
#define FDL_TEMPLATE_INTERNAL_H

#include "fdl/fdl_core.h"

namespace fdl::detail {

/**
 * @brief Apply a canvas template to a source canvas/framing.
 *
 * Internal implementation — see fdl_apply_canvas_template() for full docs.
 *
 * @param tmpl                  Canvas template handle.
 * @param source_canvas         Source canvas handle.
 * @param source_framing        Source framing decision handle.
 * @param new_canvas_id         ID for the output canvas.
 * @param new_fd_name           Name for the output framing decision.
 * @param source_context_label  Label from source context (may be NULL).
 * @param context_creator       Creator string for the output context.
 * @return Template result with output_fdl on success, error on failure.
 */
fdl_template_result_t apply_canvas_template(
    const fdl_canvas_template_t* tmpl,
    const fdl_canvas_t* source_canvas,
    const fdl_framing_decision_t* source_framing,
    const char* new_canvas_id,
    const char* new_fd_name,
    const char* source_context_label,
    const char* context_creator);

} // namespace fdl::detail

#endif // FDL_TEMPLATE_INTERNAL_H

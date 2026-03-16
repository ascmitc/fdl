// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_framing_api.cpp
 * @brief C ABI wrapper for framing-from-intent computation and related handle-based operations.
 */
#include "fdl/fdl_core.h"
#include "fdl_builder.h"
#include "fdl_constants.h"
#include "fdl_doc.h"
#include "fdl_framing.h"

namespace {

/**
 * @brief Compute alignment offset for a single axis.
 * @param container  Size of the containing dimension.
 * @param content    Size of the content to align.
 * @param align      Alignment enum value (0=left/top, 1=center, 2=right/bottom).
 * @return Pixel offset to apply for the requested alignment.
 */
double align_offset(double container, double content, uint32_t align) {
    // CENTER enum value is 1 for both halign and valign
    if (align == FDL_HALIGN_CENTER) {
        return (container - content) / fdl::constants::kCenterDivisor;
    }
    // RIGHT (halign=2) or BOTTOM (valign=2)
    if (align == FDL_HALIGN_RIGHT) {
        return container - content;
    }
    // LEFT (halign=0) or TOP (valign=0)
    return 0.0;
}

} // namespace

extern "C" {

fdl_from_intent_result_t fdl_compute_framing_from_intent(
    fdl_dimensions_f64_t canvas_dims,
    fdl_dimensions_f64_t working_dims,
    double squeeze,
    fdl_dimensions_i64_t aspect_ratio,
    double protection,
    fdl_round_strategy_t rounding) {
    return fdl::detail::compute_framing_from_intent(
        canvas_dims, working_dims, squeeze, aspect_ratio, protection, rounding);
}

void fdl_framing_decision_adjust_anchor(
    fdl_framing_decision_t* fd, const fdl_canvas_t* canvas, fdl_halign_t h_align, fdl_valign_t v_align) {
    if (fd == nullptr || canvas == nullptr) {
        return;
    }

    const doc_lock lock(fd->owner);
    auto* fd_n = fd->node();
    auto* canvas_n = canvas->node();
    if (fd_n == nullptr || canvas_n == nullptr) {
        return;
    }

    double const canvas_w = static_cast<double>((*canvas_n)["dimensions"]["width"].as<int64_t>());
    double const canvas_h = static_cast<double>((*canvas_n)["dimensions"]["height"].as<int64_t>());
    double const fd_w = (*fd_n)["dimensions"]["width"].as<double>();
    double const fd_h = (*fd_n)["dimensions"]["height"].as<double>();

    double const anchor_x = align_offset(canvas_w, fd_w, h_align);
    double const anchor_y = align_offset(canvas_h, fd_h, v_align);

    fd_n->insert_or_assign("anchor_point", fdl::detail::make_point_float(anchor_x, anchor_y));
}

void fdl_framing_decision_adjust_protection_anchor(
    fdl_framing_decision_t* fd, const fdl_canvas_t* canvas, fdl_halign_t h_align, fdl_valign_t v_align) {
    if (fd == nullptr || canvas == nullptr) {
        return;
    }

    const doc_lock lock(fd->owner);
    auto* fd_n = fd->node();
    auto* canvas_n = canvas->node();
    if (fd_n == nullptr || canvas_n == nullptr) {
        return;
    }

    double const canvas_w = static_cast<double>((*canvas_n)["dimensions"]["width"].as<int64_t>());
    double const canvas_h = static_cast<double>((*canvas_n)["dimensions"]["height"].as<int64_t>());
    double const prot_w = (*fd_n)["protection_dimensions"]["width"].as<double>();
    double const prot_h = (*fd_n)["protection_dimensions"]["height"].as<double>();

    double const anchor_x = align_offset(canvas_w, prot_w, h_align);
    double const anchor_y = align_offset(canvas_h, prot_h, v_align);

    fd_n->insert_or_assign("protection_anchor_point", fdl::detail::make_point_float(anchor_x, anchor_y));
}

void fdl_framing_decision_populate_from_intent(
    fdl_framing_decision_t* fd,
    const fdl_canvas_t* canvas,
    const fdl_framing_intent_t* intent,
    fdl_round_strategy_t rounding) {
    if (fd == nullptr || canvas == nullptr || intent == nullptr) {
        return;
    }

    const doc_lock lock(fd->owner);
    auto* fd_n = fd->node();
    auto* canvas_n = canvas->node();
    auto* intent_n = intent->node();
    if (fd_n == nullptr || canvas_n == nullptr || intent_n == nullptr) {
        return;
    }

    // Get canvas dimensions (int -> double)
    fdl_dimensions_f64_t const canvas_dims = {
        static_cast<double>((*canvas_n)["dimensions"]["width"].as<int64_t>()),
        static_cast<double>((*canvas_n)["dimensions"]["height"].as<int64_t>())};

    // Working dims: effective if available, else canvas
    fdl_dimensions_f64_t working_dims = canvas_dims;
    if (canvas_n->contains("effective_dimensions")) {
        working_dims.width = static_cast<double>((*canvas_n)["effective_dimensions"]["width"].as<int64_t>());
        working_dims.height = static_cast<double>((*canvas_n)["effective_dimensions"]["height"].as<int64_t>());
    }

    // Get squeeze
    double const squeeze = canvas_n->contains("anamorphic_squeeze") ? (*canvas_n)["anamorphic_squeeze"].as<double>()
                                                                    : fdl::constants::kIdentitySqueeze;

    // Get aspect ratio from intent
    fdl_dimensions_i64_t const aspect_ratio = {
        (*intent_n)["aspect_ratio"]["width"].as<int64_t>(), (*intent_n)["aspect_ratio"]["height"].as<int64_t>()};

    // Get protection from intent
    double const protection = intent_n->contains("protection") ? (*intent_n)["protection"].as<double>() : 0.0;

    // Compute
    fdl_from_intent_result_t const result = fdl::detail::compute_framing_from_intent(
        canvas_dims, working_dims, squeeze, aspect_ratio, protection, rounding);

    // Write to FD
    fd_n->insert_or_assign(
        "dimensions", fdl::detail::make_dimensions_float(result.dimensions.width, result.dimensions.height));
    fd_n->insert_or_assign("anchor_point", fdl::detail::make_point_float(result.anchor_point.x, result.anchor_point.y));

    if (result.has_protection != 0) {
        fd_n->insert_or_assign(
            "protection_dimensions",
            fdl::detail::make_dimensions_float(
                result.protection_dimensions.width, result.protection_dimensions.height));
        fd_n->insert_or_assign(
            "protection_anchor_point",
            fdl::detail::make_point_float(result.protection_anchor_point.x, result.protection_anchor_point.y));
    }
}

} // extern "C"

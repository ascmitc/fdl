# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
# AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
"""FDL Core ctypes function signatures."""

from __future__ import annotations

import ctypes

from ._structs import (
    fdl_abi_version_t,
    fdl_dimensions_f64_t,
    fdl_dimensions_i64_t,
    fdl_from_intent_result_t,
    fdl_geometry_t,
    fdl_parse_result_t,
    fdl_point_f64_t,
    fdl_rect_t,
    fdl_resolve_canvas_result_t,
    fdl_round_strategy_t,
    fdl_template_result_t,
)


def bind_functions(lib: ctypes.CDLL) -> None:
    """Set argtypes and restype for all fdl_core functions."""

    # Return the ABI version of the loaded library.
    lib.fdl_abi_version.argtypes = []
    lib.fdl_abi_version.restype = fdl_abi_version_t

    # Calculate content translation shift for a single axis.
    lib.fdl_alignment_shift.argtypes = [
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_int,
        ctypes.c_double,
        ctypes.c_int,
    ]
    lib.fdl_alignment_shift.restype = ctypes.c_double

    # Apply a canvas template to a source canvas/framing. Returns template_result_t. Caller must free with fdl_template_result_free.
    lib.fdl_apply_canvas_template.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
    ]
    lib.fdl_apply_canvas_template.restype = fdl_template_result_t

    # Calculate scale factor based on fit method.
    lib.fdl_calculate_scale_factor.argtypes = [fdl_dimensions_f64_t, fdl_dimensions_f64_t, ctypes.c_uint32]
    lib.fdl_calculate_scale_factor.restype = ctypes.c_double

    # Add a framing decision to a canvas. Returns handle (owned by doc).
    lib.fdl_canvas_add_framing_decision.argtypes = [
        ctypes.c_void_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
    ]
    lib.fdl_canvas_add_framing_decision.restype = ctypes.c_void_p

    #
    lib.fdl_canvas_find_framing_decision_by_id.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_canvas_find_framing_decision_by_id.restype = ctypes.c_void_p

    #
    lib.fdl_canvas_framing_decision_at.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    lib.fdl_canvas_framing_decision_at.restype = ctypes.c_void_p

    #
    lib.fdl_canvas_framing_decisions_count.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_framing_decisions_count.restype = ctypes.c_uint32

    #
    lib.fdl_canvas_get_anamorphic_squeeze.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_get_anamorphic_squeeze.restype = ctypes.c_double

    #
    lib.fdl_canvas_get_dimensions.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_get_dimensions.restype = fdl_dimensions_i64_t

    #
    lib.fdl_canvas_get_effective_anchor_point.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_get_effective_anchor_point.restype = fdl_point_f64_t

    #
    lib.fdl_canvas_get_effective_dimensions.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_get_effective_dimensions.restype = fdl_dimensions_i64_t

    # Get effective rect. Returns 0 if absent, 1 if written to out_rect.
    lib.fdl_canvas_get_effective_rect.argtypes = [ctypes.c_void_p, ctypes.POINTER(fdl_rect_t)]
    lib.fdl_canvas_get_effective_rect.restype = ctypes.c_int

    #
    lib.fdl_canvas_get_id.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_get_id.restype = ctypes.c_char_p

    #
    lib.fdl_canvas_get_label.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_get_label.restype = ctypes.c_char_p

    #
    lib.fdl_canvas_get_photosite_dimensions.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_get_photosite_dimensions.restype = fdl_dimensions_i64_t

    #
    lib.fdl_canvas_get_physical_dimensions.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_get_physical_dimensions.restype = fdl_dimensions_f64_t

    # Get canvas rect as (0, 0, width, height).
    lib.fdl_canvas_get_rect.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_get_rect.restype = fdl_rect_t

    #
    lib.fdl_canvas_get_source_canvas_id.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_get_source_canvas_id.restype = ctypes.c_char_p

    #
    lib.fdl_canvas_has_effective_dimensions.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_has_effective_dimensions.restype = ctypes.c_int

    #
    lib.fdl_canvas_has_photosite_dimensions.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_has_photosite_dimensions.restype = ctypes.c_int

    #
    lib.fdl_canvas_has_physical_dimensions.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_has_physical_dimensions.restype = ctypes.c_int

    #
    lib.fdl_canvas_remove_effective.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_remove_effective.restype = None

    #
    lib.fdl_canvas_set_anamorphic_squeeze.argtypes = [ctypes.c_void_p, ctypes.c_double]
    lib.fdl_canvas_set_anamorphic_squeeze.restype = None

    #
    lib.fdl_canvas_set_dimensions.argtypes = [ctypes.c_void_p, fdl_dimensions_i64_t]
    lib.fdl_canvas_set_dimensions.restype = None

    # Set effective dimensions and anchor on a canvas.
    lib.fdl_canvas_set_effective_dimensions.argtypes = [ctypes.c_void_p, fdl_dimensions_i64_t, fdl_point_f64_t]
    lib.fdl_canvas_set_effective_dimensions.restype = None

    #
    lib.fdl_canvas_set_effective_dims_only.argtypes = [ctypes.c_void_p, fdl_dimensions_i64_t]
    lib.fdl_canvas_set_effective_dims_only.restype = None

    #
    lib.fdl_canvas_set_photosite_dimensions.argtypes = [ctypes.c_void_p, fdl_dimensions_i64_t]
    lib.fdl_canvas_set_photosite_dimensions.restype = None

    #
    lib.fdl_canvas_set_physical_dimensions.argtypes = [ctypes.c_void_p, fdl_dimensions_f64_t]
    lib.fdl_canvas_set_physical_dimensions.restype = None

    #
    lib.fdl_canvas_template_get_alignment_method_horizontal.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_get_alignment_method_horizontal.restype = ctypes.c_uint32

    #
    lib.fdl_canvas_template_get_alignment_method_vertical.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_get_alignment_method_vertical.restype = ctypes.c_uint32

    #
    lib.fdl_canvas_template_get_fit_method.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_get_fit_method.restype = ctypes.c_uint32

    #
    lib.fdl_canvas_template_get_fit_source.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_get_fit_source.restype = ctypes.c_uint32

    #
    lib.fdl_canvas_template_get_id.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_get_id.restype = ctypes.c_char_p

    #
    lib.fdl_canvas_template_get_label.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_get_label.restype = ctypes.c_char_p

    #
    lib.fdl_canvas_template_get_maximum_dimensions.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_get_maximum_dimensions.restype = fdl_dimensions_i64_t

    # Get pad_to_maximum flag. Returns 1 if true, 0 if false.
    lib.fdl_canvas_template_get_pad_to_maximum.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_get_pad_to_maximum.restype = ctypes.c_int

    #
    lib.fdl_canvas_template_get_preserve_from_source_canvas.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_get_preserve_from_source_canvas.restype = ctypes.c_uint32

    #
    lib.fdl_canvas_template_get_round.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_get_round.restype = fdl_round_strategy_t

    #
    lib.fdl_canvas_template_get_target_anamorphic_squeeze.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_get_target_anamorphic_squeeze.restype = ctypes.c_double

    #
    lib.fdl_canvas_template_get_target_dimensions.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_get_target_dimensions.restype = fdl_dimensions_i64_t

    #
    lib.fdl_canvas_template_has_maximum_dimensions.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_has_maximum_dimensions.restype = ctypes.c_int

    #
    lib.fdl_canvas_template_has_preserve_from_source_canvas.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_has_preserve_from_source_canvas.restype = ctypes.c_int

    #
    lib.fdl_canvas_template_set_maximum_dimensions.argtypes = [ctypes.c_void_p, fdl_dimensions_i64_t]
    lib.fdl_canvas_template_set_maximum_dimensions.restype = None

    # Set pad_to_maximum on a canvas template.
    lib.fdl_canvas_template_set_pad_to_maximum.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.fdl_canvas_template_set_pad_to_maximum.restype = None

    #
    lib.fdl_canvas_template_set_preserve_from_source_canvas.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    lib.fdl_canvas_template_set_preserve_from_source_canvas.restype = None

    # Serialize canvas template to canonical JSON string. Caller owns (free with fdl_free).
    lib.fdl_canvas_template_to_json.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.fdl_canvas_template_to_json.restype = ctypes.c_void_p

    # Serialize canvas sub-object to canonical JSON string. Caller owns (free with fdl_free).
    lib.fdl_canvas_to_json.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.fdl_canvas_to_json.restype = ctypes.c_void_p

    #
    lib.fdl_clip_id_get_clip_name.argtypes = [ctypes.c_void_p]
    lib.fdl_clip_id_get_clip_name.restype = ctypes.c_char_p

    #
    lib.fdl_clip_id_get_file.argtypes = [ctypes.c_void_p]
    lib.fdl_clip_id_get_file.restype = ctypes.c_char_p

    #
    lib.fdl_clip_id_has_file.argtypes = [ctypes.c_void_p]
    lib.fdl_clip_id_has_file.restype = ctypes.c_int

    #
    lib.fdl_clip_id_has_sequence.argtypes = [ctypes.c_void_p]
    lib.fdl_clip_id_has_sequence.restype = ctypes.c_int

    #
    lib.fdl_clip_id_sequence.argtypes = [ctypes.c_void_p]
    lib.fdl_clip_id_sequence.restype = ctypes.c_void_p

    # Serialize clip_id to canonical JSON. Caller frees with fdl_free.
    lib.fdl_clip_id_to_json.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.fdl_clip_id_to_json.restype = ctypes.c_void_p

    # Validate clip_id JSON for mutual exclusion. Returns NULL if valid.
    lib.fdl_clip_id_validate_json.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
    lib.fdl_clip_id_validate_json.restype = ctypes.c_void_p

    # Compute a framing decision from a framing intent.
    lib.fdl_compute_framing_from_intent.argtypes = [
        fdl_dimensions_f64_t,
        fdl_dimensions_f64_t,
        ctypes.c_double,
        fdl_dimensions_i64_t,
        ctypes.c_double,
        fdl_round_strategy_t,
    ]
    lib.fdl_compute_framing_from_intent.restype = fdl_from_intent_result_t

    # Add a canvas to a context. Returns handle (owned by doc).
    lib.fdl_context_add_canvas.argtypes = [
        ctypes.c_void_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_int64,
        ctypes.c_int64,
        ctypes.c_double,
    ]
    lib.fdl_context_add_canvas.restype = ctypes.c_void_p

    #
    lib.fdl_context_canvas_at.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    lib.fdl_context_canvas_at.restype = ctypes.c_void_p

    #
    lib.fdl_context_canvases_count.argtypes = [ctypes.c_void_p]
    lib.fdl_context_canvases_count.restype = ctypes.c_uint32

    #
    lib.fdl_context_clip_id.argtypes = [ctypes.c_void_p]
    lib.fdl_context_clip_id.restype = ctypes.c_void_p

    #
    lib.fdl_context_find_canvas_by_id.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_context_find_canvas_by_id.restype = ctypes.c_void_p

    # Get clip_id as JSON string. Returns NULL if not present. Caller owns (free with fdl_free).
    lib.fdl_context_get_clip_id.argtypes = [ctypes.c_void_p]
    lib.fdl_context_get_clip_id.restype = ctypes.c_void_p

    #
    lib.fdl_context_get_context_creator.argtypes = [ctypes.c_void_p]
    lib.fdl_context_get_context_creator.restype = ctypes.c_char_p

    #
    lib.fdl_context_get_label.argtypes = [ctypes.c_void_p]
    lib.fdl_context_get_label.restype = ctypes.c_char_p

    #
    lib.fdl_context_has_clip_id.argtypes = [ctypes.c_void_p]
    lib.fdl_context_has_clip_id.restype = ctypes.c_int

    #
    lib.fdl_context_remove_clip_id.argtypes = [ctypes.c_void_p]
    lib.fdl_context_remove_clip_id.restype = None

    # Resolve canvas for given input dimensions. Returns non-owning handles. Caller must free error with fdl_free.
    lib.fdl_context_resolve_canvas_for_dimensions.argtypes = [ctypes.c_void_p, fdl_dimensions_f64_t, ctypes.c_void_p, ctypes.c_void_p]
    lib.fdl_context_resolve_canvas_for_dimensions.restype = fdl_resolve_canvas_result_t

    #
    lib.fdl_context_set_clip_id_json.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]
    lib.fdl_context_set_clip_id_json.restype = ctypes.c_void_p

    # Serialize context sub-object to canonical JSON string. Caller owns (free with fdl_free).
    lib.fdl_context_to_json.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.fdl_context_to_json.restype = ctypes.c_void_p

    # Clamp dimensions to maximum bounds. Delta offset written to out_delta.
    lib.fdl_dimensions_clamp_to_dims.argtypes = [fdl_dimensions_f64_t, fdl_dimensions_f64_t, ctypes.POINTER(fdl_point_f64_t)]
    lib.fdl_dimensions_clamp_to_dims.restype = fdl_dimensions_f64_t

    # Check approximate equality with FDL tolerances.
    lib.fdl_dimensions_equal.argtypes = [fdl_dimensions_f64_t, fdl_dimensions_f64_t]
    lib.fdl_dimensions_equal.restype = ctypes.c_int

    # Greater-than (OR logic) for float64 dimensions.
    lib.fdl_dimensions_f64_gt.argtypes = [fdl_dimensions_f64_t, fdl_dimensions_f64_t]
    lib.fdl_dimensions_f64_gt.restype = ctypes.c_int

    # Less-than (OR logic) for float64 dimensions.
    lib.fdl_dimensions_f64_lt.argtypes = [fdl_dimensions_f64_t, fdl_dimensions_f64_t]
    lib.fdl_dimensions_f64_lt.restype = ctypes.c_int

    # Convert float dimensions to int64 by truncation.
    lib.fdl_dimensions_f64_to_i64.argtypes = [fdl_dimensions_f64_t]
    lib.fdl_dimensions_f64_to_i64.restype = fdl_dimensions_i64_t

    # Greater-than (OR logic) for int64 dimensions.
    lib.fdl_dimensions_i64_gt.argtypes = [fdl_dimensions_i64_t, fdl_dimensions_i64_t]
    lib.fdl_dimensions_i64_gt.restype = ctypes.c_int

    # Check if both width and height are zero (int64 variant).
    lib.fdl_dimensions_i64_is_zero.argtypes = [fdl_dimensions_i64_t]
    lib.fdl_dimensions_i64_is_zero.restype = ctypes.c_int

    # Less-than (OR logic) for int64 dimensions.
    lib.fdl_dimensions_i64_lt.argtypes = [fdl_dimensions_i64_t, fdl_dimensions_i64_t]
    lib.fdl_dimensions_i64_lt.restype = ctypes.c_int

    # Normalize int64 dimensions by applying anamorphic squeeze to width. Returns float dimensions.
    lib.fdl_dimensions_i64_normalize.argtypes = [fdl_dimensions_i64_t, ctypes.c_double]
    lib.fdl_dimensions_i64_normalize.restype = fdl_dimensions_f64_t

    # Check if both width and height are zero.
    lib.fdl_dimensions_is_zero.argtypes = [fdl_dimensions_f64_t]
    lib.fdl_dimensions_is_zero.restype = ctypes.c_int

    # Normalize dimensions by applying anamorphic squeeze to width.
    lib.fdl_dimensions_normalize.argtypes = [fdl_dimensions_f64_t, ctypes.c_double]
    lib.fdl_dimensions_normalize.restype = fdl_dimensions_f64_t

    # Normalize and scale dimensions in one step.
    lib.fdl_dimensions_normalize_and_scale.argtypes = [fdl_dimensions_f64_t, ctypes.c_double, ctypes.c_double, ctypes.c_double]
    lib.fdl_dimensions_normalize_and_scale.restype = fdl_dimensions_f64_t

    # Scale normalized dimensions and apply target squeeze.
    lib.fdl_dimensions_scale.argtypes = [fdl_dimensions_f64_t, ctypes.c_double, ctypes.c_double]
    lib.fdl_dimensions_scale.restype = fdl_dimensions_f64_t

    # Subtract two dimensions.
    lib.fdl_dimensions_sub.argtypes = [fdl_dimensions_f64_t, fdl_dimensions_f64_t]
    lib.fdl_dimensions_sub.restype = fdl_dimensions_f64_t

    # Add a canvas template to the document. Returns handle (owned by doc).
    lib.fdl_doc_add_canvas_template.argtypes = [
        ctypes.c_void_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_int64,
        ctypes.c_int64,
        ctypes.c_double,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_uint32,
        fdl_round_strategy_t,
    ]
    lib.fdl_doc_add_canvas_template.restype = ctypes.c_void_p

    # Add a context to the document. Returns handle (owned by doc).
    lib.fdl_doc_add_context.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
    lib.fdl_doc_add_context.restype = ctypes.c_void_p

    # Add a framing intent to the document. Returns handle (owned by doc).
    lib.fdl_doc_add_framing_intent.argtypes = [
        ctypes.c_void_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_int64,
        ctypes.c_int64,
        ctypes.c_double,
    ]
    lib.fdl_doc_add_framing_intent.restype = ctypes.c_void_p

    #
    lib.fdl_doc_canvas_template_at.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    lib.fdl_doc_canvas_template_at.restype = ctypes.c_void_p

    #
    lib.fdl_doc_canvas_template_find_by_id.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_doc_canvas_template_find_by_id.restype = ctypes.c_void_p

    #
    lib.fdl_doc_canvas_templates_count.argtypes = [ctypes.c_void_p]
    lib.fdl_doc_canvas_templates_count.restype = ctypes.c_uint32

    #
    lib.fdl_doc_context_at.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    lib.fdl_doc_context_at.restype = ctypes.c_void_p

    #
    lib.fdl_doc_context_find_by_label.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_doc_context_find_by_label.restype = ctypes.c_void_p

    #
    lib.fdl_doc_contexts_count.argtypes = [ctypes.c_void_p]
    lib.fdl_doc_contexts_count.restype = ctypes.c_uint32

    # Create an empty FDL document. Returns NULL on allocation failure.
    lib.fdl_doc_create.argtypes = []
    lib.fdl_doc_create.restype = ctypes.c_void_p

    # Create a new FDL document with header fields and empty collections.
    lib.fdl_doc_create_with_header.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p]
    lib.fdl_doc_create_with_header.restype = ctypes.c_void_p

    #
    lib.fdl_doc_framing_intent_at.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    lib.fdl_doc_framing_intent_at.restype = ctypes.c_void_p

    #
    lib.fdl_doc_framing_intent_find_by_id.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_doc_framing_intent_find_by_id.restype = ctypes.c_void_p

    #
    lib.fdl_doc_framing_intents_count.argtypes = [ctypes.c_void_p]
    lib.fdl_doc_framing_intents_count.restype = ctypes.c_uint32

    # Free an FDL document. Safe to call with NULL.
    lib.fdl_doc_free.argtypes = [ctypes.c_void_p]
    lib.fdl_doc_free.restype = None

    #
    lib.fdl_doc_get_default_framing_intent.argtypes = [ctypes.c_void_p]
    lib.fdl_doc_get_default_framing_intent.restype = ctypes.c_char_p

    #
    lib.fdl_doc_get_fdl_creator.argtypes = [ctypes.c_void_p]
    lib.fdl_doc_get_fdl_creator.restype = ctypes.c_char_p

    #
    lib.fdl_doc_get_uuid.argtypes = [ctypes.c_void_p]
    lib.fdl_doc_get_uuid.restype = ctypes.c_char_p

    #
    lib.fdl_doc_get_version_major.argtypes = [ctypes.c_void_p]
    lib.fdl_doc_get_version_major.restype = ctypes.c_int

    #
    lib.fdl_doc_get_version_minor.argtypes = [ctypes.c_void_p]
    lib.fdl_doc_get_version_minor.restype = ctypes.c_int

    # Parse a JSON string into an FDL document. On success result.doc is non-NULL. On failure result.error is non-NULL (free with fdl_free).
    lib.fdl_doc_parse_json.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
    lib.fdl_doc_parse_json.restype = fdl_parse_result_t

    #
    lib.fdl_doc_set_default_framing_intent.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_doc_set_default_framing_intent.restype = None

    #
    lib.fdl_doc_set_fdl_creator.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_doc_set_fdl_creator.restype = None

    #
    lib.fdl_doc_set_uuid.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_doc_set_uuid.restype = None

    # Set the FDL version.
    lib.fdl_doc_set_version.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    lib.fdl_doc_set_version.restype = None

    # Serialize document to canonical JSON string. Caller owns the returned string (free with fdl_free).
    lib.fdl_doc_to_json.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.fdl_doc_to_json.restype = ctypes.c_void_p

    # Run schema (Draft 2020-12) and semantic validators. Returns a result handle.
    lib.fdl_doc_validate.argtypes = [ctypes.c_void_p]
    lib.fdl_doc_validate.restype = ctypes.c_void_p

    #
    lib.fdl_file_sequence_get_idx.argtypes = [ctypes.c_void_p]
    lib.fdl_file_sequence_get_idx.restype = ctypes.c_char_p

    #
    lib.fdl_file_sequence_get_max.argtypes = [ctypes.c_void_p]
    lib.fdl_file_sequence_get_max.restype = ctypes.c_int64

    #
    lib.fdl_file_sequence_get_min.argtypes = [ctypes.c_void_p]
    lib.fdl_file_sequence_get_min.restype = ctypes.c_int64

    #
    lib.fdl_file_sequence_get_value.argtypes = [ctypes.c_void_p]
    lib.fdl_file_sequence_get_value.restype = ctypes.c_char_p

    # Absolute tolerance for floating-point comparison (1e-6).
    lib.fdl_fp_abs_tol.argtypes = []
    lib.fdl_fp_abs_tol.restype = ctypes.c_double

    # Relative tolerance for floating-point comparison (1e-9).
    lib.fdl_fp_rel_tol.argtypes = []
    lib.fdl_fp_rel_tol.restype = ctypes.c_double

    # Adjust anchor_point on a framing decision based on alignment within canvas.
    lib.fdl_framing_decision_adjust_anchor.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32]
    lib.fdl_framing_decision_adjust_anchor.restype = None

    # Adjust protection_anchor_point on a framing decision based on alignment within canvas.
    lib.fdl_framing_decision_adjust_protection_anchor.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32]
    lib.fdl_framing_decision_adjust_protection_anchor.restype = None

    #
    lib.fdl_framing_decision_get_anchor_point.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_decision_get_anchor_point.restype = fdl_point_f64_t

    #
    lib.fdl_framing_decision_get_dimensions.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_decision_get_dimensions.restype = fdl_dimensions_f64_t

    #
    lib.fdl_framing_decision_get_framing_intent_id.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_decision_get_framing_intent_id.restype = ctypes.c_char_p

    #
    lib.fdl_framing_decision_get_id.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_decision_get_id.restype = ctypes.c_char_p

    #
    lib.fdl_framing_decision_get_label.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_decision_get_label.restype = ctypes.c_char_p

    #
    lib.fdl_framing_decision_get_protection_anchor_point.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_decision_get_protection_anchor_point.restype = fdl_point_f64_t

    #
    lib.fdl_framing_decision_get_protection_dimensions.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_decision_get_protection_dimensions.restype = fdl_dimensions_f64_t

    # Get protection rect. Returns 0 if absent, 1 if written to out_rect.
    lib.fdl_framing_decision_get_protection_rect.argtypes = [ctypes.c_void_p, ctypes.POINTER(fdl_rect_t)]
    lib.fdl_framing_decision_get_protection_rect.restype = ctypes.c_int

    # Get framing decision rect as (anchor_x, anchor_y, width, height).
    lib.fdl_framing_decision_get_rect.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_decision_get_rect.restype = fdl_rect_t

    #
    lib.fdl_framing_decision_has_protection.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_decision_has_protection.restype = ctypes.c_int

    # Populate a framing decision from a canvas and framing intent.
    lib.fdl_framing_decision_populate_from_intent.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, fdl_round_strategy_t]
    lib.fdl_framing_decision_populate_from_intent.restype = None

    #
    lib.fdl_framing_decision_remove_protection.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_decision_remove_protection.restype = None

    #
    lib.fdl_framing_decision_set_anchor_point.argtypes = [ctypes.c_void_p, fdl_point_f64_t]
    lib.fdl_framing_decision_set_anchor_point.restype = None

    #
    lib.fdl_framing_decision_set_dimensions.argtypes = [ctypes.c_void_p, fdl_dimensions_f64_t]
    lib.fdl_framing_decision_set_dimensions.restype = None

    # Set protection dimensions and anchor on a framing decision.
    lib.fdl_framing_decision_set_protection.argtypes = [ctypes.c_void_p, fdl_dimensions_f64_t, fdl_point_f64_t]
    lib.fdl_framing_decision_set_protection.restype = None

    #
    lib.fdl_framing_decision_set_protection_anchor_point.argtypes = [ctypes.c_void_p, fdl_point_f64_t]
    lib.fdl_framing_decision_set_protection_anchor_point.restype = None

    #
    lib.fdl_framing_decision_set_protection_dimensions.argtypes = [ctypes.c_void_p, fdl_dimensions_f64_t]
    lib.fdl_framing_decision_set_protection_dimensions.restype = None

    # Serialize framing decision to canonical JSON string. Caller owns (free with fdl_free).
    lib.fdl_framing_decision_to_json.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.fdl_framing_decision_to_json.restype = ctypes.c_void_p

    #
    lib.fdl_framing_intent_get_aspect_ratio.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_intent_get_aspect_ratio.restype = fdl_dimensions_i64_t

    #
    lib.fdl_framing_intent_get_id.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_intent_get_id.restype = ctypes.c_char_p

    #
    lib.fdl_framing_intent_get_label.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_intent_get_label.restype = ctypes.c_char_p

    #
    lib.fdl_framing_intent_get_protection.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_intent_get_protection.restype = ctypes.c_double

    #
    lib.fdl_framing_intent_set_aspect_ratio.argtypes = [ctypes.c_void_p, fdl_dimensions_i64_t]
    lib.fdl_framing_intent_set_aspect_ratio.restype = None

    #
    lib.fdl_framing_intent_set_protection.argtypes = [ctypes.c_void_p, ctypes.c_double]
    lib.fdl_framing_intent_set_protection.restype = None

    # Serialize framing intent to canonical JSON string. Caller owns (free with fdl_free).
    lib.fdl_framing_intent_to_json.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.fdl_framing_intent_to_json.restype = ctypes.c_void_p

    # Free memory allocated by fdl_core functions.
    lib.fdl_free.argtypes = [ctypes.c_void_p]
    lib.fdl_free.restype = None

    # Apply offset to all anchors. Returns clamped geometry. Theoretical anchors written to output pointers.
    lib.fdl_geometry_apply_offset.argtypes = [
        fdl_geometry_t,
        fdl_point_f64_t,
        ctypes.POINTER(fdl_point_f64_t),
        ctypes.POINTER(fdl_point_f64_t),
        ctypes.POINTER(fdl_point_f64_t),
    ]
    lib.fdl_geometry_apply_offset.restype = fdl_geometry_t

    # Crop all dimensions to visible portion within canvas.
    lib.fdl_geometry_crop.argtypes = [fdl_geometry_t, fdl_point_f64_t, fdl_point_f64_t, fdl_point_f64_t]
    lib.fdl_geometry_crop.restype = fdl_geometry_t

    # Fill gaps in the geometry hierarchy by propagating populated dimensions upward.
    lib.fdl_geometry_fill_hierarchy_gaps.argtypes = [fdl_geometry_t, fdl_point_f64_t]
    lib.fdl_geometry_fill_hierarchy_gaps.restype = fdl_geometry_t

    # Extract dimensions and anchor from geometry by path. Returns 0 on success, -1 on invalid path.
    lib.fdl_geometry_get_dims_anchor_from_path.argtypes = [
        ctypes.POINTER(fdl_geometry_t),
        ctypes.c_uint32,
        ctypes.POINTER(fdl_dimensions_f64_t),
        ctypes.POINTER(fdl_point_f64_t),
    ]
    lib.fdl_geometry_get_dims_anchor_from_path.restype = ctypes.c_int

    # Normalize and scale all 7 fields of the geometry.
    lib.fdl_geometry_normalize_and_scale.argtypes = [fdl_geometry_t, ctypes.c_double, ctypes.c_double, ctypes.c_double]
    lib.fdl_geometry_normalize_and_scale.restype = fdl_geometry_t

    # Round all 7 fields of the geometry.
    lib.fdl_geometry_round.argtypes = [fdl_geometry_t, fdl_round_strategy_t]
    lib.fdl_geometry_round.restype = fdl_geometry_t

    # Create a rect from raw coordinates.
    lib.fdl_make_rect.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double]
    lib.fdl_make_rect.restype = fdl_rect_t

    # Determine output canvas size for a single axis.
    lib.fdl_output_size_for_axis.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_int]
    lib.fdl_output_size_for_axis.restype = ctypes.c_double

    # Add two points.
    lib.fdl_point_add.argtypes = [fdl_point_f64_t, fdl_point_f64_t]
    lib.fdl_point_add.restype = fdl_point_f64_t

    # Clamp point values to specified range.
    lib.fdl_point_clamp.argtypes = [fdl_point_f64_t, ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_int]
    lib.fdl_point_clamp.restype = fdl_point_f64_t

    # Check approximate equality with FDL tolerances.
    lib.fdl_point_equal.argtypes = [fdl_point_f64_t, fdl_point_f64_t]
    lib.fdl_point_equal.restype = ctypes.c_int

    # Greater-than (OR logic) for float64 points.
    lib.fdl_point_f64_gt.argtypes = [fdl_point_f64_t, fdl_point_f64_t]
    lib.fdl_point_f64_gt.restype = ctypes.c_int

    # Less-than (OR logic) for float64 points.
    lib.fdl_point_f64_lt.argtypes = [fdl_point_f64_t, fdl_point_f64_t]
    lib.fdl_point_f64_lt.restype = ctypes.c_int

    # Check if both x and y are zero.
    lib.fdl_point_is_zero.argtypes = [fdl_point_f64_t]
    lib.fdl_point_is_zero.restype = ctypes.c_int

    # Multiply point by scalar.
    lib.fdl_point_mul_scalar.argtypes = [fdl_point_f64_t, ctypes.c_double]
    lib.fdl_point_mul_scalar.restype = fdl_point_f64_t

    # Normalize point by applying anamorphic squeeze to x.
    lib.fdl_point_normalize.argtypes = [fdl_point_f64_t, ctypes.c_double]
    lib.fdl_point_normalize.restype = fdl_point_f64_t

    # Normalize and scale a point in one step.
    lib.fdl_point_normalize_and_scale.argtypes = [fdl_point_f64_t, ctypes.c_double, ctypes.c_double, ctypes.c_double]
    lib.fdl_point_normalize_and_scale.restype = fdl_point_f64_t

    # Scale a normalized point and apply target squeeze.
    lib.fdl_point_scale.argtypes = [fdl_point_f64_t, ctypes.c_double, ctypes.c_double]
    lib.fdl_point_scale.restype = fdl_point_f64_t

    # Subtract two points.
    lib.fdl_point_sub.argtypes = [fdl_point_f64_t, fdl_point_f64_t]
    lib.fdl_point_sub.restype = fdl_point_f64_t

    # Resolve dims/anchor from canvas/framing handles by path. Returns 0=success, 1=absent, -1=invalid.
    lib.fdl_resolve_geometry_layer.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.POINTER(fdl_dimensions_f64_t),
        ctypes.POINTER(fdl_point_f64_t),
    ]
    lib.fdl_resolve_geometry_layer.restype = ctypes.c_int

    # Round a single float value according to FDL rounding rules.
    lib.fdl_round.argtypes = [ctypes.c_double, ctypes.c_uint32, ctypes.c_uint32]
    lib.fdl_round.restype = ctypes.c_int64

    # Round both width and height of dimensions.
    lib.fdl_round_dimensions.argtypes = [fdl_dimensions_f64_t, ctypes.c_uint32, ctypes.c_uint32]
    lib.fdl_round_dimensions.restype = fdl_dimensions_f64_t

    # Round both x and y of a point.
    lib.fdl_round_point.argtypes = [fdl_point_f64_t, ctypes.c_uint32, ctypes.c_uint32]
    lib.fdl_round_point.restype = fdl_point_f64_t

    # Free a template result (doc + error string). Safe to call with NULL.
    lib.fdl_template_result_free.argtypes = [ctypes.POINTER(fdl_template_result_t)]
    lib.fdl_template_result_free.restype = None

    # Get a specific error message by index. Returns NULL if index is out of range.
    lib.fdl_validation_result_error_at.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    lib.fdl_validation_result_error_at.restype = ctypes.c_char_p

    # Get the number of validation errors.
    lib.fdl_validation_result_error_count.argtypes = [ctypes.c_void_p]
    lib.fdl_validation_result_error_count.restype = ctypes.c_uint32

    # Free a validation result. Safe to call with NULL.
    lib.fdl_validation_result_free.argtypes = [ctypes.c_void_p]
    lib.fdl_validation_result_free.restype = None

    # Custom attr: set_custom_attr_string on FDL
    lib.fdl_doc_set_custom_attr_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
    lib.fdl_doc_set_custom_attr_string.restype = ctypes.c_int

    # Custom attr: set_custom_attr_int on FDL
    lib.fdl_doc_set_custom_attr_int.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int64]
    lib.fdl_doc_set_custom_attr_int.restype = ctypes.c_int

    # Custom attr: set_custom_attr_float on FDL
    lib.fdl_doc_set_custom_attr_float.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_double]
    lib.fdl_doc_set_custom_attr_float.restype = ctypes.c_int

    # Custom attr: set_custom_attr_bool on FDL
    lib.fdl_doc_set_custom_attr_bool.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
    lib.fdl_doc_set_custom_attr_bool.restype = ctypes.c_int

    # Custom attr: get_custom_attr_string on FDL
    lib.fdl_doc_get_custom_attr_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_doc_get_custom_attr_string.restype = ctypes.c_char_p

    # Custom attr: get_custom_attr_int on FDL
    lib.fdl_doc_get_custom_attr_int.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int64)]
    lib.fdl_doc_get_custom_attr_int.restype = ctypes.c_int

    # Custom attr: get_custom_attr_float on FDL
    lib.fdl_doc_get_custom_attr_float.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_double)]
    lib.fdl_doc_get_custom_attr_float.restype = ctypes.c_int

    # Custom attr: get_custom_attr_bool on FDL
    lib.fdl_doc_get_custom_attr_bool.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
    lib.fdl_doc_get_custom_attr_bool.restype = ctypes.c_int

    # Custom attr: has_custom_attr on FDL
    lib.fdl_doc_has_custom_attr.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_doc_has_custom_attr.restype = ctypes.c_int

    # Custom attr: get_custom_attr_type on FDL
    lib.fdl_doc_get_custom_attr_type.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_doc_get_custom_attr_type.restype = ctypes.c_uint32

    # Custom attr: remove_custom_attr on FDL
    lib.fdl_doc_remove_custom_attr.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_doc_remove_custom_attr.restype = ctypes.c_int

    # Custom attr: custom_attrs_count on FDL
    lib.fdl_doc_custom_attrs_count.argtypes = [ctypes.c_void_p]
    lib.fdl_doc_custom_attrs_count.restype = ctypes.c_uint32

    # Custom attr: custom_attr_name_at on FDL
    lib.fdl_doc_custom_attr_name_at.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    lib.fdl_doc_custom_attr_name_at.restype = ctypes.c_char_p

    # Custom attr: set_custom_attr_point_f64 on FDL
    lib.fdl_doc_set_custom_attr_point_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, fdl_point_f64_t]
    lib.fdl_doc_set_custom_attr_point_f64.restype = ctypes.c_int

    # Custom attr: get_custom_attr_point_f64 on FDL
    lib.fdl_doc_get_custom_attr_point_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_point_f64_t)]
    lib.fdl_doc_get_custom_attr_point_f64.restype = ctypes.c_int

    # Custom attr: set_custom_attr_dims_f64 on FDL
    lib.fdl_doc_set_custom_attr_dims_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, fdl_dimensions_f64_t]
    lib.fdl_doc_set_custom_attr_dims_f64.restype = ctypes.c_int

    # Custom attr: get_custom_attr_dims_f64 on FDL
    lib.fdl_doc_get_custom_attr_dims_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_dimensions_f64_t)]
    lib.fdl_doc_get_custom_attr_dims_f64.restype = ctypes.c_int

    # Custom attr: set_custom_attr_dims_i64 on FDL
    lib.fdl_doc_set_custom_attr_dims_i64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, fdl_dimensions_i64_t]
    lib.fdl_doc_set_custom_attr_dims_i64.restype = ctypes.c_int

    # Custom attr: get_custom_attr_dims_i64 on FDL
    lib.fdl_doc_get_custom_attr_dims_i64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_dimensions_i64_t)]
    lib.fdl_doc_get_custom_attr_dims_i64.restype = ctypes.c_int

    # Custom attr: set_custom_attr_string on Context
    lib.fdl_context_set_custom_attr_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
    lib.fdl_context_set_custom_attr_string.restype = ctypes.c_int

    # Custom attr: set_custom_attr_int on Context
    lib.fdl_context_set_custom_attr_int.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int64]
    lib.fdl_context_set_custom_attr_int.restype = ctypes.c_int

    # Custom attr: set_custom_attr_float on Context
    lib.fdl_context_set_custom_attr_float.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_double]
    lib.fdl_context_set_custom_attr_float.restype = ctypes.c_int

    # Custom attr: set_custom_attr_bool on Context
    lib.fdl_context_set_custom_attr_bool.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
    lib.fdl_context_set_custom_attr_bool.restype = ctypes.c_int

    # Custom attr: get_custom_attr_string on Context
    lib.fdl_context_get_custom_attr_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_context_get_custom_attr_string.restype = ctypes.c_char_p

    # Custom attr: get_custom_attr_int on Context
    lib.fdl_context_get_custom_attr_int.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int64)]
    lib.fdl_context_get_custom_attr_int.restype = ctypes.c_int

    # Custom attr: get_custom_attr_float on Context
    lib.fdl_context_get_custom_attr_float.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_double)]
    lib.fdl_context_get_custom_attr_float.restype = ctypes.c_int

    # Custom attr: get_custom_attr_bool on Context
    lib.fdl_context_get_custom_attr_bool.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
    lib.fdl_context_get_custom_attr_bool.restype = ctypes.c_int

    # Custom attr: has_custom_attr on Context
    lib.fdl_context_has_custom_attr.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_context_has_custom_attr.restype = ctypes.c_int

    # Custom attr: get_custom_attr_type on Context
    lib.fdl_context_get_custom_attr_type.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_context_get_custom_attr_type.restype = ctypes.c_uint32

    # Custom attr: remove_custom_attr on Context
    lib.fdl_context_remove_custom_attr.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_context_remove_custom_attr.restype = ctypes.c_int

    # Custom attr: custom_attrs_count on Context
    lib.fdl_context_custom_attrs_count.argtypes = [ctypes.c_void_p]
    lib.fdl_context_custom_attrs_count.restype = ctypes.c_uint32

    # Custom attr: custom_attr_name_at on Context
    lib.fdl_context_custom_attr_name_at.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    lib.fdl_context_custom_attr_name_at.restype = ctypes.c_char_p

    # Custom attr: set_custom_attr_point_f64 on Context
    lib.fdl_context_set_custom_attr_point_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, fdl_point_f64_t]
    lib.fdl_context_set_custom_attr_point_f64.restype = ctypes.c_int

    # Custom attr: get_custom_attr_point_f64 on Context
    lib.fdl_context_get_custom_attr_point_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_point_f64_t)]
    lib.fdl_context_get_custom_attr_point_f64.restype = ctypes.c_int

    # Custom attr: set_custom_attr_dims_f64 on Context
    lib.fdl_context_set_custom_attr_dims_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, fdl_dimensions_f64_t]
    lib.fdl_context_set_custom_attr_dims_f64.restype = ctypes.c_int

    # Custom attr: get_custom_attr_dims_f64 on Context
    lib.fdl_context_get_custom_attr_dims_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_dimensions_f64_t)]
    lib.fdl_context_get_custom_attr_dims_f64.restype = ctypes.c_int

    # Custom attr: set_custom_attr_dims_i64 on Context
    lib.fdl_context_set_custom_attr_dims_i64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, fdl_dimensions_i64_t]
    lib.fdl_context_set_custom_attr_dims_i64.restype = ctypes.c_int

    # Custom attr: get_custom_attr_dims_i64 on Context
    lib.fdl_context_get_custom_attr_dims_i64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_dimensions_i64_t)]
    lib.fdl_context_get_custom_attr_dims_i64.restype = ctypes.c_int

    # Custom attr: set_custom_attr_string on Canvas
    lib.fdl_canvas_set_custom_attr_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
    lib.fdl_canvas_set_custom_attr_string.restype = ctypes.c_int

    # Custom attr: set_custom_attr_int on Canvas
    lib.fdl_canvas_set_custom_attr_int.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int64]
    lib.fdl_canvas_set_custom_attr_int.restype = ctypes.c_int

    # Custom attr: set_custom_attr_float on Canvas
    lib.fdl_canvas_set_custom_attr_float.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_double]
    lib.fdl_canvas_set_custom_attr_float.restype = ctypes.c_int

    # Custom attr: set_custom_attr_bool on Canvas
    lib.fdl_canvas_set_custom_attr_bool.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
    lib.fdl_canvas_set_custom_attr_bool.restype = ctypes.c_int

    # Custom attr: get_custom_attr_string on Canvas
    lib.fdl_canvas_get_custom_attr_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_canvas_get_custom_attr_string.restype = ctypes.c_char_p

    # Custom attr: get_custom_attr_int on Canvas
    lib.fdl_canvas_get_custom_attr_int.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int64)]
    lib.fdl_canvas_get_custom_attr_int.restype = ctypes.c_int

    # Custom attr: get_custom_attr_float on Canvas
    lib.fdl_canvas_get_custom_attr_float.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_double)]
    lib.fdl_canvas_get_custom_attr_float.restype = ctypes.c_int

    # Custom attr: get_custom_attr_bool on Canvas
    lib.fdl_canvas_get_custom_attr_bool.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
    lib.fdl_canvas_get_custom_attr_bool.restype = ctypes.c_int

    # Custom attr: has_custom_attr on Canvas
    lib.fdl_canvas_has_custom_attr.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_canvas_has_custom_attr.restype = ctypes.c_int

    # Custom attr: get_custom_attr_type on Canvas
    lib.fdl_canvas_get_custom_attr_type.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_canvas_get_custom_attr_type.restype = ctypes.c_uint32

    # Custom attr: remove_custom_attr on Canvas
    lib.fdl_canvas_remove_custom_attr.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_canvas_remove_custom_attr.restype = ctypes.c_int

    # Custom attr: custom_attrs_count on Canvas
    lib.fdl_canvas_custom_attrs_count.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_custom_attrs_count.restype = ctypes.c_uint32

    # Custom attr: custom_attr_name_at on Canvas
    lib.fdl_canvas_custom_attr_name_at.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    lib.fdl_canvas_custom_attr_name_at.restype = ctypes.c_char_p

    # Custom attr: set_custom_attr_point_f64 on Canvas
    lib.fdl_canvas_set_custom_attr_point_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, fdl_point_f64_t]
    lib.fdl_canvas_set_custom_attr_point_f64.restype = ctypes.c_int

    # Custom attr: get_custom_attr_point_f64 on Canvas
    lib.fdl_canvas_get_custom_attr_point_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_point_f64_t)]
    lib.fdl_canvas_get_custom_attr_point_f64.restype = ctypes.c_int

    # Custom attr: set_custom_attr_dims_f64 on Canvas
    lib.fdl_canvas_set_custom_attr_dims_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, fdl_dimensions_f64_t]
    lib.fdl_canvas_set_custom_attr_dims_f64.restype = ctypes.c_int

    # Custom attr: get_custom_attr_dims_f64 on Canvas
    lib.fdl_canvas_get_custom_attr_dims_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_dimensions_f64_t)]
    lib.fdl_canvas_get_custom_attr_dims_f64.restype = ctypes.c_int

    # Custom attr: set_custom_attr_dims_i64 on Canvas
    lib.fdl_canvas_set_custom_attr_dims_i64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, fdl_dimensions_i64_t]
    lib.fdl_canvas_set_custom_attr_dims_i64.restype = ctypes.c_int

    # Custom attr: get_custom_attr_dims_i64 on Canvas
    lib.fdl_canvas_get_custom_attr_dims_i64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_dimensions_i64_t)]
    lib.fdl_canvas_get_custom_attr_dims_i64.restype = ctypes.c_int

    # Custom attr: set_custom_attr_string on FramingDecision
    lib.fdl_framing_decision_set_custom_attr_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
    lib.fdl_framing_decision_set_custom_attr_string.restype = ctypes.c_int

    # Custom attr: set_custom_attr_int on FramingDecision
    lib.fdl_framing_decision_set_custom_attr_int.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int64]
    lib.fdl_framing_decision_set_custom_attr_int.restype = ctypes.c_int

    # Custom attr: set_custom_attr_float on FramingDecision
    lib.fdl_framing_decision_set_custom_attr_float.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_double]
    lib.fdl_framing_decision_set_custom_attr_float.restype = ctypes.c_int

    # Custom attr: set_custom_attr_bool on FramingDecision
    lib.fdl_framing_decision_set_custom_attr_bool.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
    lib.fdl_framing_decision_set_custom_attr_bool.restype = ctypes.c_int

    # Custom attr: get_custom_attr_string on FramingDecision
    lib.fdl_framing_decision_get_custom_attr_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_framing_decision_get_custom_attr_string.restype = ctypes.c_char_p

    # Custom attr: get_custom_attr_int on FramingDecision
    lib.fdl_framing_decision_get_custom_attr_int.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int64)]
    lib.fdl_framing_decision_get_custom_attr_int.restype = ctypes.c_int

    # Custom attr: get_custom_attr_float on FramingDecision
    lib.fdl_framing_decision_get_custom_attr_float.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_double)]
    lib.fdl_framing_decision_get_custom_attr_float.restype = ctypes.c_int

    # Custom attr: get_custom_attr_bool on FramingDecision
    lib.fdl_framing_decision_get_custom_attr_bool.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
    lib.fdl_framing_decision_get_custom_attr_bool.restype = ctypes.c_int

    # Custom attr: has_custom_attr on FramingDecision
    lib.fdl_framing_decision_has_custom_attr.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_framing_decision_has_custom_attr.restype = ctypes.c_int

    # Custom attr: get_custom_attr_type on FramingDecision
    lib.fdl_framing_decision_get_custom_attr_type.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_framing_decision_get_custom_attr_type.restype = ctypes.c_uint32

    # Custom attr: remove_custom_attr on FramingDecision
    lib.fdl_framing_decision_remove_custom_attr.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_framing_decision_remove_custom_attr.restype = ctypes.c_int

    # Custom attr: custom_attrs_count on FramingDecision
    lib.fdl_framing_decision_custom_attrs_count.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_decision_custom_attrs_count.restype = ctypes.c_uint32

    # Custom attr: custom_attr_name_at on FramingDecision
    lib.fdl_framing_decision_custom_attr_name_at.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    lib.fdl_framing_decision_custom_attr_name_at.restype = ctypes.c_char_p

    # Custom attr: set_custom_attr_point_f64 on FramingDecision
    lib.fdl_framing_decision_set_custom_attr_point_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, fdl_point_f64_t]
    lib.fdl_framing_decision_set_custom_attr_point_f64.restype = ctypes.c_int

    # Custom attr: get_custom_attr_point_f64 on FramingDecision
    lib.fdl_framing_decision_get_custom_attr_point_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_point_f64_t)]
    lib.fdl_framing_decision_get_custom_attr_point_f64.restype = ctypes.c_int

    # Custom attr: set_custom_attr_dims_f64 on FramingDecision
    lib.fdl_framing_decision_set_custom_attr_dims_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, fdl_dimensions_f64_t]
    lib.fdl_framing_decision_set_custom_attr_dims_f64.restype = ctypes.c_int

    # Custom attr: get_custom_attr_dims_f64 on FramingDecision
    lib.fdl_framing_decision_get_custom_attr_dims_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_dimensions_f64_t)]
    lib.fdl_framing_decision_get_custom_attr_dims_f64.restype = ctypes.c_int

    # Custom attr: set_custom_attr_dims_i64 on FramingDecision
    lib.fdl_framing_decision_set_custom_attr_dims_i64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, fdl_dimensions_i64_t]
    lib.fdl_framing_decision_set_custom_attr_dims_i64.restype = ctypes.c_int

    # Custom attr: get_custom_attr_dims_i64 on FramingDecision
    lib.fdl_framing_decision_get_custom_attr_dims_i64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_dimensions_i64_t)]
    lib.fdl_framing_decision_get_custom_attr_dims_i64.restype = ctypes.c_int

    # Custom attr: set_custom_attr_string on FramingIntent
    lib.fdl_framing_intent_set_custom_attr_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
    lib.fdl_framing_intent_set_custom_attr_string.restype = ctypes.c_int

    # Custom attr: set_custom_attr_int on FramingIntent
    lib.fdl_framing_intent_set_custom_attr_int.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int64]
    lib.fdl_framing_intent_set_custom_attr_int.restype = ctypes.c_int

    # Custom attr: set_custom_attr_float on FramingIntent
    lib.fdl_framing_intent_set_custom_attr_float.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_double]
    lib.fdl_framing_intent_set_custom_attr_float.restype = ctypes.c_int

    # Custom attr: set_custom_attr_bool on FramingIntent
    lib.fdl_framing_intent_set_custom_attr_bool.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
    lib.fdl_framing_intent_set_custom_attr_bool.restype = ctypes.c_int

    # Custom attr: get_custom_attr_string on FramingIntent
    lib.fdl_framing_intent_get_custom_attr_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_framing_intent_get_custom_attr_string.restype = ctypes.c_char_p

    # Custom attr: get_custom_attr_int on FramingIntent
    lib.fdl_framing_intent_get_custom_attr_int.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int64)]
    lib.fdl_framing_intent_get_custom_attr_int.restype = ctypes.c_int

    # Custom attr: get_custom_attr_float on FramingIntent
    lib.fdl_framing_intent_get_custom_attr_float.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_double)]
    lib.fdl_framing_intent_get_custom_attr_float.restype = ctypes.c_int

    # Custom attr: get_custom_attr_bool on FramingIntent
    lib.fdl_framing_intent_get_custom_attr_bool.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
    lib.fdl_framing_intent_get_custom_attr_bool.restype = ctypes.c_int

    # Custom attr: has_custom_attr on FramingIntent
    lib.fdl_framing_intent_has_custom_attr.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_framing_intent_has_custom_attr.restype = ctypes.c_int

    # Custom attr: get_custom_attr_type on FramingIntent
    lib.fdl_framing_intent_get_custom_attr_type.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_framing_intent_get_custom_attr_type.restype = ctypes.c_uint32

    # Custom attr: remove_custom_attr on FramingIntent
    lib.fdl_framing_intent_remove_custom_attr.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_framing_intent_remove_custom_attr.restype = ctypes.c_int

    # Custom attr: custom_attrs_count on FramingIntent
    lib.fdl_framing_intent_custom_attrs_count.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_intent_custom_attrs_count.restype = ctypes.c_uint32

    # Custom attr: custom_attr_name_at on FramingIntent
    lib.fdl_framing_intent_custom_attr_name_at.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    lib.fdl_framing_intent_custom_attr_name_at.restype = ctypes.c_char_p

    # Custom attr: set_custom_attr_point_f64 on FramingIntent
    lib.fdl_framing_intent_set_custom_attr_point_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, fdl_point_f64_t]
    lib.fdl_framing_intent_set_custom_attr_point_f64.restype = ctypes.c_int

    # Custom attr: get_custom_attr_point_f64 on FramingIntent
    lib.fdl_framing_intent_get_custom_attr_point_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_point_f64_t)]
    lib.fdl_framing_intent_get_custom_attr_point_f64.restype = ctypes.c_int

    # Custom attr: set_custom_attr_dims_f64 on FramingIntent
    lib.fdl_framing_intent_set_custom_attr_dims_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, fdl_dimensions_f64_t]
    lib.fdl_framing_intent_set_custom_attr_dims_f64.restype = ctypes.c_int

    # Custom attr: get_custom_attr_dims_f64 on FramingIntent
    lib.fdl_framing_intent_get_custom_attr_dims_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_dimensions_f64_t)]
    lib.fdl_framing_intent_get_custom_attr_dims_f64.restype = ctypes.c_int

    # Custom attr: set_custom_attr_dims_i64 on FramingIntent
    lib.fdl_framing_intent_set_custom_attr_dims_i64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, fdl_dimensions_i64_t]
    lib.fdl_framing_intent_set_custom_attr_dims_i64.restype = ctypes.c_int

    # Custom attr: get_custom_attr_dims_i64 on FramingIntent
    lib.fdl_framing_intent_get_custom_attr_dims_i64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_dimensions_i64_t)]
    lib.fdl_framing_intent_get_custom_attr_dims_i64.restype = ctypes.c_int

    # Custom attr: set_custom_attr_string on CanvasTemplate
    lib.fdl_canvas_template_set_custom_attr_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
    lib.fdl_canvas_template_set_custom_attr_string.restype = ctypes.c_int

    # Custom attr: set_custom_attr_int on CanvasTemplate
    lib.fdl_canvas_template_set_custom_attr_int.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int64]
    lib.fdl_canvas_template_set_custom_attr_int.restype = ctypes.c_int

    # Custom attr: set_custom_attr_float on CanvasTemplate
    lib.fdl_canvas_template_set_custom_attr_float.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_double]
    lib.fdl_canvas_template_set_custom_attr_float.restype = ctypes.c_int

    # Custom attr: set_custom_attr_bool on CanvasTemplate
    lib.fdl_canvas_template_set_custom_attr_bool.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
    lib.fdl_canvas_template_set_custom_attr_bool.restype = ctypes.c_int

    # Custom attr: get_custom_attr_string on CanvasTemplate
    lib.fdl_canvas_template_get_custom_attr_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_canvas_template_get_custom_attr_string.restype = ctypes.c_char_p

    # Custom attr: get_custom_attr_int on CanvasTemplate
    lib.fdl_canvas_template_get_custom_attr_int.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int64)]
    lib.fdl_canvas_template_get_custom_attr_int.restype = ctypes.c_int

    # Custom attr: get_custom_attr_float on CanvasTemplate
    lib.fdl_canvas_template_get_custom_attr_float.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_double)]
    lib.fdl_canvas_template_get_custom_attr_float.restype = ctypes.c_int

    # Custom attr: get_custom_attr_bool on CanvasTemplate
    lib.fdl_canvas_template_get_custom_attr_bool.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
    lib.fdl_canvas_template_get_custom_attr_bool.restype = ctypes.c_int

    # Custom attr: has_custom_attr on CanvasTemplate
    lib.fdl_canvas_template_has_custom_attr.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_canvas_template_has_custom_attr.restype = ctypes.c_int

    # Custom attr: get_custom_attr_type on CanvasTemplate
    lib.fdl_canvas_template_get_custom_attr_type.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_canvas_template_get_custom_attr_type.restype = ctypes.c_uint32

    # Custom attr: remove_custom_attr on CanvasTemplate
    lib.fdl_canvas_template_remove_custom_attr.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_canvas_template_remove_custom_attr.restype = ctypes.c_int

    # Custom attr: custom_attrs_count on CanvasTemplate
    lib.fdl_canvas_template_custom_attrs_count.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_custom_attrs_count.restype = ctypes.c_uint32

    # Custom attr: custom_attr_name_at on CanvasTemplate
    lib.fdl_canvas_template_custom_attr_name_at.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    lib.fdl_canvas_template_custom_attr_name_at.restype = ctypes.c_char_p

    # Custom attr: set_custom_attr_point_f64 on CanvasTemplate
    lib.fdl_canvas_template_set_custom_attr_point_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, fdl_point_f64_t]
    lib.fdl_canvas_template_set_custom_attr_point_f64.restype = ctypes.c_int

    # Custom attr: get_custom_attr_point_f64 on CanvasTemplate
    lib.fdl_canvas_template_get_custom_attr_point_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_point_f64_t)]
    lib.fdl_canvas_template_get_custom_attr_point_f64.restype = ctypes.c_int

    # Custom attr: set_custom_attr_dims_f64 on CanvasTemplate
    lib.fdl_canvas_template_set_custom_attr_dims_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, fdl_dimensions_f64_t]
    lib.fdl_canvas_template_set_custom_attr_dims_f64.restype = ctypes.c_int

    # Custom attr: get_custom_attr_dims_f64 on CanvasTemplate
    lib.fdl_canvas_template_get_custom_attr_dims_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_dimensions_f64_t)]
    lib.fdl_canvas_template_get_custom_attr_dims_f64.restype = ctypes.c_int

    # Custom attr: set_custom_attr_dims_i64 on CanvasTemplate
    lib.fdl_canvas_template_set_custom_attr_dims_i64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, fdl_dimensions_i64_t]
    lib.fdl_canvas_template_set_custom_attr_dims_i64.restype = ctypes.c_int

    # Custom attr: get_custom_attr_dims_i64 on CanvasTemplate
    lib.fdl_canvas_template_get_custom_attr_dims_i64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_dimensions_i64_t)]
    lib.fdl_canvas_template_get_custom_attr_dims_i64.restype = ctypes.c_int

    # Custom attr: set_custom_attr_string on ClipID
    lib.fdl_clip_id_set_custom_attr_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
    lib.fdl_clip_id_set_custom_attr_string.restype = ctypes.c_int

    # Custom attr: set_custom_attr_int on ClipID
    lib.fdl_clip_id_set_custom_attr_int.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int64]
    lib.fdl_clip_id_set_custom_attr_int.restype = ctypes.c_int

    # Custom attr: set_custom_attr_float on ClipID
    lib.fdl_clip_id_set_custom_attr_float.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_double]
    lib.fdl_clip_id_set_custom_attr_float.restype = ctypes.c_int

    # Custom attr: set_custom_attr_bool on ClipID
    lib.fdl_clip_id_set_custom_attr_bool.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
    lib.fdl_clip_id_set_custom_attr_bool.restype = ctypes.c_int

    # Custom attr: get_custom_attr_string on ClipID
    lib.fdl_clip_id_get_custom_attr_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_clip_id_get_custom_attr_string.restype = ctypes.c_char_p

    # Custom attr: get_custom_attr_int on ClipID
    lib.fdl_clip_id_get_custom_attr_int.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int64)]
    lib.fdl_clip_id_get_custom_attr_int.restype = ctypes.c_int

    # Custom attr: get_custom_attr_float on ClipID
    lib.fdl_clip_id_get_custom_attr_float.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_double)]
    lib.fdl_clip_id_get_custom_attr_float.restype = ctypes.c_int

    # Custom attr: get_custom_attr_bool on ClipID
    lib.fdl_clip_id_get_custom_attr_bool.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
    lib.fdl_clip_id_get_custom_attr_bool.restype = ctypes.c_int

    # Custom attr: has_custom_attr on ClipID
    lib.fdl_clip_id_has_custom_attr.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_clip_id_has_custom_attr.restype = ctypes.c_int

    # Custom attr: get_custom_attr_type on ClipID
    lib.fdl_clip_id_get_custom_attr_type.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_clip_id_get_custom_attr_type.restype = ctypes.c_uint32

    # Custom attr: remove_custom_attr on ClipID
    lib.fdl_clip_id_remove_custom_attr.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_clip_id_remove_custom_attr.restype = ctypes.c_int

    # Custom attr: custom_attrs_count on ClipID
    lib.fdl_clip_id_custom_attrs_count.argtypes = [ctypes.c_void_p]
    lib.fdl_clip_id_custom_attrs_count.restype = ctypes.c_uint32

    # Custom attr: custom_attr_name_at on ClipID
    lib.fdl_clip_id_custom_attr_name_at.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    lib.fdl_clip_id_custom_attr_name_at.restype = ctypes.c_char_p

    # Custom attr: set_custom_attr_point_f64 on ClipID
    lib.fdl_clip_id_set_custom_attr_point_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, fdl_point_f64_t]
    lib.fdl_clip_id_set_custom_attr_point_f64.restype = ctypes.c_int

    # Custom attr: get_custom_attr_point_f64 on ClipID
    lib.fdl_clip_id_get_custom_attr_point_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_point_f64_t)]
    lib.fdl_clip_id_get_custom_attr_point_f64.restype = ctypes.c_int

    # Custom attr: set_custom_attr_dims_f64 on ClipID
    lib.fdl_clip_id_set_custom_attr_dims_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, fdl_dimensions_f64_t]
    lib.fdl_clip_id_set_custom_attr_dims_f64.restype = ctypes.c_int

    # Custom attr: get_custom_attr_dims_f64 on ClipID
    lib.fdl_clip_id_get_custom_attr_dims_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_dimensions_f64_t)]
    lib.fdl_clip_id_get_custom_attr_dims_f64.restype = ctypes.c_int

    # Custom attr: set_custom_attr_dims_i64 on ClipID
    lib.fdl_clip_id_set_custom_attr_dims_i64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, fdl_dimensions_i64_t]
    lib.fdl_clip_id_set_custom_attr_dims_i64.restype = ctypes.c_int

    # Custom attr: get_custom_attr_dims_i64 on ClipID
    lib.fdl_clip_id_get_custom_attr_dims_i64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_dimensions_i64_t)]
    lib.fdl_clip_id_get_custom_attr_dims_i64.restype = ctypes.c_int

    # Custom attr: set_custom_attr_string on FileSequence
    lib.fdl_file_sequence_set_custom_attr_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
    lib.fdl_file_sequence_set_custom_attr_string.restype = ctypes.c_int

    # Custom attr: set_custom_attr_int on FileSequence
    lib.fdl_file_sequence_set_custom_attr_int.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int64]
    lib.fdl_file_sequence_set_custom_attr_int.restype = ctypes.c_int

    # Custom attr: set_custom_attr_float on FileSequence
    lib.fdl_file_sequence_set_custom_attr_float.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_double]
    lib.fdl_file_sequence_set_custom_attr_float.restype = ctypes.c_int

    # Custom attr: set_custom_attr_bool on FileSequence
    lib.fdl_file_sequence_set_custom_attr_bool.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
    lib.fdl_file_sequence_set_custom_attr_bool.restype = ctypes.c_int

    # Custom attr: get_custom_attr_string on FileSequence
    lib.fdl_file_sequence_get_custom_attr_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_file_sequence_get_custom_attr_string.restype = ctypes.c_char_p

    # Custom attr: get_custom_attr_int on FileSequence
    lib.fdl_file_sequence_get_custom_attr_int.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int64)]
    lib.fdl_file_sequence_get_custom_attr_int.restype = ctypes.c_int

    # Custom attr: get_custom_attr_float on FileSequence
    lib.fdl_file_sequence_get_custom_attr_float.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_double)]
    lib.fdl_file_sequence_get_custom_attr_float.restype = ctypes.c_int

    # Custom attr: get_custom_attr_bool on FileSequence
    lib.fdl_file_sequence_get_custom_attr_bool.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
    lib.fdl_file_sequence_get_custom_attr_bool.restype = ctypes.c_int

    # Custom attr: has_custom_attr on FileSequence
    lib.fdl_file_sequence_has_custom_attr.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_file_sequence_has_custom_attr.restype = ctypes.c_int

    # Custom attr: get_custom_attr_type on FileSequence
    lib.fdl_file_sequence_get_custom_attr_type.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_file_sequence_get_custom_attr_type.restype = ctypes.c_uint32

    # Custom attr: remove_custom_attr on FileSequence
    lib.fdl_file_sequence_remove_custom_attr.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_file_sequence_remove_custom_attr.restype = ctypes.c_int

    # Custom attr: custom_attrs_count on FileSequence
    lib.fdl_file_sequence_custom_attrs_count.argtypes = [ctypes.c_void_p]
    lib.fdl_file_sequence_custom_attrs_count.restype = ctypes.c_uint32

    # Custom attr: custom_attr_name_at on FileSequence
    lib.fdl_file_sequence_custom_attr_name_at.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    lib.fdl_file_sequence_custom_attr_name_at.restype = ctypes.c_char_p

    # Custom attr: set_custom_attr_point_f64 on FileSequence
    lib.fdl_file_sequence_set_custom_attr_point_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, fdl_point_f64_t]
    lib.fdl_file_sequence_set_custom_attr_point_f64.restype = ctypes.c_int

    # Custom attr: get_custom_attr_point_f64 on FileSequence
    lib.fdl_file_sequence_get_custom_attr_point_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_point_f64_t)]
    lib.fdl_file_sequence_get_custom_attr_point_f64.restype = ctypes.c_int

    # Custom attr: set_custom_attr_dims_f64 on FileSequence
    lib.fdl_file_sequence_set_custom_attr_dims_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, fdl_dimensions_f64_t]
    lib.fdl_file_sequence_set_custom_attr_dims_f64.restype = ctypes.c_int

    # Custom attr: get_custom_attr_dims_f64 on FileSequence
    lib.fdl_file_sequence_get_custom_attr_dims_f64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_dimensions_f64_t)]
    lib.fdl_file_sequence_get_custom_attr_dims_f64.restype = ctypes.c_int

    # Custom attr: set_custom_attr_dims_i64 on FileSequence
    lib.fdl_file_sequence_set_custom_attr_dims_i64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, fdl_dimensions_i64_t]
    lib.fdl_file_sequence_set_custom_attr_dims_i64.restype = ctypes.c_int

    # Custom attr: get_custom_attr_dims_i64 on FileSequence
    lib.fdl_file_sequence_get_custom_attr_dims_i64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_dimensions_i64_t)]
    lib.fdl_file_sequence_get_custom_attr_dims_i64.restype = ctypes.c_int

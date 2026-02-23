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

    # Apply a canvas template to a source canvas/framing.
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

    # Add a framing decision to a canvas.
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

    # Find a framing decision by its ID within a canvas.
    lib.fdl_canvas_find_framing_decision_by_id.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_canvas_find_framing_decision_by_id.restype = ctypes.c_void_p

    # Get a framing decision by index within a canvas.
    lib.fdl_canvas_framing_decision_at.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    lib.fdl_canvas_framing_decision_at.restype = ctypes.c_void_p

    # Get the number of framing decisions in a canvas.
    lib.fdl_canvas_framing_decisions_count.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_framing_decisions_count.restype = ctypes.c_uint32

    # Get the anamorphic squeeze factor.
    lib.fdl_canvas_get_anamorphic_squeeze.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_get_anamorphic_squeeze.restype = ctypes.c_double

    # Get the canvas dimensions in pixels.
    lib.fdl_canvas_get_dimensions.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_get_dimensions.restype = fdl_dimensions_i64_t

    # Get the effective anchor point (offset from canvas origin).
    lib.fdl_canvas_get_effective_anchor_point.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_get_effective_anchor_point.restype = fdl_point_f64_t

    # Get effective (active image area) dimensions.
    lib.fdl_canvas_get_effective_dimensions.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_get_effective_dimensions.restype = fdl_dimensions_i64_t

    # Get the effective (active image) rect of a canvas.
    lib.fdl_canvas_get_effective_rect.argtypes = [ctypes.c_void_p, ctypes.POINTER(fdl_rect_t)]
    lib.fdl_canvas_get_effective_rect.restype = ctypes.c_int

    # Get the ID of a canvas.
    lib.fdl_canvas_get_id.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_get_id.restype = ctypes.c_char_p

    # Get the label of a canvas.
    lib.fdl_canvas_get_label.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_get_label.restype = ctypes.c_char_p

    # Get photosite (sensor) dimensions.
    lib.fdl_canvas_get_photosite_dimensions.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_get_photosite_dimensions.restype = fdl_dimensions_i64_t

    # Get physical dimensions (e.g. millimeters on sensor).
    lib.fdl_canvas_get_physical_dimensions.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_get_physical_dimensions.restype = fdl_dimensions_f64_t

    # Get the full canvas rect: (0, 0, dims.width, dims.height).
    lib.fdl_canvas_get_rect.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_get_rect.restype = fdl_rect_t

    # Get the source_canvas_id of a canvas (the canvas this was derived from).
    lib.fdl_canvas_get_source_canvas_id.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_get_source_canvas_id.restype = ctypes.c_char_p

    # Check if the canvas has effective dimensions set.
    lib.fdl_canvas_has_effective_dimensions.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_has_effective_dimensions.restype = ctypes.c_int

    # Check if the canvas has photosite dimensions set.
    lib.fdl_canvas_has_photosite_dimensions.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_has_photosite_dimensions.restype = ctypes.c_int

    # Check if the canvas has physical dimensions set.
    lib.fdl_canvas_has_physical_dimensions.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_has_physical_dimensions.restype = ctypes.c_int

    # Remove effective dimensions and anchor from a canvas.
    lib.fdl_canvas_remove_effective.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_remove_effective.restype = None

    # Set anamorphic squeeze on a canvas.
    lib.fdl_canvas_set_anamorphic_squeeze.argtypes = [ctypes.c_void_p, ctypes.c_double]
    lib.fdl_canvas_set_anamorphic_squeeze.restype = None

    # Set dimensions on a canvas.
    lib.fdl_canvas_set_dimensions.argtypes = [ctypes.c_void_p, fdl_dimensions_i64_t]
    lib.fdl_canvas_set_dimensions.restype = None

    # Set effective dimensions and anchor on a canvas.
    lib.fdl_canvas_set_effective_dimensions.argtypes = [ctypes.c_void_p, fdl_dimensions_i64_t, fdl_point_f64_t]
    lib.fdl_canvas_set_effective_dimensions.restype = None

    # Set effective dimensions on a canvas.
    lib.fdl_canvas_set_effective_dims_only.argtypes = [ctypes.c_void_p, fdl_dimensions_i64_t]
    lib.fdl_canvas_set_effective_dims_only.restype = None

    # Set photosite dimensions on a canvas.
    lib.fdl_canvas_set_photosite_dimensions.argtypes = [ctypes.c_void_p, fdl_dimensions_i64_t]
    lib.fdl_canvas_set_photosite_dimensions.restype = None

    # Set physical dimensions on a canvas.
    lib.fdl_canvas_set_physical_dimensions.argtypes = [ctypes.c_void_p, fdl_dimensions_f64_t]
    lib.fdl_canvas_set_physical_dimensions.restype = None

    # Get the horizontal alignment method.
    lib.fdl_canvas_template_get_alignment_method_horizontal.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_get_alignment_method_horizontal.restype = ctypes.c_uint32

    # Get the vertical alignment method.
    lib.fdl_canvas_template_get_alignment_method_vertical.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_get_alignment_method_vertical.restype = ctypes.c_uint32

    # Get the fit method — how source is scaled into target.
    lib.fdl_canvas_template_get_fit_method.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_get_fit_method.restype = ctypes.c_uint32

    # Get the fit source — which dimension layer to scale from.
    lib.fdl_canvas_template_get_fit_source.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_get_fit_source.restype = ctypes.c_uint32

    # Get the ID of a canvas template.
    lib.fdl_canvas_template_get_id.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_get_id.restype = ctypes.c_char_p

    # Get the label of a canvas template.
    lib.fdl_canvas_template_get_label.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_get_label.restype = ctypes.c_char_p

    # Get the maximum_dimensions constraint.
    lib.fdl_canvas_template_get_maximum_dimensions.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_get_maximum_dimensions.restype = fdl_dimensions_i64_t

    # Get the pad_to_maximum flag.
    lib.fdl_canvas_template_get_pad_to_maximum.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_get_pad_to_maximum.restype = ctypes.c_int

    # Get the preserve_from_source_canvas geometry path.
    lib.fdl_canvas_template_get_preserve_from_source_canvas.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_get_preserve_from_source_canvas.restype = ctypes.c_uint32

    # Get the rounding strategy.
    lib.fdl_canvas_template_get_round.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_get_round.restype = fdl_round_strategy_t

    # Get the target anamorphic squeeze factor.
    lib.fdl_canvas_template_get_target_anamorphic_squeeze.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_get_target_anamorphic_squeeze.restype = ctypes.c_double

    # Get the target dimensions of a canvas template.
    lib.fdl_canvas_template_get_target_dimensions.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_get_target_dimensions.restype = fdl_dimensions_i64_t

    # Check if maximum_dimensions constraint is set.
    lib.fdl_canvas_template_has_maximum_dimensions.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_has_maximum_dimensions.restype = ctypes.c_int

    # Check if preserve_from_source_canvas is set.
    lib.fdl_canvas_template_has_preserve_from_source_canvas.argtypes = [ctypes.c_void_p]
    lib.fdl_canvas_template_has_preserve_from_source_canvas.restype = ctypes.c_int

    # Set maximum_dimensions on a canvas template.
    lib.fdl_canvas_template_set_maximum_dimensions.argtypes = [ctypes.c_void_p, fdl_dimensions_i64_t]
    lib.fdl_canvas_template_set_maximum_dimensions.restype = None

    # Set pad_to_maximum flag on a canvas template.
    lib.fdl_canvas_template_set_pad_to_maximum.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.fdl_canvas_template_set_pad_to_maximum.restype = None

    # Set preserve_from_source_canvas on a canvas template.
    lib.fdl_canvas_template_set_preserve_from_source_canvas.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    lib.fdl_canvas_template_set_preserve_from_source_canvas.restype = None

    # Serialize a canvas template to canonical JSON.
    lib.fdl_canvas_template_to_json.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.fdl_canvas_template_to_json.restype = ctypes.c_void_p

    # Serialize a canvas sub-object to canonical JSON.
    lib.fdl_canvas_to_json.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.fdl_canvas_to_json.restype = ctypes.c_void_p

    # Get the clip_name from a clip_id.
    lib.fdl_clip_id_get_clip_name.argtypes = [ctypes.c_void_p]
    lib.fdl_clip_id_get_clip_name.restype = ctypes.c_char_p

    # Get the file path from a clip_id.
    lib.fdl_clip_id_get_file.argtypes = [ctypes.c_void_p]
    lib.fdl_clip_id_get_file.restype = ctypes.c_char_p

    # Check if a clip_id has a file path.
    lib.fdl_clip_id_has_file.argtypes = [ctypes.c_void_p]
    lib.fdl_clip_id_has_file.restype = ctypes.c_int

    # Check if a clip_id has a file sequence.
    lib.fdl_clip_id_has_sequence.argtypes = [ctypes.c_void_p]
    lib.fdl_clip_id_has_sequence.restype = ctypes.c_int

    # Get the file sequence handle from a clip_id.
    lib.fdl_clip_id_sequence.argtypes = [ctypes.c_void_p]
    lib.fdl_clip_id_sequence.restype = ctypes.c_void_p

    # Serialize a clip_id to canonical JSON.
    lib.fdl_clip_id_to_json.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.fdl_clip_id_to_json.restype = ctypes.c_void_p

    # Validate clip_id JSON for mutual exclusion (file vs sequence).
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

    # Add a canvas to a context.
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

    # Get a canvas by index within a context.
    lib.fdl_context_canvas_at.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    lib.fdl_context_canvas_at.restype = ctypes.c_void_p

    # Get the number of canvases in a context.
    lib.fdl_context_canvases_count.argtypes = [ctypes.c_void_p]
    lib.fdl_context_canvases_count.restype = ctypes.c_uint32

    # Get the clip_id handle from a context.
    lib.fdl_context_clip_id.argtypes = [ctypes.c_void_p]
    lib.fdl_context_clip_id.restype = ctypes.c_void_p

    # Find a canvas by its ID within a context.
    lib.fdl_context_find_canvas_by_id.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_context_find_canvas_by_id.restype = ctypes.c_void_p

    # Get clip_id as a JSON string.
    lib.fdl_context_get_clip_id.argtypes = [ctypes.c_void_p]
    lib.fdl_context_get_clip_id.restype = ctypes.c_void_p

    # Get the context_creator of a context.
    lib.fdl_context_get_context_creator.argtypes = [ctypes.c_void_p]
    lib.fdl_context_get_context_creator.restype = ctypes.c_char_p

    # Get the label of a context.
    lib.fdl_context_get_label.argtypes = [ctypes.c_void_p]
    lib.fdl_context_get_label.restype = ctypes.c_char_p

    # Check if a context has a clip_id.
    lib.fdl_context_has_clip_id.argtypes = [ctypes.c_void_p]
    lib.fdl_context_has_clip_id.restype = ctypes.c_int

    # Remove clip_id from a context. Safe to call if not present.
    lib.fdl_context_remove_clip_id.argtypes = [ctypes.c_void_p]
    lib.fdl_context_remove_clip_id.restype = None

    # Resolve canvas for given input dimensions.
    lib.fdl_context_resolve_canvas_for_dimensions.argtypes = [ctypes.c_void_p, fdl_dimensions_f64_t, ctypes.c_void_p, ctypes.c_void_p]
    lib.fdl_context_resolve_canvas_for_dimensions.restype = fdl_resolve_canvas_result_t

    # Set clip_id on a context from a JSON string.
    lib.fdl_context_set_clip_id_json.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]
    lib.fdl_context_set_clip_id_json.restype = ctypes.c_void_p

    # Serialize a context sub-object to canonical JSON.
    lib.fdl_context_to_json.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.fdl_context_to_json.restype = ctypes.c_void_p

    # Clamp dimensions to maximum bounds.
    lib.fdl_dimensions_clamp_to_dims.argtypes = [fdl_dimensions_f64_t, fdl_dimensions_f64_t, ctypes.POINTER(fdl_point_f64_t)]
    lib.fdl_dimensions_clamp_to_dims.restype = fdl_dimensions_f64_t

    # Check if dimensions are approximately equal within FDL tolerance.
    lib.fdl_dimensions_equal.argtypes = [fdl_dimensions_f64_t, fdl_dimensions_f64_t]
    lib.fdl_dimensions_equal.restype = ctypes.c_int

    # Check if a > b using OR logic (either width or height is greater).
    lib.fdl_dimensions_f64_gt.argtypes = [fdl_dimensions_f64_t, fdl_dimensions_f64_t]
    lib.fdl_dimensions_f64_gt.restype = ctypes.c_int

    # Check if a < b using OR logic (either width or height is less).
    lib.fdl_dimensions_f64_lt.argtypes = [fdl_dimensions_f64_t, fdl_dimensions_f64_t]
    lib.fdl_dimensions_f64_lt.restype = ctypes.c_int

    # Convert float dimensions to int64 by truncation.
    lib.fdl_dimensions_f64_to_i64.argtypes = [fdl_dimensions_f64_t]
    lib.fdl_dimensions_f64_to_i64.restype = fdl_dimensions_i64_t

    # Check if a > b using OR logic (either width or height is greater).
    lib.fdl_dimensions_i64_gt.argtypes = [fdl_dimensions_i64_t, fdl_dimensions_i64_t]
    lib.fdl_dimensions_i64_gt.restype = ctypes.c_int

    # Check if both width and height are zero (int64 variant).
    lib.fdl_dimensions_i64_is_zero.argtypes = [fdl_dimensions_i64_t]
    lib.fdl_dimensions_i64_is_zero.restype = ctypes.c_int

    # Check if a < b using OR logic (either width or height is less).
    lib.fdl_dimensions_i64_lt.argtypes = [fdl_dimensions_i64_t, fdl_dimensions_i64_t]
    lib.fdl_dimensions_i64_lt.restype = ctypes.c_int

    # Normalize int64 dimensions by applying anamorphic squeeze to width.
    lib.fdl_dimensions_i64_normalize.argtypes = [fdl_dimensions_i64_t, ctypes.c_double]
    lib.fdl_dimensions_i64_normalize.restype = fdl_dimensions_f64_t

    # Check if both width and height are zero.
    lib.fdl_dimensions_is_zero.argtypes = [fdl_dimensions_f64_t]
    lib.fdl_dimensions_is_zero.restype = ctypes.c_int

    # Normalize dimensions by applying anamorphic squeeze to width.
    lib.fdl_dimensions_normalize.argtypes = [fdl_dimensions_f64_t, ctypes.c_double]
    lib.fdl_dimensions_normalize.restype = fdl_dimensions_f64_t

    # Normalize and scale in one step.
    lib.fdl_dimensions_normalize_and_scale.argtypes = [fdl_dimensions_f64_t, ctypes.c_double, ctypes.c_double, ctypes.c_double]
    lib.fdl_dimensions_normalize_and_scale.restype = fdl_dimensions_f64_t

    # Scale normalized dimensions and apply target squeeze.
    lib.fdl_dimensions_scale.argtypes = [fdl_dimensions_f64_t, ctypes.c_double, ctypes.c_double]
    lib.fdl_dimensions_scale.restype = fdl_dimensions_f64_t

    # Subtract two dimensions: result = a - b.
    lib.fdl_dimensions_sub.argtypes = [fdl_dimensions_f64_t, fdl_dimensions_f64_t]
    lib.fdl_dimensions_sub.restype = fdl_dimensions_f64_t

    # Add a canvas template to the document.
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

    # Add a context to the document.
    lib.fdl_doc_add_context.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
    lib.fdl_doc_add_context.restype = ctypes.c_void_p

    # Add a framing intent to the document.
    lib.fdl_doc_add_framing_intent.argtypes = [
        ctypes.c_void_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_int64,
        ctypes.c_int64,
        ctypes.c_double,
    ]
    lib.fdl_doc_add_framing_intent.restype = ctypes.c_void_p

    # Get a canvas template by index.
    lib.fdl_doc_canvas_template_at.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    lib.fdl_doc_canvas_template_at.restype = ctypes.c_void_p

    # Find a canvas template by its ID string.
    lib.fdl_doc_canvas_template_find_by_id.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_doc_canvas_template_find_by_id.restype = ctypes.c_void_p

    # Get the number of canvas templates in the document.
    lib.fdl_doc_canvas_templates_count.argtypes = [ctypes.c_void_p]
    lib.fdl_doc_canvas_templates_count.restype = ctypes.c_uint32

    # Get a context by index.
    lib.fdl_doc_context_at.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    lib.fdl_doc_context_at.restype = ctypes.c_void_p

    # Find a context by its label string.
    lib.fdl_doc_context_find_by_label.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_doc_context_find_by_label.restype = ctypes.c_void_p

    # Get the number of contexts in the document.
    lib.fdl_doc_contexts_count.argtypes = [ctypes.c_void_p]
    lib.fdl_doc_contexts_count.restype = ctypes.c_uint32

    # Create an empty FDL document.
    lib.fdl_doc_create.argtypes = []
    lib.fdl_doc_create.restype = ctypes.c_void_p

    # Create a new FDL document with header fields and empty collections.
    lib.fdl_doc_create_with_header.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p]
    lib.fdl_doc_create_with_header.restype = ctypes.c_void_p

    # Get a framing intent by index.
    lib.fdl_doc_framing_intent_at.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    lib.fdl_doc_framing_intent_at.restype = ctypes.c_void_p

    # Find a framing intent by its ID string.
    lib.fdl_doc_framing_intent_find_by_id.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_doc_framing_intent_find_by_id.restype = ctypes.c_void_p

    # Get the number of framing intents in the document.
    lib.fdl_doc_framing_intents_count.argtypes = [ctypes.c_void_p]
    lib.fdl_doc_framing_intents_count.restype = ctypes.c_uint32

    # Free an FDL document and all associated handles.
    lib.fdl_doc_free.argtypes = [ctypes.c_void_p]
    lib.fdl_doc_free.restype = None

    # Get the default_framing_intent from a parsed FDL document.
    lib.fdl_doc_get_default_framing_intent.argtypes = [ctypes.c_void_p]
    lib.fdl_doc_get_default_framing_intent.restype = ctypes.c_char_p

    # Get the fdl_creator from a parsed FDL document.
    lib.fdl_doc_get_fdl_creator.argtypes = [ctypes.c_void_p]
    lib.fdl_doc_get_fdl_creator.restype = ctypes.c_char_p

    # Get the UUID from a parsed FDL document.
    lib.fdl_doc_get_uuid.argtypes = [ctypes.c_void_p]
    lib.fdl_doc_get_uuid.restype = ctypes.c_char_p

    # Get the FDL version major number.
    lib.fdl_doc_get_version_major.argtypes = [ctypes.c_void_p]
    lib.fdl_doc_get_version_major.restype = ctypes.c_int

    # Get the FDL version minor number.
    lib.fdl_doc_get_version_minor.argtypes = [ctypes.c_void_p]
    lib.fdl_doc_get_version_minor.restype = ctypes.c_int

    # Parse a JSON string into an FDL document.
    lib.fdl_doc_parse_json.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
    lib.fdl_doc_parse_json.restype = fdl_parse_result_t

    # Set the default_framing_intent on a document.
    lib.fdl_doc_set_default_framing_intent.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_doc_set_default_framing_intent.restype = None

    # Set the fdl_creator on a document.
    lib.fdl_doc_set_fdl_creator.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_doc_set_fdl_creator.restype = None

    # Set the UUID on a document.
    lib.fdl_doc_set_uuid.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.fdl_doc_set_uuid.restype = None

    # Set the FDL version on a document.
    lib.fdl_doc_set_version.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    lib.fdl_doc_set_version.restype = None

    # Serialize document to canonical JSON string.
    lib.fdl_doc_to_json.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.fdl_doc_to_json.restype = ctypes.c_void_p

    # Run schema and semantic validators on the document.
    lib.fdl_doc_validate.argtypes = [ctypes.c_void_p]
    lib.fdl_doc_validate.restype = ctypes.c_void_p

    # Get the index variable name.
    lib.fdl_file_sequence_get_idx.argtypes = [ctypes.c_void_p]
    lib.fdl_file_sequence_get_idx.restype = ctypes.c_char_p

    # Get the maximum (last) frame number.
    lib.fdl_file_sequence_get_max.argtypes = [ctypes.c_void_p]
    lib.fdl_file_sequence_get_max.restype = ctypes.c_int64

    # Get the minimum (first) frame number.
    lib.fdl_file_sequence_get_min.argtypes = [ctypes.c_void_p]
    lib.fdl_file_sequence_get_min.restype = ctypes.c_int64

    # Get the sequence pattern value string.
    lib.fdl_file_sequence_get_value.argtypes = [ctypes.c_void_p]
    lib.fdl_file_sequence_get_value.restype = ctypes.c_char_p

    # Absolute tolerance for floating-point comparison.
    lib.fdl_fp_abs_tol.argtypes = []
    lib.fdl_fp_abs_tol.restype = ctypes.c_double

    # Relative tolerance for floating-point comparison.
    lib.fdl_fp_rel_tol.argtypes = []
    lib.fdl_fp_rel_tol.restype = ctypes.c_double

    # Adjust anchor_point on a framing decision based on alignment within canvas.
    lib.fdl_framing_decision_adjust_anchor.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32]
    lib.fdl_framing_decision_adjust_anchor.restype = None

    # Adjust protection_anchor_point on a framing decision based on alignment within canvas.
    lib.fdl_framing_decision_adjust_protection_anchor.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32]
    lib.fdl_framing_decision_adjust_protection_anchor.restype = None

    # Get the anchor point of a framing decision.
    lib.fdl_framing_decision_get_anchor_point.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_decision_get_anchor_point.restype = fdl_point_f64_t

    # Get the framing decision dimensions (floating-point sub-pixel).
    lib.fdl_framing_decision_get_dimensions.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_decision_get_dimensions.restype = fdl_dimensions_f64_t

    # Get the framing_intent_id that this framing decision references.
    lib.fdl_framing_decision_get_framing_intent_id.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_decision_get_framing_intent_id.restype = ctypes.c_char_p

    # Get the ID of a framing decision.
    lib.fdl_framing_decision_get_id.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_decision_get_id.restype = ctypes.c_char_p

    # Get the label of a framing decision.
    lib.fdl_framing_decision_get_label.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_decision_get_label.restype = ctypes.c_char_p

    # Get the protection anchor point.
    lib.fdl_framing_decision_get_protection_anchor_point.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_decision_get_protection_anchor_point.restype = fdl_point_f64_t

    # Get the protection area dimensions.
    lib.fdl_framing_decision_get_protection_dimensions.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_decision_get_protection_dimensions.restype = fdl_dimensions_f64_t

    # Get the framing decision protection rect.
    lib.fdl_framing_decision_get_protection_rect.argtypes = [ctypes.c_void_p, ctypes.POINTER(fdl_rect_t)]
    lib.fdl_framing_decision_get_protection_rect.restype = ctypes.c_int

    # Get the framing decision rect: (anchor.x, anchor.y, dims.width, dims.height).
    lib.fdl_framing_decision_get_rect.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_decision_get_rect.restype = fdl_rect_t

    # Check if a framing decision has protection area set.
    lib.fdl_framing_decision_has_protection.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_decision_has_protection.restype = ctypes.c_int

    # Populate a framing decision from a canvas and framing intent.
    lib.fdl_framing_decision_populate_from_intent.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, fdl_round_strategy_t]
    lib.fdl_framing_decision_populate_from_intent.restype = None

    # Remove protection dimensions and anchor from a framing decision.
    lib.fdl_framing_decision_remove_protection.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_decision_remove_protection.restype = None

    # Set anchor point on a framing decision.
    lib.fdl_framing_decision_set_anchor_point.argtypes = [ctypes.c_void_p, fdl_point_f64_t]
    lib.fdl_framing_decision_set_anchor_point.restype = None

    # Set dimensions on a framing decision.
    lib.fdl_framing_decision_set_dimensions.argtypes = [ctypes.c_void_p, fdl_dimensions_f64_t]
    lib.fdl_framing_decision_set_dimensions.restype = None

    # Set protection dimensions and anchor on a framing decision.
    lib.fdl_framing_decision_set_protection.argtypes = [ctypes.c_void_p, fdl_dimensions_f64_t, fdl_point_f64_t]
    lib.fdl_framing_decision_set_protection.restype = None

    # Set protection anchor point on a framing decision (without changing dimensions).
    lib.fdl_framing_decision_set_protection_anchor_point.argtypes = [ctypes.c_void_p, fdl_point_f64_t]
    lib.fdl_framing_decision_set_protection_anchor_point.restype = None

    # Set protection dimensions on a framing decision (without changing anchor).
    lib.fdl_framing_decision_set_protection_dimensions.argtypes = [ctypes.c_void_p, fdl_dimensions_f64_t]
    lib.fdl_framing_decision_set_protection_dimensions.restype = None

    # Serialize a framing decision to canonical JSON.
    lib.fdl_framing_decision_to_json.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.fdl_framing_decision_to_json.restype = ctypes.c_void_p

    # Get the target aspect ratio of a framing intent.
    lib.fdl_framing_intent_get_aspect_ratio.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_intent_get_aspect_ratio.restype = fdl_dimensions_i64_t

    # Get the ID of a framing intent.
    lib.fdl_framing_intent_get_id.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_intent_get_id.restype = ctypes.c_char_p

    # Get the label of a framing intent.
    lib.fdl_framing_intent_get_label.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_intent_get_label.restype = ctypes.c_char_p

    # Get the protection factor of a framing intent.
    lib.fdl_framing_intent_get_protection.argtypes = [ctypes.c_void_p]
    lib.fdl_framing_intent_get_protection.restype = ctypes.c_double

    # Set aspect ratio on a framing intent.
    lib.fdl_framing_intent_set_aspect_ratio.argtypes = [ctypes.c_void_p, fdl_dimensions_i64_t]
    lib.fdl_framing_intent_set_aspect_ratio.restype = None

    # Set protection factor on a framing intent.
    lib.fdl_framing_intent_set_protection.argtypes = [ctypes.c_void_p, ctypes.c_double]
    lib.fdl_framing_intent_set_protection.restype = None

    # Serialize a framing intent to canonical JSON.
    lib.fdl_framing_intent_to_json.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.fdl_framing_intent_to_json.restype = ctypes.c_void_p

    # Free memory allocated by fdl_core functions.
    lib.fdl_free.argtypes = [ctypes.c_void_p]
    lib.fdl_free.restype = None

    # Apply offset to all anchors, clamping to canvas bounds.
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

    # Extract dimensions and anchor from geometry by path.
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

    # Construct a rect from raw coordinates.
    lib.fdl_make_rect.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double]
    lib.fdl_make_rect.restype = fdl_rect_t

    # Determine output canvas size for a single axis.
    lib.fdl_output_size_for_axis.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_int]
    lib.fdl_output_size_for_axis.restype = ctypes.c_double

    # Add two points: result = a + b.
    lib.fdl_point_add.argtypes = [fdl_point_f64_t, fdl_point_f64_t]
    lib.fdl_point_add.restype = fdl_point_f64_t

    # Clamp point values to [min_val, max_val].
    lib.fdl_point_clamp.argtypes = [fdl_point_f64_t, ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_int]
    lib.fdl_point_clamp.restype = fdl_point_f64_t

    # Check approximate equality within FDL tolerances.
    lib.fdl_point_equal.argtypes = [fdl_point_f64_t, fdl_point_f64_t]
    lib.fdl_point_equal.restype = ctypes.c_int

    # Check if a > b using OR logic (either x or y is greater).
    lib.fdl_point_f64_gt.argtypes = [fdl_point_f64_t, fdl_point_f64_t]
    lib.fdl_point_f64_gt.restype = ctypes.c_int

    # Check if a < b using OR logic (either x or y is less).
    lib.fdl_point_f64_lt.argtypes = [fdl_point_f64_t, fdl_point_f64_t]
    lib.fdl_point_f64_lt.restype = ctypes.c_int

    # Check if both x and y are zero.
    lib.fdl_point_is_zero.argtypes = [fdl_point_f64_t]
    lib.fdl_point_is_zero.restype = ctypes.c_int

    # Multiply point by scalar.
    lib.fdl_point_mul_scalar.argtypes = [fdl_point_f64_t, ctypes.c_double]
    lib.fdl_point_mul_scalar.restype = fdl_point_f64_t

    # Normalize a point by applying anamorphic squeeze to x.
    lib.fdl_point_normalize.argtypes = [fdl_point_f64_t, ctypes.c_double]
    lib.fdl_point_normalize.restype = fdl_point_f64_t

    # Normalize and scale a point in one step.
    lib.fdl_point_normalize_and_scale.argtypes = [fdl_point_f64_t, ctypes.c_double, ctypes.c_double, ctypes.c_double]
    lib.fdl_point_normalize_and_scale.restype = fdl_point_f64_t

    # Scale a normalized point and apply target squeeze.
    lib.fdl_point_scale.argtypes = [fdl_point_f64_t, ctypes.c_double, ctypes.c_double]
    lib.fdl_point_scale.restype = fdl_point_f64_t

    # Subtract two points: result = a - b.
    lib.fdl_point_sub.argtypes = [fdl_point_f64_t, fdl_point_f64_t]
    lib.fdl_point_sub.restype = fdl_point_f64_t

    # Resolve dimensions and anchor directly from canvas/framing handles for a path.
    lib.fdl_resolve_geometry_layer.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.POINTER(fdl_dimensions_f64_t),
        ctypes.POINTER(fdl_point_f64_t),
    ]
    lib.fdl_resolve_geometry_layer.restype = ctypes.c_int

    # Round a single value according to FDL rounding rules.
    lib.fdl_round.argtypes = [ctypes.c_double, ctypes.c_uint32, ctypes.c_uint32]
    lib.fdl_round.restype = ctypes.c_int64

    # Round dimensions according to FDL rounding rules.
    lib.fdl_round_dimensions.argtypes = [fdl_dimensions_f64_t, ctypes.c_uint32, ctypes.c_uint32]
    lib.fdl_round_dimensions.restype = fdl_dimensions_f64_t

    # Round a point according to FDL rounding rules.
    lib.fdl_round_point.argtypes = [fdl_point_f64_t, ctypes.c_uint32, ctypes.c_uint32]
    lib.fdl_round_point.restype = fdl_point_f64_t

    # Free a template result (doc + all allocated strings).
    lib.fdl_template_result_free.argtypes = [ctypes.POINTER(fdl_template_result_t)]
    lib.fdl_template_result_free.restype = None

    # Get a specific error message by index.
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

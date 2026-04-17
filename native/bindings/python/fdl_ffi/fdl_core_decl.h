// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0

#define FDL_TRUE 1
#define FDL_FALSE 0

#define FDL_DEFAULT_JSON_INDENT 2

typedef uint32_t fdl_custom_attr_type_t;
#define FDL_CUSTOM_ATTR_TYPE_NONE 0
#define FDL_CUSTOM_ATTR_TYPE_STRING 1
#define FDL_CUSTOM_ATTR_TYPE_INT 2
#define FDL_CUSTOM_ATTR_TYPE_FLOAT 3
#define FDL_CUSTOM_ATTR_TYPE_BOOL 4
#define FDL_CUSTOM_ATTR_TYPE_POINT_F64 5
#define FDL_CUSTOM_ATTR_TYPE_DIMS_F64 6
#define FDL_CUSTOM_ATTR_TYPE_DIMS_I64 7
#define FDL_CUSTOM_ATTR_TYPE_OTHER 8

typedef struct fdl_abi_version_t {
    uint64_t major;
    uint64_t minor;
    uint64_t patch;
} fdl_abi_version_t;

fdl_abi_version_t fdl_abi_version(void);

typedef struct fdl_dimensions_i64_t {
    int64_t width;
    int64_t height;
} fdl_dimensions_i64_t;

typedef struct fdl_dimensions_f64_t {
    double width;
    double height;
} fdl_dimensions_f64_t;

typedef struct fdl_point_f64_t {
    double x;
    double y;
} fdl_point_f64_t;

typedef struct fdl_rect_t {
    double x;
    double y;
    double width;
    double height;
} fdl_rect_t;

typedef uint64_t fdl_rounding_mode_t;
#define FDL_ROUNDING_MODE_UP 0
#define FDL_ROUNDING_MODE_DOWN 1
#define FDL_ROUNDING_MODE_ROUND 2

typedef uint64_t fdl_rounding_even_t;
#define FDL_ROUNDING_EVEN_WHOLE 0
#define FDL_ROUNDING_EVEN_EVEN 1

typedef uint32_t fdl_geometry_path_t;
#define FDL_GEOMETRY_PATH_CANVAS_DIMENSIONS 0
#define FDL_GEOMETRY_PATH_CANVAS_EFFECTIVE_DIMENSIONS 1
#define FDL_GEOMETRY_PATH_FRAMING_PROTECTION_DIMENSIONS 2
#define FDL_GEOMETRY_PATH_FRAMING_DIMENSIONS 3

typedef uint32_t fdl_fit_method_t;
#define FDL_FIT_METHOD_WIDTH 0
#define FDL_FIT_METHOD_HEIGHT 1
#define FDL_FIT_METHOD_FIT_ALL 2
#define FDL_FIT_METHOD_FILL 3

typedef uint32_t fdl_halign_t;
#define FDL_HALIGN_LEFT 0
#define FDL_HALIGN_CENTER 1
#define FDL_HALIGN_RIGHT 2

typedef uint32_t fdl_valign_t;
#define FDL_VALIGN_TOP 0
#define FDL_VALIGN_CENTER 1
#define FDL_VALIGN_BOTTOM 2

typedef struct fdl_geometry_t {
    fdl_dimensions_f64_t canvas_dims;
    fdl_dimensions_f64_t effective_dims;
    fdl_dimensions_f64_t protection_dims;
    fdl_dimensions_f64_t framing_dims;
    fdl_point_f64_t effective_anchor;
    fdl_point_f64_t protection_anchor;
    fdl_point_f64_t framing_anchor;
} fdl_geometry_t;

typedef struct fdl_round_strategy_t {
    fdl_rounding_even_t even;
    fdl_rounding_mode_t mode;
} fdl_round_strategy_t;

typedef struct fdl_from_intent_result_t {
    fdl_dimensions_f64_t dimensions;
    fdl_point_f64_t anchor_point;
    int has_protection;
    fdl_dimensions_f64_t protection_dimensions;
    fdl_point_f64_t protection_anchor_point;
} fdl_from_intent_result_t;

int64_t fdl_round(double value, fdl_rounding_even_t even, fdl_rounding_mode_t mode);

fdl_dimensions_f64_t
fdl_round_dimensions(fdl_dimensions_f64_t dims, fdl_rounding_even_t even, fdl_rounding_mode_t mode);

fdl_point_f64_t fdl_round_point(fdl_point_f64_t point, fdl_rounding_even_t even, fdl_rounding_mode_t mode);

fdl_dimensions_f64_t fdl_dimensions_normalize(fdl_dimensions_f64_t dims, double squeeze);

fdl_dimensions_f64_t
fdl_dimensions_scale(fdl_dimensions_f64_t dims, double scale_factor, double target_squeeze);

fdl_dimensions_f64_t fdl_dimensions_normalize_and_scale(
    fdl_dimensions_f64_t dims, double input_squeeze, double scale_factor, double target_squeeze);

fdl_dimensions_f64_t fdl_dimensions_sub(fdl_dimensions_f64_t a, fdl_dimensions_f64_t b);

int fdl_dimensions_equal(fdl_dimensions_f64_t a, fdl_dimensions_f64_t b);

int fdl_dimensions_f64_gt(fdl_dimensions_f64_t a, fdl_dimensions_f64_t b);

int fdl_dimensions_f64_lt(fdl_dimensions_f64_t a, fdl_dimensions_f64_t b);

int fdl_dimensions_is_zero(fdl_dimensions_f64_t dims);

int fdl_dimensions_i64_is_zero(fdl_dimensions_i64_t dims);

fdl_dimensions_f64_t fdl_dimensions_i64_normalize(fdl_dimensions_i64_t dims, double squeeze);

fdl_dimensions_i64_t fdl_dimensions_f64_to_i64(fdl_dimensions_f64_t dims);

int fdl_dimensions_i64_gt(fdl_dimensions_i64_t a, fdl_dimensions_i64_t b);

int fdl_dimensions_i64_lt(fdl_dimensions_i64_t a, fdl_dimensions_i64_t b);

fdl_point_f64_t fdl_point_normalize(fdl_point_f64_t point, double squeeze);

fdl_point_f64_t fdl_point_scale(fdl_point_f64_t point, double scale_factor, double target_squeeze);

fdl_point_f64_t fdl_point_add(fdl_point_f64_t a, fdl_point_f64_t b);

fdl_point_f64_t fdl_point_sub(fdl_point_f64_t a, fdl_point_f64_t b);

fdl_point_f64_t fdl_point_mul_scalar(fdl_point_f64_t a, double scalar);

fdl_point_f64_t
fdl_point_clamp(fdl_point_f64_t point, double min_val, double max_val, int has_min, int has_max);

int fdl_point_is_zero(fdl_point_f64_t point);

fdl_point_f64_t
fdl_point_normalize_and_scale(fdl_point_f64_t point, double input_squeeze, double scale_factor, double target_squeeze);

int fdl_point_equal(fdl_point_f64_t a, fdl_point_f64_t b);

int fdl_point_f64_lt(fdl_point_f64_t a, fdl_point_f64_t b);

int fdl_point_f64_gt(fdl_point_f64_t a, fdl_point_f64_t b);

double fdl_fp_rel_tol(void);

double fdl_fp_abs_tol(void);

fdl_geometry_t fdl_geometry_fill_hierarchy_gaps(fdl_geometry_t geo, fdl_point_f64_t anchor_offset);

fdl_geometry_t
fdl_geometry_normalize_and_scale(fdl_geometry_t geo, double source_squeeze, double scale_factor, double target_squeeze);

fdl_geometry_t fdl_geometry_round(fdl_geometry_t geo, fdl_round_strategy_t strategy);

fdl_geometry_t fdl_geometry_apply_offset(
    fdl_geometry_t geo,
    fdl_point_f64_t offset,
    fdl_point_f64_t* theo_eff,
    fdl_point_f64_t* theo_prot,
    fdl_point_f64_t* theo_fram);

fdl_geometry_t
fdl_geometry_crop(fdl_geometry_t geo, fdl_point_f64_t theo_eff, fdl_point_f64_t theo_prot, fdl_point_f64_t theo_fram);

int fdl_geometry_get_dims_anchor_from_path(
    const fdl_geometry_t* geo, fdl_geometry_path_t path, fdl_dimensions_f64_t* out_dims, fdl_point_f64_t* out_anchor);

double fdl_calculate_scale_factor(
    fdl_dimensions_f64_t fit_norm, fdl_dimensions_f64_t target_norm, fdl_fit_method_t fit_method);

double fdl_output_size_for_axis(double canvas_size, double max_size, int has_max, int pad_to_max);

double fdl_alignment_shift(
    double fit_size,
    double fit_anchor,
    double output_size,
    double canvas_size,
    double target_size,
    int is_center,
    double align_factor,
    int pad_to_max);

fdl_dimensions_f64_t
fdl_dimensions_clamp_to_dims(fdl_dimensions_f64_t dims, fdl_dimensions_f64_t clamp_dims, fdl_point_f64_t* out_delta);

fdl_from_intent_result_t fdl_compute_framing_from_intent(
    fdl_dimensions_f64_t canvas_dims,
    fdl_dimensions_f64_t working_dims,
    double squeeze,
    fdl_dimensions_i64_t aspect_ratio,
    double protection,
    fdl_round_strategy_t rounding);

typedef struct fdl_doc fdl_doc_t;

typedef struct fdl_context fdl_context_t;
typedef struct fdl_canvas fdl_canvas_t;
typedef struct fdl_framing_decision fdl_framing_decision_t;
typedef struct fdl_framing_intent fdl_framing_intent_t;
typedef struct fdl_canvas_template fdl_canvas_template_t;
typedef struct fdl_clip_id fdl_clip_id_t;
typedef struct fdl_file_sequence fdl_file_sequence_t;

typedef struct fdl_parse_result_t {
    fdl_doc_t* doc;
    const char* error;
} fdl_parse_result_t;

fdl_doc_t* fdl_doc_create(void);

void fdl_doc_free(fdl_doc_t* doc);

fdl_parse_result_t fdl_doc_parse_json(const char* json_str, size_t json_len);

const char* fdl_doc_get_uuid(const fdl_doc_t* doc);

const char* fdl_doc_get_fdl_creator(const fdl_doc_t* doc);

const char* fdl_doc_get_default_framing_intent(const fdl_doc_t* doc);

int fdl_doc_get_version_major(const fdl_doc_t* doc);

int fdl_doc_get_version_minor(const fdl_doc_t* doc);

char* fdl_doc_to_json(const fdl_doc_t* doc, int indent);

char* fdl_context_to_json(const fdl_context_t* ctx, int indent);

char* fdl_canvas_to_json(const fdl_canvas_t* canvas, int indent);

char* fdl_framing_decision_to_json(const fdl_framing_decision_t* fd, int indent);

char* fdl_framing_intent_to_json(const fdl_framing_intent_t* fi, int indent);

char* fdl_canvas_template_to_json(const fdl_canvas_template_t* ct, int indent);

uint32_t fdl_doc_framing_intents_count(fdl_doc_t* doc);

fdl_framing_intent_t* fdl_doc_framing_intent_at(fdl_doc_t* doc, uint32_t index);

fdl_framing_intent_t* fdl_doc_framing_intent_find_by_id(fdl_doc_t* doc, const char* id);

uint32_t fdl_doc_contexts_count(fdl_doc_t* doc);

fdl_context_t* fdl_doc_context_at(fdl_doc_t* doc, uint32_t index);

fdl_context_t* fdl_doc_context_find_by_label(fdl_doc_t* doc, const char* label);

uint32_t fdl_doc_canvas_templates_count(fdl_doc_t* doc);

fdl_canvas_template_t* fdl_doc_canvas_template_at(fdl_doc_t* doc, uint32_t index);

fdl_canvas_template_t* fdl_doc_canvas_template_find_by_id(fdl_doc_t* doc, const char* id);

uint32_t fdl_context_canvases_count(const fdl_context_t* ctx);

fdl_canvas_t* fdl_context_canvas_at(fdl_context_t* ctx, uint32_t index);

fdl_canvas_t* fdl_context_find_canvas_by_id(fdl_context_t* ctx, const char* id);

uint32_t fdl_canvas_framing_decisions_count(const fdl_canvas_t* canvas);

fdl_framing_decision_t* fdl_canvas_framing_decision_at(fdl_canvas_t* canvas, uint32_t index);

fdl_framing_decision_t* fdl_canvas_find_framing_decision_by_id(fdl_canvas_t* canvas, const char* id);

const char* fdl_context_get_label(const fdl_context_t* ctx);

const char* fdl_context_get_context_creator(const fdl_context_t* ctx);

int fdl_context_has_clip_id(const fdl_context_t* ctx);

const char* fdl_context_get_clip_id(const fdl_context_t* ctx);

fdl_clip_id_t* fdl_context_clip_id(fdl_context_t* ctx);

const char* fdl_clip_id_get_clip_name(const fdl_clip_id_t* cid);

int fdl_clip_id_has_file(const fdl_clip_id_t* cid);

const char* fdl_clip_id_get_file(const fdl_clip_id_t* cid);

int fdl_clip_id_has_sequence(const fdl_clip_id_t* cid);

fdl_file_sequence_t* fdl_clip_id_sequence(fdl_clip_id_t* cid);

char* fdl_clip_id_to_json(const fdl_clip_id_t* cid, int indent);

const char* fdl_file_sequence_get_value(const fdl_file_sequence_t* seq);

const char* fdl_file_sequence_get_idx(const fdl_file_sequence_t* seq);

int64_t fdl_file_sequence_get_min(const fdl_file_sequence_t* seq);

int64_t fdl_file_sequence_get_max(const fdl_file_sequence_t* seq);

const char* fdl_canvas_get_label(const fdl_canvas_t* canvas);

const char* fdl_canvas_get_id(const fdl_canvas_t* canvas);

const char* fdl_canvas_get_source_canvas_id(const fdl_canvas_t* canvas);

fdl_dimensions_i64_t fdl_canvas_get_dimensions(const fdl_canvas_t* canvas);

int fdl_canvas_has_effective_dimensions(const fdl_canvas_t* canvas);

fdl_dimensions_i64_t fdl_canvas_get_effective_dimensions(const fdl_canvas_t* canvas);

fdl_point_f64_t fdl_canvas_get_effective_anchor_point(const fdl_canvas_t* canvas);

double fdl_canvas_get_anamorphic_squeeze(const fdl_canvas_t* canvas);

int fdl_canvas_has_photosite_dimensions(const fdl_canvas_t* canvas);

fdl_dimensions_i64_t fdl_canvas_get_photosite_dimensions(const fdl_canvas_t* canvas);

int fdl_canvas_has_physical_dimensions(const fdl_canvas_t* canvas);

fdl_dimensions_f64_t fdl_canvas_get_physical_dimensions(const fdl_canvas_t* canvas);

const char* fdl_framing_decision_get_label(const fdl_framing_decision_t* fd);

const char* fdl_framing_decision_get_id(const fdl_framing_decision_t* fd);

const char* fdl_framing_decision_get_framing_intent_id(const fdl_framing_decision_t* fd);

fdl_dimensions_f64_t fdl_framing_decision_get_dimensions(const fdl_framing_decision_t* fd);

fdl_point_f64_t fdl_framing_decision_get_anchor_point(const fdl_framing_decision_t* fd);

int fdl_framing_decision_has_protection(const fdl_framing_decision_t* fd);

fdl_dimensions_f64_t fdl_framing_decision_get_protection_dimensions(const fdl_framing_decision_t* fd);

fdl_point_f64_t fdl_framing_decision_get_protection_anchor_point(const fdl_framing_decision_t* fd);

const char* fdl_framing_intent_get_label(const fdl_framing_intent_t* fi);

const char* fdl_framing_intent_get_id(const fdl_framing_intent_t* fi);

fdl_dimensions_i64_t fdl_framing_intent_get_aspect_ratio(const fdl_framing_intent_t* fi);

double fdl_framing_intent_get_protection(const fdl_framing_intent_t* fi);

const char* fdl_canvas_template_get_label(const fdl_canvas_template_t* ct);

const char* fdl_canvas_template_get_id(const fdl_canvas_template_t* ct);

fdl_dimensions_i64_t fdl_canvas_template_get_target_dimensions(const fdl_canvas_template_t* ct);

double fdl_canvas_template_get_target_anamorphic_squeeze(const fdl_canvas_template_t* ct);

fdl_geometry_path_t fdl_canvas_template_get_fit_source(const fdl_canvas_template_t* ct);

fdl_fit_method_t fdl_canvas_template_get_fit_method(const fdl_canvas_template_t* ct);

fdl_halign_t fdl_canvas_template_get_alignment_method_horizontal(const fdl_canvas_template_t* ct);

fdl_valign_t fdl_canvas_template_get_alignment_method_vertical(const fdl_canvas_template_t* ct);

int fdl_canvas_template_has_preserve_from_source_canvas(const fdl_canvas_template_t* ct);

fdl_geometry_path_t fdl_canvas_template_get_preserve_from_source_canvas(const fdl_canvas_template_t* ct);

int fdl_canvas_template_has_maximum_dimensions(const fdl_canvas_template_t* ct);

fdl_dimensions_i64_t fdl_canvas_template_get_maximum_dimensions(const fdl_canvas_template_t* ct);

int fdl_canvas_template_get_pad_to_maximum(const fdl_canvas_template_t* ct);

int fdl_canvas_template_has_round(const fdl_canvas_template_t* ct);

fdl_round_strategy_t fdl_canvas_template_get_round(const fdl_canvas_template_t* ct);

int fdl_resolve_geometry_layer(
    const fdl_canvas_t* canvas,
    const fdl_framing_decision_t* framing,
    fdl_geometry_path_t path,
    fdl_dimensions_f64_t* out_dims,
    fdl_point_f64_t* out_anchor);

fdl_rect_t fdl_make_rect(double x, double y, double width, double height);

fdl_rect_t fdl_canvas_get_rect(const fdl_canvas_t* canvas);

int fdl_canvas_get_effective_rect(const fdl_canvas_t* canvas, fdl_rect_t* out_rect);

fdl_rect_t fdl_framing_decision_get_rect(const fdl_framing_decision_t* fd);

int fdl_framing_decision_get_protection_rect(const fdl_framing_decision_t* fd, fdl_rect_t* out_rect);

typedef struct fdl_template_result_t {
    fdl_doc_t* output_fdl;
    const char* context_label;
    const char* canvas_id;
    const char* framing_decision_id;
    const char* error;
} fdl_template_result_t;

fdl_template_result_t fdl_apply_canvas_template(
    const fdl_canvas_template_t* tmpl,
    const fdl_canvas_t* source_canvas,
    const fdl_framing_decision_t* source_framing,
    const char* new_canvas_id,
    const char* new_fd_name,
    const char* source_context_label,
    const char* context_creator);

void fdl_template_result_free(fdl_template_result_t* result);

typedef struct fdl_resolve_canvas_result_t {
    fdl_canvas_t* canvas;
    fdl_framing_decision_t* framing_decision;
    int was_resolved;
    const char* error;
} fdl_resolve_canvas_result_t;

fdl_resolve_canvas_result_t fdl_context_resolve_canvas_for_dimensions(
    fdl_context_t* ctx, fdl_dimensions_f64_t input_dims, fdl_canvas_t* canvas, fdl_framing_decision_t* framing);

fdl_doc_t* fdl_doc_create_with_header(
    const char* uuid,
    int version_major,
    int version_minor,
    const char* fdl_creator,
    const char* default_framing_intent);

void fdl_doc_set_uuid(fdl_doc_t* doc, const char* uuid);

void fdl_doc_set_fdl_creator(fdl_doc_t* doc, const char* creator);

void fdl_doc_set_default_framing_intent(fdl_doc_t* doc, const char* fi_id);

void fdl_doc_set_version(fdl_doc_t* doc, int major, int minor);

fdl_framing_intent_t* fdl_doc_add_framing_intent(
    fdl_doc_t* doc, const char* id, const char* label, int64_t aspect_w, int64_t aspect_h, double protection);

fdl_context_t* fdl_doc_add_context(fdl_doc_t* doc, const char* label, const char* context_creator);

fdl_canvas_t* fdl_context_add_canvas(
    fdl_context_t* ctx,
    const char* id,
    const char* label,
    const char* source_canvas_id,
    int64_t dim_w,
    int64_t dim_h,
    double squeeze);

void fdl_canvas_set_effective_dimensions(
    fdl_canvas_t* canvas, fdl_dimensions_i64_t dims, fdl_point_f64_t anchor);

void fdl_canvas_set_photosite_dimensions(fdl_canvas_t* canvas, fdl_dimensions_i64_t dims);

void fdl_canvas_set_physical_dimensions(fdl_canvas_t* canvas, fdl_dimensions_f64_t dims);

fdl_framing_decision_t* fdl_canvas_add_framing_decision(
    fdl_canvas_t* canvas,
    const char* id,
    const char* label,
    const char* framing_intent_id,
    double dim_w,
    double dim_h,
    double anchor_x,
    double anchor_y);

fdl_canvas_template_t* fdl_doc_add_canvas_template(
    fdl_doc_t* doc,
    const char* id,
    const char* label,
    int64_t target_w,
    int64_t target_h,
    double target_squeeze,
    fdl_geometry_path_t fit_source,
    fdl_fit_method_t fit_method,
    fdl_halign_t halign,
    fdl_valign_t valign,
    fdl_round_strategy_t rounding);

void fdl_canvas_template_set_preserve_from_source_canvas(fdl_canvas_template_t* ct, fdl_geometry_path_t path);

void fdl_canvas_template_set_maximum_dimensions(fdl_canvas_template_t* ct, fdl_dimensions_i64_t dims);

void fdl_canvas_template_set_pad_to_maximum(fdl_canvas_template_t* ct, int pad);

void fdl_framing_decision_set_protection(
    fdl_framing_decision_t* fd, fdl_dimensions_f64_t dims, fdl_point_f64_t anchor);

void fdl_framing_intent_set_aspect_ratio(fdl_framing_intent_t* fi, fdl_dimensions_i64_t dims);

void fdl_framing_intent_set_protection(fdl_framing_intent_t* fi, double protection);

void fdl_canvas_set_dimensions(fdl_canvas_t* canvas, fdl_dimensions_i64_t dims);

void fdl_canvas_set_anamorphic_squeeze(fdl_canvas_t* canvas, double squeeze);

void fdl_canvas_set_effective_dims_only(fdl_canvas_t* canvas, fdl_dimensions_i64_t dims);

void fdl_canvas_remove_effective(fdl_canvas_t* canvas);

void fdl_framing_decision_set_dimensions(fdl_framing_decision_t* fd, fdl_dimensions_f64_t dims);

void fdl_framing_decision_set_anchor_point(fdl_framing_decision_t* fd, fdl_point_f64_t point);

void fdl_framing_decision_set_protection_dimensions(fdl_framing_decision_t* fd, fdl_dimensions_f64_t dims);

void fdl_framing_decision_set_protection_anchor_point(fdl_framing_decision_t* fd, fdl_point_f64_t point);

void fdl_framing_decision_remove_protection(fdl_framing_decision_t* fd);

void fdl_framing_decision_adjust_anchor(
    fdl_framing_decision_t* fd, const fdl_canvas_t* canvas, fdl_halign_t h_align, fdl_valign_t v_align);

void fdl_framing_decision_adjust_protection_anchor(
    fdl_framing_decision_t* fd, const fdl_canvas_t* canvas, fdl_halign_t h_align, fdl_valign_t v_align);

void fdl_framing_decision_populate_from_intent(
    fdl_framing_decision_t* fd,
    const fdl_canvas_t* canvas,
    const fdl_framing_intent_t* intent,
    fdl_round_strategy_t rounding);

const char* fdl_context_set_clip_id_json(fdl_context_t* ctx, const char* json_str, size_t json_len);

void fdl_context_remove_clip_id(fdl_context_t* ctx);

const char* fdl_clip_id_validate_json(const char* json_str, size_t json_len);

typedef struct fdl_validation_result fdl_validation_result_t;

fdl_validation_result_t* fdl_doc_validate(const fdl_doc_t* doc);

uint32_t fdl_validation_result_error_count(const fdl_validation_result_t* result);

const char* fdl_validation_result_error_at(const fdl_validation_result_t* result, uint32_t index);

void fdl_validation_result_free(fdl_validation_result_t* result);

void fdl_free(void* ptr);

/* Custom attribute functions (expanded from FDL_CUSTOM_ATTR_DECL macro) */
int fdl_doc_set_custom_attr_string(fdl_doc_t* h, const char* name, const char* value);
int fdl_doc_set_custom_attr_int(fdl_doc_t* h, const char* name, int64_t value);
int fdl_doc_set_custom_attr_float(fdl_doc_t* h, const char* name, double value);
int fdl_doc_set_custom_attr_bool(fdl_doc_t* h, const char* name, int value);
const char* fdl_doc_get_custom_attr_string(const fdl_doc_t* h, const char* name);
int fdl_doc_get_custom_attr_int(const fdl_doc_t* h, const char* name, int64_t* out);
int fdl_doc_get_custom_attr_float(const fdl_doc_t* h, const char* name, double* out);
int fdl_doc_get_custom_attr_bool(const fdl_doc_t* h, const char* name, int* out);
int fdl_doc_has_custom_attr(const fdl_doc_t* h, const char* name);
uint32_t fdl_doc_get_custom_attr_type(const fdl_doc_t* h, const char* name);
int fdl_doc_remove_custom_attr(fdl_doc_t* h, const char* name);
uint32_t fdl_doc_custom_attrs_count(const fdl_doc_t* h);
const char* fdl_doc_custom_attr_name_at(const fdl_doc_t* h, uint32_t index);
int fdl_doc_set_custom_attr_point_f64(fdl_doc_t* h, const char* name, fdl_point_f64_t value);
int fdl_doc_get_custom_attr_point_f64(const fdl_doc_t* h, const char* name, fdl_point_f64_t* out);
int fdl_doc_set_custom_attr_dims_f64(fdl_doc_t* h, const char* name, fdl_dimensions_f64_t value);
int fdl_doc_get_custom_attr_dims_f64(const fdl_doc_t* h, const char* name, fdl_dimensions_f64_t* out);
int fdl_doc_set_custom_attr_dims_i64(fdl_doc_t* h, const char* name, fdl_dimensions_i64_t value);
int fdl_doc_get_custom_attr_dims_i64(const fdl_doc_t* h, const char* name, fdl_dimensions_i64_t* out);
int fdl_context_set_custom_attr_string(fdl_context_t* h, const char* name, const char* value);
int fdl_context_set_custom_attr_int(fdl_context_t* h, const char* name, int64_t value);
int fdl_context_set_custom_attr_float(fdl_context_t* h, const char* name, double value);
int fdl_context_set_custom_attr_bool(fdl_context_t* h, const char* name, int value);
const char* fdl_context_get_custom_attr_string(const fdl_context_t* h, const char* name);
int fdl_context_get_custom_attr_int(const fdl_context_t* h, const char* name, int64_t* out);
int fdl_context_get_custom_attr_float(const fdl_context_t* h, const char* name, double* out);
int fdl_context_get_custom_attr_bool(const fdl_context_t* h, const char* name, int* out);
int fdl_context_has_custom_attr(const fdl_context_t* h, const char* name);
uint32_t fdl_context_get_custom_attr_type(const fdl_context_t* h, const char* name);
int fdl_context_remove_custom_attr(fdl_context_t* h, const char* name);
uint32_t fdl_context_custom_attrs_count(const fdl_context_t* h);
const char* fdl_context_custom_attr_name_at(const fdl_context_t* h, uint32_t index);
int fdl_context_set_custom_attr_point_f64(fdl_context_t* h, const char* name, fdl_point_f64_t value);
int fdl_context_get_custom_attr_point_f64(const fdl_context_t* h, const char* name, fdl_point_f64_t* out);
int fdl_context_set_custom_attr_dims_f64(fdl_context_t* h, const char* name, fdl_dimensions_f64_t value);
int fdl_context_get_custom_attr_dims_f64(const fdl_context_t* h, const char* name, fdl_dimensions_f64_t* out);
int fdl_context_set_custom_attr_dims_i64(fdl_context_t* h, const char* name, fdl_dimensions_i64_t value);
int fdl_context_get_custom_attr_dims_i64(const fdl_context_t* h, const char* name, fdl_dimensions_i64_t* out);
int fdl_canvas_set_custom_attr_string(fdl_canvas_t* h, const char* name, const char* value);
int fdl_canvas_set_custom_attr_int(fdl_canvas_t* h, const char* name, int64_t value);
int fdl_canvas_set_custom_attr_float(fdl_canvas_t* h, const char* name, double value);
int fdl_canvas_set_custom_attr_bool(fdl_canvas_t* h, const char* name, int value);
const char* fdl_canvas_get_custom_attr_string(const fdl_canvas_t* h, const char* name);
int fdl_canvas_get_custom_attr_int(const fdl_canvas_t* h, const char* name, int64_t* out);
int fdl_canvas_get_custom_attr_float(const fdl_canvas_t* h, const char* name, double* out);
int fdl_canvas_get_custom_attr_bool(const fdl_canvas_t* h, const char* name, int* out);
int fdl_canvas_has_custom_attr(const fdl_canvas_t* h, const char* name);
uint32_t fdl_canvas_get_custom_attr_type(const fdl_canvas_t* h, const char* name);
int fdl_canvas_remove_custom_attr(fdl_canvas_t* h, const char* name);
uint32_t fdl_canvas_custom_attrs_count(const fdl_canvas_t* h);
const char* fdl_canvas_custom_attr_name_at(const fdl_canvas_t* h, uint32_t index);
int fdl_canvas_set_custom_attr_point_f64(fdl_canvas_t* h, const char* name, fdl_point_f64_t value);
int fdl_canvas_get_custom_attr_point_f64(const fdl_canvas_t* h, const char* name, fdl_point_f64_t* out);
int fdl_canvas_set_custom_attr_dims_f64(fdl_canvas_t* h, const char* name, fdl_dimensions_f64_t value);
int fdl_canvas_get_custom_attr_dims_f64(const fdl_canvas_t* h, const char* name, fdl_dimensions_f64_t* out);
int fdl_canvas_set_custom_attr_dims_i64(fdl_canvas_t* h, const char* name, fdl_dimensions_i64_t value);
int fdl_canvas_get_custom_attr_dims_i64(const fdl_canvas_t* h, const char* name, fdl_dimensions_i64_t* out);
int fdl_framing_decision_set_custom_attr_string(fdl_framing_decision_t* h, const char* name, const char* value);
int fdl_framing_decision_set_custom_attr_int(fdl_framing_decision_t* h, const char* name, int64_t value);
int fdl_framing_decision_set_custom_attr_float(fdl_framing_decision_t* h, const char* name, double value);
int fdl_framing_decision_set_custom_attr_bool(fdl_framing_decision_t* h, const char* name, int value);
const char* fdl_framing_decision_get_custom_attr_string(const fdl_framing_decision_t* h, const char* name);
int fdl_framing_decision_get_custom_attr_int(const fdl_framing_decision_t* h, const char* name, int64_t* out);
int fdl_framing_decision_get_custom_attr_float(const fdl_framing_decision_t* h, const char* name, double* out);
int fdl_framing_decision_get_custom_attr_bool(const fdl_framing_decision_t* h, const char* name, int* out);
int fdl_framing_decision_has_custom_attr(const fdl_framing_decision_t* h, const char* name);
uint32_t fdl_framing_decision_get_custom_attr_type(const fdl_framing_decision_t* h, const char* name);
int fdl_framing_decision_remove_custom_attr(fdl_framing_decision_t* h, const char* name);
uint32_t fdl_framing_decision_custom_attrs_count(const fdl_framing_decision_t* h);
const char* fdl_framing_decision_custom_attr_name_at(const fdl_framing_decision_t* h, uint32_t index);
int fdl_framing_decision_set_custom_attr_point_f64(fdl_framing_decision_t* h, const char* name, fdl_point_f64_t value);
int fdl_framing_decision_get_custom_attr_point_f64(const fdl_framing_decision_t* h, const char* name, fdl_point_f64_t* out);
int fdl_framing_decision_set_custom_attr_dims_f64(fdl_framing_decision_t* h, const char* name, fdl_dimensions_f64_t value);
int fdl_framing_decision_get_custom_attr_dims_f64(const fdl_framing_decision_t* h, const char* name, fdl_dimensions_f64_t* out);
int fdl_framing_decision_set_custom_attr_dims_i64(fdl_framing_decision_t* h, const char* name, fdl_dimensions_i64_t value);
int fdl_framing_decision_get_custom_attr_dims_i64(const fdl_framing_decision_t* h, const char* name, fdl_dimensions_i64_t* out);
int fdl_framing_intent_set_custom_attr_string(fdl_framing_intent_t* h, const char* name, const char* value);
int fdl_framing_intent_set_custom_attr_int(fdl_framing_intent_t* h, const char* name, int64_t value);
int fdl_framing_intent_set_custom_attr_float(fdl_framing_intent_t* h, const char* name, double value);
int fdl_framing_intent_set_custom_attr_bool(fdl_framing_intent_t* h, const char* name, int value);
const char* fdl_framing_intent_get_custom_attr_string(const fdl_framing_intent_t* h, const char* name);
int fdl_framing_intent_get_custom_attr_int(const fdl_framing_intent_t* h, const char* name, int64_t* out);
int fdl_framing_intent_get_custom_attr_float(const fdl_framing_intent_t* h, const char* name, double* out);
int fdl_framing_intent_get_custom_attr_bool(const fdl_framing_intent_t* h, const char* name, int* out);
int fdl_framing_intent_has_custom_attr(const fdl_framing_intent_t* h, const char* name);
uint32_t fdl_framing_intent_get_custom_attr_type(const fdl_framing_intent_t* h, const char* name);
int fdl_framing_intent_remove_custom_attr(fdl_framing_intent_t* h, const char* name);
uint32_t fdl_framing_intent_custom_attrs_count(const fdl_framing_intent_t* h);
const char* fdl_framing_intent_custom_attr_name_at(const fdl_framing_intent_t* h, uint32_t index);
int fdl_framing_intent_set_custom_attr_point_f64(fdl_framing_intent_t* h, const char* name, fdl_point_f64_t value);
int fdl_framing_intent_get_custom_attr_point_f64(const fdl_framing_intent_t* h, const char* name, fdl_point_f64_t* out);
int fdl_framing_intent_set_custom_attr_dims_f64(fdl_framing_intent_t* h, const char* name, fdl_dimensions_f64_t value);
int fdl_framing_intent_get_custom_attr_dims_f64(const fdl_framing_intent_t* h, const char* name, fdl_dimensions_f64_t* out);
int fdl_framing_intent_set_custom_attr_dims_i64(fdl_framing_intent_t* h, const char* name, fdl_dimensions_i64_t value);
int fdl_framing_intent_get_custom_attr_dims_i64(const fdl_framing_intent_t* h, const char* name, fdl_dimensions_i64_t* out);
int fdl_canvas_template_set_custom_attr_string(fdl_canvas_template_t* h, const char* name, const char* value);
int fdl_canvas_template_set_custom_attr_int(fdl_canvas_template_t* h, const char* name, int64_t value);
int fdl_canvas_template_set_custom_attr_float(fdl_canvas_template_t* h, const char* name, double value);
int fdl_canvas_template_set_custom_attr_bool(fdl_canvas_template_t* h, const char* name, int value);
const char* fdl_canvas_template_get_custom_attr_string(const fdl_canvas_template_t* h, const char* name);
int fdl_canvas_template_get_custom_attr_int(const fdl_canvas_template_t* h, const char* name, int64_t* out);
int fdl_canvas_template_get_custom_attr_float(const fdl_canvas_template_t* h, const char* name, double* out);
int fdl_canvas_template_get_custom_attr_bool(const fdl_canvas_template_t* h, const char* name, int* out);
int fdl_canvas_template_has_custom_attr(const fdl_canvas_template_t* h, const char* name);
uint32_t fdl_canvas_template_get_custom_attr_type(const fdl_canvas_template_t* h, const char* name);
int fdl_canvas_template_remove_custom_attr(fdl_canvas_template_t* h, const char* name);
uint32_t fdl_canvas_template_custom_attrs_count(const fdl_canvas_template_t* h);
const char* fdl_canvas_template_custom_attr_name_at(const fdl_canvas_template_t* h, uint32_t index);
int fdl_canvas_template_set_custom_attr_point_f64(fdl_canvas_template_t* h, const char* name, fdl_point_f64_t value);
int fdl_canvas_template_get_custom_attr_point_f64(const fdl_canvas_template_t* h, const char* name, fdl_point_f64_t* out);
int fdl_canvas_template_set_custom_attr_dims_f64(fdl_canvas_template_t* h, const char* name, fdl_dimensions_f64_t value);
int fdl_canvas_template_get_custom_attr_dims_f64(const fdl_canvas_template_t* h, const char* name, fdl_dimensions_f64_t* out);
int fdl_canvas_template_set_custom_attr_dims_i64(fdl_canvas_template_t* h, const char* name, fdl_dimensions_i64_t value);
int fdl_canvas_template_get_custom_attr_dims_i64(const fdl_canvas_template_t* h, const char* name, fdl_dimensions_i64_t* out);
int fdl_clip_id_set_custom_attr_string(fdl_clip_id_t* h, const char* name, const char* value);
int fdl_clip_id_set_custom_attr_int(fdl_clip_id_t* h, const char* name, int64_t value);
int fdl_clip_id_set_custom_attr_float(fdl_clip_id_t* h, const char* name, double value);
int fdl_clip_id_set_custom_attr_bool(fdl_clip_id_t* h, const char* name, int value);
const char* fdl_clip_id_get_custom_attr_string(const fdl_clip_id_t* h, const char* name);
int fdl_clip_id_get_custom_attr_int(const fdl_clip_id_t* h, const char* name, int64_t* out);
int fdl_clip_id_get_custom_attr_float(const fdl_clip_id_t* h, const char* name, double* out);
int fdl_clip_id_get_custom_attr_bool(const fdl_clip_id_t* h, const char* name, int* out);
int fdl_clip_id_has_custom_attr(const fdl_clip_id_t* h, const char* name);
uint32_t fdl_clip_id_get_custom_attr_type(const fdl_clip_id_t* h, const char* name);
int fdl_clip_id_remove_custom_attr(fdl_clip_id_t* h, const char* name);
uint32_t fdl_clip_id_custom_attrs_count(const fdl_clip_id_t* h);
const char* fdl_clip_id_custom_attr_name_at(const fdl_clip_id_t* h, uint32_t index);
int fdl_clip_id_set_custom_attr_point_f64(fdl_clip_id_t* h, const char* name, fdl_point_f64_t value);
int fdl_clip_id_get_custom_attr_point_f64(const fdl_clip_id_t* h, const char* name, fdl_point_f64_t* out);
int fdl_clip_id_set_custom_attr_dims_f64(fdl_clip_id_t* h, const char* name, fdl_dimensions_f64_t value);
int fdl_clip_id_get_custom_attr_dims_f64(const fdl_clip_id_t* h, const char* name, fdl_dimensions_f64_t* out);
int fdl_clip_id_set_custom_attr_dims_i64(fdl_clip_id_t* h, const char* name, fdl_dimensions_i64_t value);
int fdl_clip_id_get_custom_attr_dims_i64(const fdl_clip_id_t* h, const char* name, fdl_dimensions_i64_t* out);
int fdl_file_sequence_set_custom_attr_string(fdl_file_sequence_t* h, const char* name, const char* value);
int fdl_file_sequence_set_custom_attr_int(fdl_file_sequence_t* h, const char* name, int64_t value);
int fdl_file_sequence_set_custom_attr_float(fdl_file_sequence_t* h, const char* name, double value);
int fdl_file_sequence_set_custom_attr_bool(fdl_file_sequence_t* h, const char* name, int value);
const char* fdl_file_sequence_get_custom_attr_string(const fdl_file_sequence_t* h, const char* name);
int fdl_file_sequence_get_custom_attr_int(const fdl_file_sequence_t* h, const char* name, int64_t* out);
int fdl_file_sequence_get_custom_attr_float(const fdl_file_sequence_t* h, const char* name, double* out);
int fdl_file_sequence_get_custom_attr_bool(const fdl_file_sequence_t* h, const char* name, int* out);
int fdl_file_sequence_has_custom_attr(const fdl_file_sequence_t* h, const char* name);
uint32_t fdl_file_sequence_get_custom_attr_type(const fdl_file_sequence_t* h, const char* name);
int fdl_file_sequence_remove_custom_attr(fdl_file_sequence_t* h, const char* name);
uint32_t fdl_file_sequence_custom_attrs_count(const fdl_file_sequence_t* h);
const char* fdl_file_sequence_custom_attr_name_at(const fdl_file_sequence_t* h, uint32_t index);
int fdl_file_sequence_set_custom_attr_point_f64(fdl_file_sequence_t* h, const char* name, fdl_point_f64_t value);
int fdl_file_sequence_get_custom_attr_point_f64(const fdl_file_sequence_t* h, const char* name, fdl_point_f64_t* out);
int fdl_file_sequence_set_custom_attr_dims_f64(fdl_file_sequence_t* h, const char* name, fdl_dimensions_f64_t value);
int fdl_file_sequence_get_custom_attr_dims_f64(const fdl_file_sequence_t* h, const char* name, fdl_dimensions_f64_t* out);
int fdl_file_sequence_set_custom_attr_dims_i64(fdl_file_sequence_t* h, const char* name, fdl_dimensions_i64_t value);
int fdl_file_sequence_get_custom_attr_dims_i64(const fdl_file_sequence_t* h, const char* name, fdl_dimensions_i64_t* out);

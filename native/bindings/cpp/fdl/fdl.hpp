// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
// AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
/**
 * @file fdl.hpp
 * @brief Header-only C++ RAII wrappers around the fdl_core C ABI.
 *
 * Provides move-only RAII FDL ownership and non-owning handle Refs
 * for convenient FDL document traversal from C++ consumers.
 *
 * Usage:
 *   #include "fdl/fdl.hpp"
 *
 *   auto doc = fdl::read_from_file("my_document.fdl");
 *   for (uint32_t i = 0; i < doc.contexts_count(); ++i) {
 *       auto ctx = doc.context_at(i);
 *       // ...
 *   }
 *   fdl::write_to_file(doc, "output.fdl");
 */

#ifndef FDL_HPP
#define FDL_HPP

#include "fdl/fdl_core.h"

#include <cstdint>
#include <fstream>
#include <iterator>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace fdl {

// -----------------------------------------------------------------------
// First-class custom attribute name constants
// -----------------------------------------------------------------------

/** Custom attribute name for the template scale factor (float). */
inline constexpr const char* ATTR_SCALE_FACTOR = FDL_ATTR_SCALE_FACTOR;
/** Custom attribute name for the template content translation (point_f64). */
inline constexpr const char* ATTR_CONTENT_TRANSLATION = FDL_ATTR_CONTENT_TRANSLATION;
/** Custom attribute name for the template scaled bounding box (dims_f64). */
inline constexpr const char* ATTR_SCALED_BOUNDING_BOX = FDL_ATTR_SCALED_BOUNDING_BOX;

// -----------------------------------------------------------------------
// Value type wrapper classes
// -----------------------------------------------------------------------

// Forward declarations for cross-type references in deferred methods
class DimensionsInt;
class DimensionsFloat;
class PointFloat;
class Rect;

class DimensionsInt {
public:
    DimensionsInt() : data_{} {}
    DimensionsInt(int64_t width, int64_t height) : data_{width, height} {}
    DimensionsInt(fdl_dimensions_i64_t raw) : data_(raw) {}
    operator fdl_dimensions_i64_t() const { return data_; }

    int64_t width() const { return data_.width; }
    int64_t height() const { return data_.height; }

    bool is_zero() const { return ::fdl_dimensions_i64_is_zero(data_) != 0; }

    std::string format() const {
        std::ostringstream ss;
        ss << data_.width << "x" << data_.height;
        return ss.str();
    }

    DimensionsFloat normalize(double squeeze) const;
    bool operator>(const DimensionsInt& other) const { return ::fdl_dimensions_i64_gt(data_, other.data_) != 0; }
    bool operator<(const DimensionsInt& other) const { return ::fdl_dimensions_i64_lt(data_, other.data_) != 0; }
    explicit operator bool() const { return !is_zero(); }
    bool operator==(const DimensionsInt& other) const {
        return data_.width == other.data_.width && data_.height == other.data_.height;
    }
    bool operator!=(const DimensionsInt& other) const { return !(*this == other); }
    bool operator==(const DimensionsFloat& other) const;
    bool operator!=(const DimensionsFloat& other) const { return !(*this == other); }

    fdl_dimensions_i64_t raw() const { return data_; }

private:
    fdl_dimensions_i64_t data_;
};

class DimensionsFloat {
public:
    DimensionsFloat() : data_{} {}
    DimensionsFloat(double width, double height) : data_{width, height} {}
    DimensionsFloat(fdl_dimensions_f64_t raw) : data_(raw) {}
    operator fdl_dimensions_f64_t() const { return data_; }

    double width() const { return data_.width; }
    double height() const { return data_.height; }

    bool is_zero() const { return ::fdl_dimensions_is_zero(data_) != 0; }

    DimensionsFloat normalize(double squeeze) const {
        return DimensionsFloat(::fdl_dimensions_normalize(data_, squeeze));
    }

    DimensionsFloat scale(double scale_factor, double target_squeeze) const {
        return DimensionsFloat(::fdl_dimensions_scale(data_, scale_factor, target_squeeze));
    }

    DimensionsFloat normalize_and_scale(double input_squeeze, double scale_factor, double target_squeeze) const {
        return DimensionsFloat(
            ::fdl_dimensions_normalize_and_scale(data_, input_squeeze, scale_factor, target_squeeze));
    }

    DimensionsFloat round(fdl_rounding_even_t even, fdl_rounding_mode_t mode) const {
        return DimensionsFloat(::fdl_round_dimensions(data_, even, mode));
    }

    std::string format() const {
        std::ostringstream ss;
        ss << data_.width << "x" << data_.height;
        return ss.str();
    }

    DimensionsInt to_int() const {
        return DimensionsInt(static_cast<int64_t>(data_.width), static_cast<int64_t>(data_.height));
    }

    void scale_by(double factor) {
        data_.width *= factor;
        data_.height *= factor;
    }

    std::pair<DimensionsFloat, PointFloat> clamp_to_dims(const DimensionsFloat& clamp_dims) const;
    DimensionsFloat operator-(const DimensionsFloat& other) const {
        return DimensionsFloat(::fdl_dimensions_sub(data_, other.data_));
    }
    bool operator<(const DimensionsFloat& other) const { return ::fdl_dimensions_f64_lt(data_, other.data_) != 0; }
    bool operator>(const DimensionsFloat& other) const { return ::fdl_dimensions_f64_gt(data_, other.data_) != 0; }
    explicit operator bool() const { return !is_zero(); }
    bool operator==(const DimensionsFloat& other) const { return ::fdl_dimensions_equal(data_, other.data_) != 0; }
    bool operator!=(const DimensionsFloat& other) const { return !(*this == other); }
    bool operator==(const DimensionsInt& other) const;
    bool operator!=(const DimensionsInt& other) const { return !(*this == other); }

    fdl_dimensions_f64_t raw() const { return data_; }

private:
    fdl_dimensions_f64_t data_;
};

class PointFloat {
public:
    PointFloat() : data_{} {}
    PointFloat(double x, double y) : data_{x, y} {}
    PointFloat(fdl_point_f64_t raw) : data_(raw) {}
    operator fdl_point_f64_t() const { return data_; }

    double x() const { return data_.x; }
    double y() const { return data_.y; }

    bool is_zero() const { return ::fdl_point_is_zero(data_) != 0; }

    PointFloat normalize(double squeeze) const { return PointFloat(::fdl_point_normalize(data_, squeeze)); }

    PointFloat scale(double scale_factor, double target_squeeze) const {
        return PointFloat(::fdl_point_scale(data_, scale_factor, target_squeeze));
    }

    PointFloat normalize_and_scale(double input_squeeze, double scale_factor, double target_squeeze) const {
        return PointFloat(::fdl_point_normalize_and_scale(data_, input_squeeze, scale_factor, target_squeeze));
    }

    PointFloat clamp(std::optional<double> min_val = std::nullopt, std::optional<double> max_val = std::nullopt) const {
        return PointFloat(::fdl_point_clamp(
            data_,
            min_val.value_or(0.0),
            max_val.value_or(0.0),
            min_val.has_value() ? 1 : 0,
            max_val.has_value() ? 1 : 0));
    }

    PointFloat round(fdl_rounding_even_t even, fdl_rounding_mode_t mode) const {
        return PointFloat(::fdl_round_point(data_, even, mode));
    }

    std::string format() const {
        std::ostringstream ss;
        ss << data_.x << "x" << data_.y;
        return ss.str();
    }

    PointFloat operator+(const PointFloat& other) const { return PointFloat(::fdl_point_add(data_, other.data_)); }
    PointFloat& operator+=(const PointFloat& other) {
        data_.x += other.data_.x;
        data_.y += other.data_.y;
        return *this;
    }
    PointFloat operator-(const PointFloat& other) const { return PointFloat(::fdl_point_sub(data_, other.data_)); }
    PointFloat operator*(double scalar) const { return PointFloat(::fdl_point_mul_scalar(data_, scalar)); }
    PointFloat operator*(const PointFloat& other) const {
        return PointFloat(data_.x * other.data_.x, data_.y * other.data_.y);
    }
    bool operator<(const PointFloat& other) const { return ::fdl_point_f64_lt(data_, other.data_) != 0; }
    bool operator>(const PointFloat& other) const { return ::fdl_point_f64_gt(data_, other.data_) != 0; }
    bool operator==(const PointFloat& other) const { return ::fdl_point_equal(data_, other.data_) != 0; }
    bool operator!=(const PointFloat& other) const { return !(*this == other); }

    fdl_point_f64_t raw() const { return data_; }

private:
    fdl_point_f64_t data_;
};

class Rect {
public:
    Rect() : data_{} {}
    Rect(double x, double y, double width, double height) : data_{x, y, width, height} {}
    Rect(fdl_rect_t raw) : data_(raw) {}
    operator fdl_rect_t() const { return data_; }

    double x() const { return data_.x; }
    double y() const { return data_.y; }
    double width() const { return data_.width; }
    double height() const { return data_.height; }

    bool operator==(const Rect& other) const {
        return data_.x == other.data_.x && data_.y == other.data_.y && data_.width == other.data_.width &&
               data_.height == other.data_.height;
    }
    bool operator!=(const Rect& other) const { return !(*this == other); }

    fdl_rect_t raw() const { return data_; }

private:
    fdl_rect_t data_;
};

// -----------------------------------------------------------------------
// Supporting structs
// -----------------------------------------------------------------------

struct Version {
    int major;
    int minor;
};

// -----------------------------------------------------------------------
// Forward declarations
// -----------------------------------------------------------------------
class FDL;
class ContextRef;
class CanvasRef;
class FramingDecisionRef;
class FramingIntentRef;
class CanvasTemplateRef;
class ClipIDRef;
class FileSequenceRef;
struct TemplateResult;
struct ResolveCanvasResult;

// -----------------------------------------------------------------------
// FDL — RAII owner of fdl_doc_t*
// -----------------------------------------------------------------------
class FDL {
public:
    FDL() noexcept : doc_(nullptr) {}

    explicit FDL(fdl_doc_t* handle) noexcept : doc_(handle) {}

    ~FDL() {
        if (doc_) {
            fdl_doc_free(doc_);
        }
    }

    // Move-only
    FDL(FDL&& other) noexcept : doc_(other.doc_) { other.doc_ = nullptr; }
    FDL& operator=(FDL&& other) noexcept {
        if (this != &other) {
            if (doc_) {
                fdl_doc_free(doc_);
            }
            doc_ = other.doc_;
            other.doc_ = nullptr;
        }
        return *this;
    }
    FDL(const FDL&) = delete;
    FDL& operator=(const FDL&) = delete;

    /** Raw pointer access (non-owning). */
    fdl_doc_t* get() const noexcept { return doc_; }

    explicit operator bool() const noexcept { return doc_ != nullptr; }

    // --- Property accessors ---
    std::string uuid() const {
        const char* p = fdl_doc_get_uuid(doc_);
        return p ? std::string(p) : std::string();
    }
    void set_uuid(const std::string& value) { fdl_doc_set_uuid(doc_, value.c_str()); }

    std::string fdl_creator() const {
        const char* p = fdl_doc_get_fdl_creator(doc_);
        return p ? std::string(p) : std::string();
    }
    void set_fdl_creator(const std::string& value) { fdl_doc_set_fdl_creator(doc_, value.c_str()); }

    std::string default_framing_intent() const {
        const char* p = fdl_doc_get_default_framing_intent(doc_);
        return p ? std::string(p) : std::string();
    }
    void set_default_framing_intent(const std::string& value) {
        fdl_doc_set_default_framing_intent(doc_, value.c_str());
    }

    int version_major() const { return fdl_doc_get_version_major(doc_); }

    int version_minor() const { return fdl_doc_get_version_minor(doc_); }

    // --- Collection traversal ---
    uint32_t contexts_count() const { return fdl_doc_contexts_count(doc_); }
    ContextRef context_at(uint32_t i) const;
    ContextRef context_find_by_label(const std::string& label) const;
    uint32_t framing_intents_count() const { return fdl_doc_framing_intents_count(doc_); }
    FramingIntentRef framing_intent_at(uint32_t i) const;
    FramingIntentRef framing_intent_find_by_id(const std::string& id) const;
    uint32_t canvas_templates_count() const { return fdl_doc_canvas_templates_count(doc_); }
    CanvasTemplateRef canvas_template_at(uint32_t i) const;
    CanvasTemplateRef canvas_template_find_by_id(const std::string& id) const;

    // --- Serialization ---

    /** Serialize to canonical JSON string. */
    std::string to_json(int indent = 2) const {
        char* ptr = fdl_doc_to_json(doc_, indent);
        if (!ptr) {
            throw std::runtime_error("fdl_doc_to_json returned NULL");
        }
        std::string json(ptr);
        fdl_free(ptr);
        return json;
    }

    // --- Lifecycle methods ---

    /** Parse JSON bytes into a facade FDL document. */
    static FDL parse(const std::string& json) {
        auto result = fdl_doc_parse_json(json.data(), json.size());
        if (result.error) {
            std::string msg(result.error);
            fdl_free(const_cast<char*>(result.error));
            throw std::runtime_error(msg);
        }
        return FDL(result.doc);
    }

    /** Create a new empty FDL document with header fields. */
    static FDL create(
        const std::string& uuid,
        int version_major = 2,
        int version_minor = 0,
        const std::string& fdl_creator = "",
        const std::string& default_framing_intent = "") {
        auto* handle = fdl_doc_create_with_header(
            uuid.c_str(),
            version_major,
            version_minor,
            fdl_creator.c_str(),
            default_framing_intent.empty() ? nullptr : default_framing_intent.c_str());
        if (!handle) {
            throw std::runtime_error("fdl_doc_create_with_header returned NULL");
        }
        return FDL(handle);
    }

    /** Run C-core schema + semantic validation. */
    std::vector<std::string> validate() const {
        std::vector<std::string> errors;
        auto* vr = fdl_doc_validate(doc_);
        uint32_t count = fdl_validation_result_error_count(vr);
        for (uint32_t i = 0; i < count; ++i) {
            const char* msg = fdl_validation_result_error_at(vr, i);
            if (msg) {
                errors.emplace_back(msg);
            }
        }
        fdl_validation_result_free(vr);
        return errors;
    }

    /** Serialize to JSON string via C core. */
    std::string as_json(int indent = 2) const {
        char* ptr = fdl_doc_to_json(doc_, indent);
        if (!ptr) {
            throw std::runtime_error("fdl_doc_to_json returned NULL");
        }
        std::string result(ptr);
        fdl_free(ptr);
        return result;
    }

    /** Composite property — FDL version from major/minor. */
    Version version() const { return Version{version_major(), version_minor()}; }

    // --- Builder methods ---
    /** Add a framing intent to the document. */
    FramingIntentRef add_framing_intent(
        const std::string& id, const std::string& label, const fdl_dimensions_i64_t& aspect_ratio, double protection);
    /** Add a context to the document. */
    ContextRef add_context(const std::string& label, const std::string& context_creator = "");
    /** Add a canvas template to the document. */
    CanvasTemplateRef add_canvas_template(
        const std::string& id,
        const std::string& label,
        const fdl_dimensions_i64_t& target_dimensions,
        double target_anamorphic_squeeze,
        fdl_geometry_path_t fit_source,
        fdl_fit_method_t fit_method,
        fdl_halign_t alignment_method_horizontal,
        fdl_valign_t alignment_method_vertical,
        const fdl_round_strategy_t& round);

    // --- Custom attributes ---

    /** Set a string custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, const std::string& value) {
        return fdl_doc_set_custom_attr_string(doc_, name.c_str(), value.c_str());
    }
    /** Set an integer custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, int64_t value) {
        return fdl_doc_set_custom_attr_int(doc_, name.c_str(), value);
    }
    /** Set a float custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, double value) {
        return fdl_doc_set_custom_attr_float(doc_, name.c_str(), value);
    }
    /** Set a boolean custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, bool value) {
        return fdl_doc_set_custom_attr_bool(doc_, name.c_str(), value ? FDL_TRUE : FDL_FALSE);
    }
    /** Get a string custom attribute. */
    std::optional<std::string> get_custom_attr_string(const std::string& name) const {
        const char* p = fdl_doc_get_custom_attr_string(doc_, name.c_str());
        return p ? std::optional<std::string>(p) : std::nullopt;
    }
    /** Get an integer custom attribute. */
    std::optional<int64_t> get_custom_attr_int(const std::string& name) const {
        int64_t out;
        if (fdl_doc_get_custom_attr_int(doc_, name.c_str(), &out) == 0) {
            return out;
        }
        return std::nullopt;
    }
    /** Get a float custom attribute. */
    std::optional<double> get_custom_attr_float(const std::string& name) const {
        double out;
        if (fdl_doc_get_custom_attr_float(doc_, name.c_str(), &out) == 0) {
            return out;
        }
        return std::nullopt;
    }
    /** Get a boolean custom attribute. */
    std::optional<bool> get_custom_attr_bool(const std::string& name) const {
        int out;
        if (fdl_doc_get_custom_attr_bool(doc_, name.c_str(), &out) == 0) {
            return static_cast<bool>(out);
        }
        return std::nullopt;
    }
    /** Check if a custom attribute exists. */
    bool has_custom_attr(const std::string& name) const { return fdl_doc_has_custom_attr(doc_, name.c_str()) != 0; }
    /** Get the type of a custom attribute. */
    fdl_custom_attr_type_t get_custom_attr_type(const std::string& name) const {
        return fdl_doc_get_custom_attr_type(doc_, name.c_str());
    }
    /** Remove a custom attribute. Returns true if removed. */
    bool remove_custom_attr(const std::string& name) { return fdl_doc_remove_custom_attr(doc_, name.c_str()) == 0; }
    /** Return the number of custom attributes. */
    uint32_t custom_attrs_count() const { return fdl_doc_custom_attrs_count(doc_); }
    /** Return the name of the custom attribute at the given index. */
    std::string custom_attr_name_at(uint32_t index) const {
        const char* p = fdl_doc_custom_attr_name_at(doc_, index);
        return p ? std::string(p) : std::string();
    }
    /** @brief Set a PointFloat custom attribute. */
    int set_custom_attr(const std::string& name, PointFloat value) {
        fdl_point_f64_t c{value.x(), value.y()};
        return fdl_doc_set_custom_attr_point_f64(doc_, name.c_str(), c);
    }
    /** @brief Set a DimensionsFloat custom attribute. */
    int set_custom_attr(const std::string& name, DimensionsFloat value) {
        fdl_dimensions_f64_t c{value.width(), value.height()};
        return fdl_doc_set_custom_attr_dims_f64(doc_, name.c_str(), c);
    }
    /** @brief Set a DimensionsInt custom attribute. */
    int set_custom_attr(const std::string& name, DimensionsInt value) {
        fdl_dimensions_i64_t c{value.width(), value.height()};
        return fdl_doc_set_custom_attr_dims_i64(doc_, name.c_str(), c);
    }
    /** @brief Get a PointFloat custom attribute. */
    std::optional<PointFloat> get_custom_attr_point_f64(const std::string& name) const {
        fdl_point_f64_t out{};
        if (fdl_doc_get_custom_attr_point_f64(doc_, name.c_str(), &out) != 0) {
            return std::nullopt;
        }
        return PointFloat(out.x, out.y);
    }
    /** @brief Get a DimensionsFloat custom attribute. */
    std::optional<DimensionsFloat> get_custom_attr_dims_f64(const std::string& name) const {
        fdl_dimensions_f64_t out{};
        if (fdl_doc_get_custom_attr_dims_f64(doc_, name.c_str(), &out) != 0) {
            return std::nullopt;
        }
        return DimensionsFloat(out.width, out.height);
    }
    /** @brief Get a DimensionsInt custom attribute. */
    std::optional<DimensionsInt> get_custom_attr_dims_i64(const std::string& name) const {
        fdl_dimensions_i64_t out{};
        if (fdl_doc_get_custom_attr_dims_i64(doc_, name.c_str(), &out) != 0) {
            return std::nullopt;
        }
        return DimensionsInt(out.width, out.height);
    }

private:
    fdl_doc_t* doc_;
};

// -----------------------------------------------------------------------
// TemplateResult
// -----------------------------------------------------------------------
struct TemplateResult {
    FDL fdl;

    /** The new context created by the template apply. */
    ContextRef context() const;
    /** The new canvas created by the template apply. */
    CanvasRef canvas() const;
    /** The new framing decision created by the template apply. */
    FramingDecisionRef framing_decision() const;

    TemplateResult(FDL fdl_, std::string context_label_, std::string canvas_id_, std::string framing_decision_id_)
        : fdl(std::move(fdl_)), _context_label(std::move(context_label_)), _canvas_id(std::move(canvas_id_)),
          _framing_decision_id(std::move(framing_decision_id_)) {}

    TemplateResult(TemplateResult&&) = default;
    TemplateResult& operator=(TemplateResult&&) = default;

private:
    std::string _context_label;
    std::string _canvas_id;
    std::string _framing_decision_id;
};

// -----------------------------------------------------------------------
// ContextRef — non-owning
// -----------------------------------------------------------------------
class ContextRef {
public:
    explicit ContextRef(fdl_context_t* handle) noexcept : ctx_(handle) {}

    // --- Property accessors ---
    std::string label() const {
        const char* p = fdl_context_get_label(ctx_);
        return p ? std::string(p) : std::string();
    }

    std::string context_creator() const {
        const char* p = fdl_context_get_context_creator(ctx_);
        return p ? std::string(p) : std::string();
    }

    bool has_clip_id() const { return fdl_context_has_clip_id(ctx_) != 0; }
    std::optional<ClipIDRef> clip_id() const;
    void set_clip_id(const std::string& json) {
        const char* err = fdl_context_set_clip_id_json(ctx_, json.c_str(), json.size());
        if (err) {
            std::string msg(err);
            fdl_free(const_cast<char*>(err));
            throw std::runtime_error(msg);
        }
    }
    void remove_clip_id() { fdl_context_remove_clip_id(ctx_); }

    // --- Collection traversal ---
    uint32_t canvases_count() const { return fdl_context_canvases_count(ctx_); }
    CanvasRef canvas_at(uint32_t i) const;
    CanvasRef canvas_find_by_id(const std::string& id) const;

    /** Serialize to canonical JSON string. */
    std::string to_json(int indent = 2) const {
        char* ptr = fdl_context_to_json(ctx_, indent);
        if (!ptr) {
            throw std::runtime_error("fdl_context_to_json returned NULL");
        }
        std::string json(ptr);
        fdl_free(ptr);
        return json;
    }

    // --- Builder methods ---
    /** Add a canvas to this context. */
    CanvasRef add_canvas(
        const std::string& id,
        const std::string& label,
        const std::string& source_canvas_id,
        const fdl_dimensions_i64_t& dimensions,
        double anamorphic_squeeze);

    // --- Lifecycle methods ---
    /** Find matching canvas when input dimensions differ from selected canvas. */
    ::fdl::ResolveCanvasResult resolve_canvas_for_dimensions(
        const fdl_dimensions_f64_t& input_dims, const CanvasRef& canvas, const FramingDecisionRef& framing) const;

    // --- Custom attributes ---

    /** Set a string custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, const std::string& value) {
        return fdl_context_set_custom_attr_string(ctx_, name.c_str(), value.c_str());
    }
    /** Set an integer custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, int64_t value) {
        return fdl_context_set_custom_attr_int(ctx_, name.c_str(), value);
    }
    /** Set a float custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, double value) {
        return fdl_context_set_custom_attr_float(ctx_, name.c_str(), value);
    }
    /** Set a boolean custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, bool value) {
        return fdl_context_set_custom_attr_bool(ctx_, name.c_str(), value ? FDL_TRUE : FDL_FALSE);
    }
    /** Get a string custom attribute. */
    std::optional<std::string> get_custom_attr_string(const std::string& name) const {
        const char* p = fdl_context_get_custom_attr_string(ctx_, name.c_str());
        return p ? std::optional<std::string>(p) : std::nullopt;
    }
    /** Get an integer custom attribute. */
    std::optional<int64_t> get_custom_attr_int(const std::string& name) const {
        int64_t out;
        if (fdl_context_get_custom_attr_int(ctx_, name.c_str(), &out) == 0) {
            return out;
        }
        return std::nullopt;
    }
    /** Get a float custom attribute. */
    std::optional<double> get_custom_attr_float(const std::string& name) const {
        double out;
        if (fdl_context_get_custom_attr_float(ctx_, name.c_str(), &out) == 0) {
            return out;
        }
        return std::nullopt;
    }
    /** Get a boolean custom attribute. */
    std::optional<bool> get_custom_attr_bool(const std::string& name) const {
        int out;
        if (fdl_context_get_custom_attr_bool(ctx_, name.c_str(), &out) == 0) {
            return static_cast<bool>(out);
        }
        return std::nullopt;
    }
    /** Check if a custom attribute exists. */
    bool has_custom_attr(const std::string& name) const { return fdl_context_has_custom_attr(ctx_, name.c_str()) != 0; }
    /** Get the type of a custom attribute. */
    fdl_custom_attr_type_t get_custom_attr_type(const std::string& name) const {
        return fdl_context_get_custom_attr_type(ctx_, name.c_str());
    }
    /** Remove a custom attribute. Returns true if removed. */
    bool remove_custom_attr(const std::string& name) { return fdl_context_remove_custom_attr(ctx_, name.c_str()) == 0; }
    /** Return the number of custom attributes. */
    uint32_t custom_attrs_count() const { return fdl_context_custom_attrs_count(ctx_); }
    /** Return the name of the custom attribute at the given index. */
    std::string custom_attr_name_at(uint32_t index) const {
        const char* p = fdl_context_custom_attr_name_at(ctx_, index);
        return p ? std::string(p) : std::string();
    }
    /** @brief Set a PointFloat custom attribute. */
    int set_custom_attr(const std::string& name, PointFloat value) {
        fdl_point_f64_t c{value.x(), value.y()};
        return fdl_context_set_custom_attr_point_f64(ctx_, name.c_str(), c);
    }
    /** @brief Set a DimensionsFloat custom attribute. */
    int set_custom_attr(const std::string& name, DimensionsFloat value) {
        fdl_dimensions_f64_t c{value.width(), value.height()};
        return fdl_context_set_custom_attr_dims_f64(ctx_, name.c_str(), c);
    }
    /** @brief Set a DimensionsInt custom attribute. */
    int set_custom_attr(const std::string& name, DimensionsInt value) {
        fdl_dimensions_i64_t c{value.width(), value.height()};
        return fdl_context_set_custom_attr_dims_i64(ctx_, name.c_str(), c);
    }
    /** @brief Get a PointFloat custom attribute. */
    std::optional<PointFloat> get_custom_attr_point_f64(const std::string& name) const {
        fdl_point_f64_t out{};
        if (fdl_context_get_custom_attr_point_f64(ctx_, name.c_str(), &out) != 0) {
            return std::nullopt;
        }
        return PointFloat(out.x, out.y);
    }
    /** @brief Get a DimensionsFloat custom attribute. */
    std::optional<DimensionsFloat> get_custom_attr_dims_f64(const std::string& name) const {
        fdl_dimensions_f64_t out{};
        if (fdl_context_get_custom_attr_dims_f64(ctx_, name.c_str(), &out) != 0) {
            return std::nullopt;
        }
        return DimensionsFloat(out.width, out.height);
    }
    /** @brief Get a DimensionsInt custom attribute. */
    std::optional<DimensionsInt> get_custom_attr_dims_i64(const std::string& name) const {
        fdl_dimensions_i64_t out{};
        if (fdl_context_get_custom_attr_dims_i64(ctx_, name.c_str(), &out) != 0) {
            return std::nullopt;
        }
        return DimensionsInt(out.width, out.height);
    }

    fdl_context_t* get() const noexcept { return ctx_; }

private:
    fdl_context_t* ctx_;
};

// -----------------------------------------------------------------------
// CanvasRef — non-owning
// -----------------------------------------------------------------------
class CanvasRef {
public:
    explicit CanvasRef(fdl_canvas_t* handle) noexcept : canvas_(handle) {}

    // --- Property accessors ---
    std::string id() const {
        const char* p = fdl_canvas_get_id(canvas_);
        return p ? std::string(p) : std::string();
    }

    std::string label() const {
        const char* p = fdl_canvas_get_label(canvas_);
        return p ? std::string(p) : std::string();
    }

    std::string source_canvas_id() const {
        const char* p = fdl_canvas_get_source_canvas_id(canvas_);
        return p ? std::string(p) : std::string();
    }

    fdl_dimensions_i64_t dimensions() const { return fdl_canvas_get_dimensions(canvas_); }
    void set_dimensions(fdl_dimensions_i64_t value) { fdl_canvas_set_dimensions(canvas_, value); }

    double anamorphic_squeeze() const { return fdl_canvas_get_anamorphic_squeeze(canvas_); }
    void set_anamorphic_squeeze(double value) { fdl_canvas_set_anamorphic_squeeze(canvas_, value); }

    bool has_effective_dimensions() const { return fdl_canvas_has_effective_dimensions(canvas_) != 0; }
    std::optional<fdl_dimensions_i64_t> effective_dimensions() const {
        if (!fdl_canvas_has_effective_dimensions(canvas_)) {
            return std::nullopt;
        }
        return fdl_canvas_get_effective_dimensions(canvas_);
    }
    void set_effective_dimensions(fdl_dimensions_i64_t value) { fdl_canvas_set_effective_dims_only(canvas_, value); }
    void remove_effective_dimensions() { fdl_canvas_remove_effective(canvas_); }

    bool has_effective_anchor_point() const { return fdl_canvas_has_effective_dimensions(canvas_) != 0; }
    std::optional<fdl_point_f64_t> effective_anchor_point() const {
        if (!fdl_canvas_has_effective_dimensions(canvas_)) {
            return std::nullopt;
        }
        return fdl_canvas_get_effective_anchor_point(canvas_);
    }

    bool has_photosite_dimensions() const { return fdl_canvas_has_photosite_dimensions(canvas_) != 0; }
    std::optional<fdl_dimensions_i64_t> photosite_dimensions() const {
        if (!fdl_canvas_has_photosite_dimensions(canvas_)) {
            return std::nullopt;
        }
        return fdl_canvas_get_photosite_dimensions(canvas_);
    }
    void set_photosite_dimensions(fdl_dimensions_i64_t value) { fdl_canvas_set_photosite_dimensions(canvas_, value); }

    bool has_physical_dimensions() const { return fdl_canvas_has_physical_dimensions(canvas_) != 0; }
    std::optional<fdl_dimensions_f64_t> physical_dimensions() const {
        if (!fdl_canvas_has_physical_dimensions(canvas_)) {
            return std::nullopt;
        }
        return fdl_canvas_get_physical_dimensions(canvas_);
    }
    void set_physical_dimensions(fdl_dimensions_f64_t value) { fdl_canvas_set_physical_dimensions(canvas_, value); }

    // --- Collection traversal ---
    uint32_t framing_decisions_count() const { return fdl_canvas_framing_decisions_count(canvas_); }
    FramingDecisionRef framing_decision_at(uint32_t i) const;
    FramingDecisionRef framing_decision_find_by_id(const std::string& id) const;

    /** Serialize to canonical JSON string. */
    std::string to_json(int indent = 2) const {
        char* ptr = fdl_canvas_to_json(canvas_, indent);
        if (!ptr) {
            throw std::runtime_error("fdl_canvas_to_json returned NULL");
        }
        std::string json(ptr);
        fdl_free(ptr);
        return json;
    }

    // --- Builder methods ---
    /** Add a framing decision to this canvas. */
    FramingDecisionRef add_framing_decision(
        const std::string& id,
        const std::string& label,
        const std::string& framing_intent_id,
        const fdl_dimensions_f64_t& dimensions,
        const fdl_point_f64_t& anchor_point);

    // --- Lifecycle methods ---
    /** Set effective dimensions and anchor point on this canvas. */
    void set_effective(const fdl_dimensions_i64_t& dims, const fdl_point_f64_t& anchor);
    /** Get canvas rect as (0, 0, width, height). */
    Rect get_rect() const { return Rect(::fdl_canvas_get_rect(canvas_)); }
    /** Get effective rect or None if not defined. */
    std::optional<Rect> get_effective_rect() const {
        fdl_rect_t out;
        if (!::fdl_canvas_get_effective_rect(canvas_, &out)) {
            return std::nullopt;
        }
        return Rect(out);
    }

    // --- Custom attributes ---

    /** Set a string custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, const std::string& value) {
        return fdl_canvas_set_custom_attr_string(canvas_, name.c_str(), value.c_str());
    }
    /** Set an integer custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, int64_t value) {
        return fdl_canvas_set_custom_attr_int(canvas_, name.c_str(), value);
    }
    /** Set a float custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, double value) {
        return fdl_canvas_set_custom_attr_float(canvas_, name.c_str(), value);
    }
    /** Set a boolean custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, bool value) {
        return fdl_canvas_set_custom_attr_bool(canvas_, name.c_str(), value ? FDL_TRUE : FDL_FALSE);
    }
    /** Get a string custom attribute. */
    std::optional<std::string> get_custom_attr_string(const std::string& name) const {
        const char* p = fdl_canvas_get_custom_attr_string(canvas_, name.c_str());
        return p ? std::optional<std::string>(p) : std::nullopt;
    }
    /** Get an integer custom attribute. */
    std::optional<int64_t> get_custom_attr_int(const std::string& name) const {
        int64_t out;
        if (fdl_canvas_get_custom_attr_int(canvas_, name.c_str(), &out) == 0) {
            return out;
        }
        return std::nullopt;
    }
    /** Get a float custom attribute. */
    std::optional<double> get_custom_attr_float(const std::string& name) const {
        double out;
        if (fdl_canvas_get_custom_attr_float(canvas_, name.c_str(), &out) == 0) {
            return out;
        }
        return std::nullopt;
    }
    /** Get a boolean custom attribute. */
    std::optional<bool> get_custom_attr_bool(const std::string& name) const {
        int out;
        if (fdl_canvas_get_custom_attr_bool(canvas_, name.c_str(), &out) == 0) {
            return static_cast<bool>(out);
        }
        return std::nullopt;
    }
    /** Check if a custom attribute exists. */
    bool has_custom_attr(const std::string& name) const {
        return fdl_canvas_has_custom_attr(canvas_, name.c_str()) != 0;
    }
    /** Get the type of a custom attribute. */
    fdl_custom_attr_type_t get_custom_attr_type(const std::string& name) const {
        return fdl_canvas_get_custom_attr_type(canvas_, name.c_str());
    }
    /** Remove a custom attribute. Returns true if removed. */
    bool remove_custom_attr(const std::string& name) {
        return fdl_canvas_remove_custom_attr(canvas_, name.c_str()) == 0;
    }
    /** Return the number of custom attributes. */
    uint32_t custom_attrs_count() const { return fdl_canvas_custom_attrs_count(canvas_); }
    /** Return the name of the custom attribute at the given index. */
    std::string custom_attr_name_at(uint32_t index) const {
        const char* p = fdl_canvas_custom_attr_name_at(canvas_, index);
        return p ? std::string(p) : std::string();
    }
    /** @brief Set a PointFloat custom attribute. */
    int set_custom_attr(const std::string& name, PointFloat value) {
        fdl_point_f64_t c{value.x(), value.y()};
        return fdl_canvas_set_custom_attr_point_f64(canvas_, name.c_str(), c);
    }
    /** @brief Set a DimensionsFloat custom attribute. */
    int set_custom_attr(const std::string& name, DimensionsFloat value) {
        fdl_dimensions_f64_t c{value.width(), value.height()};
        return fdl_canvas_set_custom_attr_dims_f64(canvas_, name.c_str(), c);
    }
    /** @brief Set a DimensionsInt custom attribute. */
    int set_custom_attr(const std::string& name, DimensionsInt value) {
        fdl_dimensions_i64_t c{value.width(), value.height()};
        return fdl_canvas_set_custom_attr_dims_i64(canvas_, name.c_str(), c);
    }
    /** @brief Get a PointFloat custom attribute. */
    std::optional<PointFloat> get_custom_attr_point_f64(const std::string& name) const {
        fdl_point_f64_t out{};
        if (fdl_canvas_get_custom_attr_point_f64(canvas_, name.c_str(), &out) != 0) {
            return std::nullopt;
        }
        return PointFloat(out.x, out.y);
    }
    /** @brief Get a DimensionsFloat custom attribute. */
    std::optional<DimensionsFloat> get_custom_attr_dims_f64(const std::string& name) const {
        fdl_dimensions_f64_t out{};
        if (fdl_canvas_get_custom_attr_dims_f64(canvas_, name.c_str(), &out) != 0) {
            return std::nullopt;
        }
        return DimensionsFloat(out.width, out.height);
    }
    /** @brief Get a DimensionsInt custom attribute. */
    std::optional<DimensionsInt> get_custom_attr_dims_i64(const std::string& name) const {
        fdl_dimensions_i64_t out{};
        if (fdl_canvas_get_custom_attr_dims_i64(canvas_, name.c_str(), &out) != 0) {
            return std::nullopt;
        }
        return DimensionsInt(out.width, out.height);
    }

    fdl_canvas_t* get() const noexcept { return canvas_; }

private:
    fdl_canvas_t* canvas_;
};

// -----------------------------------------------------------------------
// FramingDecisionRef — non-owning
// -----------------------------------------------------------------------
class FramingDecisionRef {
public:
    explicit FramingDecisionRef(fdl_framing_decision_t* handle) noexcept : fd_(handle) {}

    // --- Property accessors ---
    std::string id() const {
        const char* p = fdl_framing_decision_get_id(fd_);
        return p ? std::string(p) : std::string();
    }

    std::string label() const {
        const char* p = fdl_framing_decision_get_label(fd_);
        return p ? std::string(p) : std::string();
    }

    std::string framing_intent_id() const {
        const char* p = fdl_framing_decision_get_framing_intent_id(fd_);
        return p ? std::string(p) : std::string();
    }

    fdl_dimensions_f64_t dimensions() const { return fdl_framing_decision_get_dimensions(fd_); }
    void set_dimensions(fdl_dimensions_f64_t value) { fdl_framing_decision_set_dimensions(fd_, value); }

    fdl_point_f64_t anchor_point() const { return fdl_framing_decision_get_anchor_point(fd_); }
    void set_anchor_point(fdl_point_f64_t value) { fdl_framing_decision_set_anchor_point(fd_, value); }

    bool has_protection_dimensions() const { return fdl_framing_decision_has_protection(fd_) != 0; }
    std::optional<fdl_dimensions_f64_t> protection_dimensions() const {
        if (!fdl_framing_decision_has_protection(fd_)) {
            return std::nullopt;
        }
        return fdl_framing_decision_get_protection_dimensions(fd_);
    }
    void set_protection_dimensions(fdl_dimensions_f64_t value) {
        fdl_framing_decision_set_protection_dimensions(fd_, value);
    }
    void remove_protection_dimensions() { fdl_framing_decision_remove_protection(fd_); }

    bool has_protection_anchor_point() const { return fdl_framing_decision_has_protection(fd_) != 0; }
    std::optional<fdl_point_f64_t> protection_anchor_point() const {
        if (!fdl_framing_decision_has_protection(fd_)) {
            return std::nullopt;
        }
        return fdl_framing_decision_get_protection_anchor_point(fd_);
    }
    void set_protection_anchor_point(fdl_point_f64_t value) {
        fdl_framing_decision_set_protection_anchor_point(fd_, value);
    }

    // --- Collection traversal ---

    /** Serialize to canonical JSON string. */
    std::string to_json(int indent = 2) const {
        char* ptr = fdl_framing_decision_to_json(fd_, indent);
        if (!ptr) {
            throw std::runtime_error("fdl_framing_decision_to_json returned NULL");
        }
        std::string json(ptr);
        fdl_free(ptr);
        return json;
    }

    // --- Builder methods ---

    // --- Lifecycle methods ---
    /** Get framing rect as (anchor_x, anchor_y, width, height). */
    Rect get_rect() const { return Rect(::fdl_framing_decision_get_rect(fd_)); }
    /** Get protection rect or None if not defined. */
    std::optional<Rect> get_protection_rect() const {
        fdl_rect_t out;
        if (!::fdl_framing_decision_get_protection_rect(fd_, &out)) {
            return std::nullopt;
        }
        return Rect(out);
    }
    /** Set protection dimensions and anchor point on this framing decision. */
    void set_protection(const fdl_dimensions_f64_t& dims, const fdl_point_f64_t& anchor);
    /** Adjust anchor point based on alignment within canvas. */
    void adjust_anchor_point(const CanvasRef& canvas, fdl_halign_t h_method, fdl_valign_t v_method);
    /** Adjust protection anchor point based on alignment within canvas. */
    void adjust_protection_anchor_point(const CanvasRef& canvas, fdl_halign_t h_method, fdl_valign_t v_method);
    /** Create a FramingDecision from a canvas and framing intent. */
    void from_framing_intent(
        const CanvasRef& canvas, const FramingIntentRef& framing_intent, const fdl_round_strategy_t& rounding);
    /** Populate this framing decision from a canvas and framing intent (in-place). */
    void populate_from_intent(
        const CanvasRef& canvas, const FramingIntentRef& framing_intent, const fdl_round_strategy_t& rounding);

    // --- Custom attributes ---

    /** Set a string custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, const std::string& value) {
        return fdl_framing_decision_set_custom_attr_string(fd_, name.c_str(), value.c_str());
    }
    /** Set an integer custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, int64_t value) {
        return fdl_framing_decision_set_custom_attr_int(fd_, name.c_str(), value);
    }
    /** Set a float custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, double value) {
        return fdl_framing_decision_set_custom_attr_float(fd_, name.c_str(), value);
    }
    /** Set a boolean custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, bool value) {
        return fdl_framing_decision_set_custom_attr_bool(fd_, name.c_str(), value ? FDL_TRUE : FDL_FALSE);
    }
    /** Get a string custom attribute. */
    std::optional<std::string> get_custom_attr_string(const std::string& name) const {
        const char* p = fdl_framing_decision_get_custom_attr_string(fd_, name.c_str());
        return p ? std::optional<std::string>(p) : std::nullopt;
    }
    /** Get an integer custom attribute. */
    std::optional<int64_t> get_custom_attr_int(const std::string& name) const {
        int64_t out;
        if (fdl_framing_decision_get_custom_attr_int(fd_, name.c_str(), &out) == 0) {
            return out;
        }
        return std::nullopt;
    }
    /** Get a float custom attribute. */
    std::optional<double> get_custom_attr_float(const std::string& name) const {
        double out;
        if (fdl_framing_decision_get_custom_attr_float(fd_, name.c_str(), &out) == 0) {
            return out;
        }
        return std::nullopt;
    }
    /** Get a boolean custom attribute. */
    std::optional<bool> get_custom_attr_bool(const std::string& name) const {
        int out;
        if (fdl_framing_decision_get_custom_attr_bool(fd_, name.c_str(), &out) == 0) {
            return static_cast<bool>(out);
        }
        return std::nullopt;
    }
    /** Check if a custom attribute exists. */
    bool has_custom_attr(const std::string& name) const {
        return fdl_framing_decision_has_custom_attr(fd_, name.c_str()) != 0;
    }
    /** Get the type of a custom attribute. */
    fdl_custom_attr_type_t get_custom_attr_type(const std::string& name) const {
        return fdl_framing_decision_get_custom_attr_type(fd_, name.c_str());
    }
    /** Remove a custom attribute. Returns true if removed. */
    bool remove_custom_attr(const std::string& name) {
        return fdl_framing_decision_remove_custom_attr(fd_, name.c_str()) == 0;
    }
    /** Return the number of custom attributes. */
    uint32_t custom_attrs_count() const { return fdl_framing_decision_custom_attrs_count(fd_); }
    /** Return the name of the custom attribute at the given index. */
    std::string custom_attr_name_at(uint32_t index) const {
        const char* p = fdl_framing_decision_custom_attr_name_at(fd_, index);
        return p ? std::string(p) : std::string();
    }
    /** @brief Set a PointFloat custom attribute. */
    int set_custom_attr(const std::string& name, PointFloat value) {
        fdl_point_f64_t c{value.x(), value.y()};
        return fdl_framing_decision_set_custom_attr_point_f64(fd_, name.c_str(), c);
    }
    /** @brief Set a DimensionsFloat custom attribute. */
    int set_custom_attr(const std::string& name, DimensionsFloat value) {
        fdl_dimensions_f64_t c{value.width(), value.height()};
        return fdl_framing_decision_set_custom_attr_dims_f64(fd_, name.c_str(), c);
    }
    /** @brief Set a DimensionsInt custom attribute. */
    int set_custom_attr(const std::string& name, DimensionsInt value) {
        fdl_dimensions_i64_t c{value.width(), value.height()};
        return fdl_framing_decision_set_custom_attr_dims_i64(fd_, name.c_str(), c);
    }
    /** @brief Get a PointFloat custom attribute. */
    std::optional<PointFloat> get_custom_attr_point_f64(const std::string& name) const {
        fdl_point_f64_t out{};
        if (fdl_framing_decision_get_custom_attr_point_f64(fd_, name.c_str(), &out) != 0) {
            return std::nullopt;
        }
        return PointFloat(out.x, out.y);
    }
    /** @brief Get a DimensionsFloat custom attribute. */
    std::optional<DimensionsFloat> get_custom_attr_dims_f64(const std::string& name) const {
        fdl_dimensions_f64_t out{};
        if (fdl_framing_decision_get_custom_attr_dims_f64(fd_, name.c_str(), &out) != 0) {
            return std::nullopt;
        }
        return DimensionsFloat(out.width, out.height);
    }
    /** @brief Get a DimensionsInt custom attribute. */
    std::optional<DimensionsInt> get_custom_attr_dims_i64(const std::string& name) const {
        fdl_dimensions_i64_t out{};
        if (fdl_framing_decision_get_custom_attr_dims_i64(fd_, name.c_str(), &out) != 0) {
            return std::nullopt;
        }
        return DimensionsInt(out.width, out.height);
    }

    fdl_framing_decision_t* get() const noexcept { return fd_; }

private:
    fdl_framing_decision_t* fd_;
};

// -----------------------------------------------------------------------
// FramingIntentRef — non-owning
// -----------------------------------------------------------------------
class FramingIntentRef {
public:
    explicit FramingIntentRef(fdl_framing_intent_t* handle) noexcept : fi_(handle) {}

    // --- Property accessors ---
    std::string id() const {
        const char* p = fdl_framing_intent_get_id(fi_);
        return p ? std::string(p) : std::string();
    }

    std::string label() const {
        const char* p = fdl_framing_intent_get_label(fi_);
        return p ? std::string(p) : std::string();
    }

    fdl_dimensions_i64_t aspect_ratio() const { return fdl_framing_intent_get_aspect_ratio(fi_); }
    void set_aspect_ratio(fdl_dimensions_i64_t value) { fdl_framing_intent_set_aspect_ratio(fi_, value); }

    double protection() const { return fdl_framing_intent_get_protection(fi_); }
    void set_protection(double value) { fdl_framing_intent_set_protection(fi_, value); }

    // --- Collection traversal ---

    /** Serialize to canonical JSON string. */
    std::string to_json(int indent = 2) const {
        char* ptr = fdl_framing_intent_to_json(fi_, indent);
        if (!ptr) {
            throw std::runtime_error("fdl_framing_intent_to_json returned NULL");
        }
        std::string json(ptr);
        fdl_free(ptr);
        return json;
    }

    // --- Builder methods ---

    // --- Custom attributes ---

    /** Set a string custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, const std::string& value) {
        return fdl_framing_intent_set_custom_attr_string(fi_, name.c_str(), value.c_str());
    }
    /** Set an integer custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, int64_t value) {
        return fdl_framing_intent_set_custom_attr_int(fi_, name.c_str(), value);
    }
    /** Set a float custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, double value) {
        return fdl_framing_intent_set_custom_attr_float(fi_, name.c_str(), value);
    }
    /** Set a boolean custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, bool value) {
        return fdl_framing_intent_set_custom_attr_bool(fi_, name.c_str(), value ? FDL_TRUE : FDL_FALSE);
    }
    /** Get a string custom attribute. */
    std::optional<std::string> get_custom_attr_string(const std::string& name) const {
        const char* p = fdl_framing_intent_get_custom_attr_string(fi_, name.c_str());
        return p ? std::optional<std::string>(p) : std::nullopt;
    }
    /** Get an integer custom attribute. */
    std::optional<int64_t> get_custom_attr_int(const std::string& name) const {
        int64_t out;
        if (fdl_framing_intent_get_custom_attr_int(fi_, name.c_str(), &out) == 0) {
            return out;
        }
        return std::nullopt;
    }
    /** Get a float custom attribute. */
    std::optional<double> get_custom_attr_float(const std::string& name) const {
        double out;
        if (fdl_framing_intent_get_custom_attr_float(fi_, name.c_str(), &out) == 0) {
            return out;
        }
        return std::nullopt;
    }
    /** Get a boolean custom attribute. */
    std::optional<bool> get_custom_attr_bool(const std::string& name) const {
        int out;
        if (fdl_framing_intent_get_custom_attr_bool(fi_, name.c_str(), &out) == 0) {
            return static_cast<bool>(out);
        }
        return std::nullopt;
    }
    /** Check if a custom attribute exists. */
    bool has_custom_attr(const std::string& name) const {
        return fdl_framing_intent_has_custom_attr(fi_, name.c_str()) != 0;
    }
    /** Get the type of a custom attribute. */
    fdl_custom_attr_type_t get_custom_attr_type(const std::string& name) const {
        return fdl_framing_intent_get_custom_attr_type(fi_, name.c_str());
    }
    /** Remove a custom attribute. Returns true if removed. */
    bool remove_custom_attr(const std::string& name) {
        return fdl_framing_intent_remove_custom_attr(fi_, name.c_str()) == 0;
    }
    /** Return the number of custom attributes. */
    uint32_t custom_attrs_count() const { return fdl_framing_intent_custom_attrs_count(fi_); }
    /** Return the name of the custom attribute at the given index. */
    std::string custom_attr_name_at(uint32_t index) const {
        const char* p = fdl_framing_intent_custom_attr_name_at(fi_, index);
        return p ? std::string(p) : std::string();
    }
    /** @brief Set a PointFloat custom attribute. */
    int set_custom_attr(const std::string& name, PointFloat value) {
        fdl_point_f64_t c{value.x(), value.y()};
        return fdl_framing_intent_set_custom_attr_point_f64(fi_, name.c_str(), c);
    }
    /** @brief Set a DimensionsFloat custom attribute. */
    int set_custom_attr(const std::string& name, DimensionsFloat value) {
        fdl_dimensions_f64_t c{value.width(), value.height()};
        return fdl_framing_intent_set_custom_attr_dims_f64(fi_, name.c_str(), c);
    }
    /** @brief Set a DimensionsInt custom attribute. */
    int set_custom_attr(const std::string& name, DimensionsInt value) {
        fdl_dimensions_i64_t c{value.width(), value.height()};
        return fdl_framing_intent_set_custom_attr_dims_i64(fi_, name.c_str(), c);
    }
    /** @brief Get a PointFloat custom attribute. */
    std::optional<PointFloat> get_custom_attr_point_f64(const std::string& name) const {
        fdl_point_f64_t out{};
        if (fdl_framing_intent_get_custom_attr_point_f64(fi_, name.c_str(), &out) != 0) {
            return std::nullopt;
        }
        return PointFloat(out.x, out.y);
    }
    /** @brief Get a DimensionsFloat custom attribute. */
    std::optional<DimensionsFloat> get_custom_attr_dims_f64(const std::string& name) const {
        fdl_dimensions_f64_t out{};
        if (fdl_framing_intent_get_custom_attr_dims_f64(fi_, name.c_str(), &out) != 0) {
            return std::nullopt;
        }
        return DimensionsFloat(out.width, out.height);
    }
    /** @brief Get a DimensionsInt custom attribute. */
    std::optional<DimensionsInt> get_custom_attr_dims_i64(const std::string& name) const {
        fdl_dimensions_i64_t out{};
        if (fdl_framing_intent_get_custom_attr_dims_i64(fi_, name.c_str(), &out) != 0) {
            return std::nullopt;
        }
        return DimensionsInt(out.width, out.height);
    }

    fdl_framing_intent_t* get() const noexcept { return fi_; }

private:
    fdl_framing_intent_t* fi_;
};

// -----------------------------------------------------------------------
// CanvasTemplateRef — non-owning
// -----------------------------------------------------------------------
class CanvasTemplateRef {
public:
    explicit CanvasTemplateRef(fdl_canvas_template_t* handle) noexcept : ct_(handle) {}

    // --- Property accessors ---
    std::string id() const {
        const char* p = fdl_canvas_template_get_id(ct_);
        return p ? std::string(p) : std::string();
    }

    std::string label() const {
        const char* p = fdl_canvas_template_get_label(ct_);
        return p ? std::string(p) : std::string();
    }

    fdl_dimensions_i64_t target_dimensions() const { return fdl_canvas_template_get_target_dimensions(ct_); }

    double target_anamorphic_squeeze() const { return fdl_canvas_template_get_target_anamorphic_squeeze(ct_); }

    fdl_geometry_path_t fit_source() const { return fdl_canvas_template_get_fit_source(ct_); }

    fdl_fit_method_t fit_method() const { return fdl_canvas_template_get_fit_method(ct_); }

    fdl_halign_t alignment_method_horizontal() const {
        return fdl_canvas_template_get_alignment_method_horizontal(ct_);
    }

    fdl_valign_t alignment_method_vertical() const { return fdl_canvas_template_get_alignment_method_vertical(ct_); }

    fdl_round_strategy_t round() const { return fdl_canvas_template_get_round(ct_); }

    bool has_preserve_from_source_canvas() const {
        return fdl_canvas_template_has_preserve_from_source_canvas(ct_) != 0;
    }
    std::optional<fdl_geometry_path_t> preserve_from_source_canvas() const {
        if (!fdl_canvas_template_has_preserve_from_source_canvas(ct_)) {
            return std::nullopt;
        }
        return fdl_canvas_template_get_preserve_from_source_canvas(ct_);
    }
    void set_preserve_from_source_canvas(fdl_geometry_path_t value) {
        fdl_canvas_template_set_preserve_from_source_canvas(ct_, value);
    }

    bool has_maximum_dimensions() const { return fdl_canvas_template_has_maximum_dimensions(ct_) != 0; }
    std::optional<fdl_dimensions_i64_t> maximum_dimensions() const {
        if (!fdl_canvas_template_has_maximum_dimensions(ct_)) {
            return std::nullopt;
        }
        return fdl_canvas_template_get_maximum_dimensions(ct_);
    }
    void set_maximum_dimensions(fdl_dimensions_i64_t value) { fdl_canvas_template_set_maximum_dimensions(ct_, value); }

    bool pad_to_maximum() const { return fdl_canvas_template_get_pad_to_maximum(ct_) != 0; }
    void set_pad_to_maximum(bool value) { fdl_canvas_template_set_pad_to_maximum(ct_, value ? 1 : 0); }

    // --- Collection traversal ---

    /** Serialize to canonical JSON string. */
    std::string to_json(int indent = 2) const {
        char* ptr = fdl_canvas_template_to_json(ct_, indent);
        if (!ptr) {
            throw std::runtime_error("fdl_canvas_template_to_json returned NULL");
        }
        std::string json(ptr);
        fdl_free(ptr);
        return json;
    }

    // --- Builder methods ---

    // --- Lifecycle methods ---
    /** Apply this canvas template to a source canvas/framing decision. */
    ::fdl::TemplateResult apply(
        const CanvasRef& source_canvas,
        const FramingDecisionRef& source_framing,
        const std::string& new_canvas_id,
        const std::string& new_fd_name,
        const std::string& source_context_label = "",
        const std::string& context_creator = "") const;

    // --- Custom attributes ---

    /** Set a string custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, const std::string& value) {
        return fdl_canvas_template_set_custom_attr_string(ct_, name.c_str(), value.c_str());
    }
    /** Set an integer custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, int64_t value) {
        return fdl_canvas_template_set_custom_attr_int(ct_, name.c_str(), value);
    }
    /** Set a float custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, double value) {
        return fdl_canvas_template_set_custom_attr_float(ct_, name.c_str(), value);
    }
    /** Set a boolean custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, bool value) {
        return fdl_canvas_template_set_custom_attr_bool(ct_, name.c_str(), value ? FDL_TRUE : FDL_FALSE);
    }
    /** Get a string custom attribute. */
    std::optional<std::string> get_custom_attr_string(const std::string& name) const {
        const char* p = fdl_canvas_template_get_custom_attr_string(ct_, name.c_str());
        return p ? std::optional<std::string>(p) : std::nullopt;
    }
    /** Get an integer custom attribute. */
    std::optional<int64_t> get_custom_attr_int(const std::string& name) const {
        int64_t out;
        if (fdl_canvas_template_get_custom_attr_int(ct_, name.c_str(), &out) == 0) {
            return out;
        }
        return std::nullopt;
    }
    /** Get a float custom attribute. */
    std::optional<double> get_custom_attr_float(const std::string& name) const {
        double out;
        if (fdl_canvas_template_get_custom_attr_float(ct_, name.c_str(), &out) == 0) {
            return out;
        }
        return std::nullopt;
    }
    /** Get a boolean custom attribute. */
    std::optional<bool> get_custom_attr_bool(const std::string& name) const {
        int out;
        if (fdl_canvas_template_get_custom_attr_bool(ct_, name.c_str(), &out) == 0) {
            return static_cast<bool>(out);
        }
        return std::nullopt;
    }
    /** Check if a custom attribute exists. */
    bool has_custom_attr(const std::string& name) const {
        return fdl_canvas_template_has_custom_attr(ct_, name.c_str()) != 0;
    }
    /** Get the type of a custom attribute. */
    fdl_custom_attr_type_t get_custom_attr_type(const std::string& name) const {
        return fdl_canvas_template_get_custom_attr_type(ct_, name.c_str());
    }
    /** Remove a custom attribute. Returns true if removed. */
    bool remove_custom_attr(const std::string& name) {
        return fdl_canvas_template_remove_custom_attr(ct_, name.c_str()) == 0;
    }
    /** Return the number of custom attributes. */
    uint32_t custom_attrs_count() const { return fdl_canvas_template_custom_attrs_count(ct_); }
    /** Return the name of the custom attribute at the given index. */
    std::string custom_attr_name_at(uint32_t index) const {
        const char* p = fdl_canvas_template_custom_attr_name_at(ct_, index);
        return p ? std::string(p) : std::string();
    }
    /** @brief Set a PointFloat custom attribute. */
    int set_custom_attr(const std::string& name, PointFloat value) {
        fdl_point_f64_t c{value.x(), value.y()};
        return fdl_canvas_template_set_custom_attr_point_f64(ct_, name.c_str(), c);
    }
    /** @brief Set a DimensionsFloat custom attribute. */
    int set_custom_attr(const std::string& name, DimensionsFloat value) {
        fdl_dimensions_f64_t c{value.width(), value.height()};
        return fdl_canvas_template_set_custom_attr_dims_f64(ct_, name.c_str(), c);
    }
    /** @brief Set a DimensionsInt custom attribute. */
    int set_custom_attr(const std::string& name, DimensionsInt value) {
        fdl_dimensions_i64_t c{value.width(), value.height()};
        return fdl_canvas_template_set_custom_attr_dims_i64(ct_, name.c_str(), c);
    }
    /** @brief Get a PointFloat custom attribute. */
    std::optional<PointFloat> get_custom_attr_point_f64(const std::string& name) const {
        fdl_point_f64_t out{};
        if (fdl_canvas_template_get_custom_attr_point_f64(ct_, name.c_str(), &out) != 0) {
            return std::nullopt;
        }
        return PointFloat(out.x, out.y);
    }
    /** @brief Get a DimensionsFloat custom attribute. */
    std::optional<DimensionsFloat> get_custom_attr_dims_f64(const std::string& name) const {
        fdl_dimensions_f64_t out{};
        if (fdl_canvas_template_get_custom_attr_dims_f64(ct_, name.c_str(), &out) != 0) {
            return std::nullopt;
        }
        return DimensionsFloat(out.width, out.height);
    }
    /** @brief Get a DimensionsInt custom attribute. */
    std::optional<DimensionsInt> get_custom_attr_dims_i64(const std::string& name) const {
        fdl_dimensions_i64_t out{};
        if (fdl_canvas_template_get_custom_attr_dims_i64(ct_, name.c_str(), &out) != 0) {
            return std::nullopt;
        }
        return DimensionsInt(out.width, out.height);
    }

    fdl_canvas_template_t* get() const noexcept { return ct_; }

private:
    fdl_canvas_template_t* ct_;
};

// -----------------------------------------------------------------------
// ClipIDRef — non-owning
// -----------------------------------------------------------------------
class ClipIDRef {
public:
    explicit ClipIDRef(fdl_clip_id_t* handle) noexcept : cid_(handle) {}

    // --- Property accessors ---
    std::string clip_name() const {
        const char* p = fdl_clip_id_get_clip_name(cid_);
        return p ? std::string(p) : std::string();
    }

    bool has_file() const { return fdl_clip_id_has_file(cid_) != 0; }
    std::optional<std::string> file() const {
        if (!fdl_clip_id_has_file(cid_)) {
            return std::nullopt;
        }
        const char* p = fdl_clip_id_get_file(cid_);
        return p ? std::optional<std::string>(p) : std::nullopt;
    }

    bool has_sequence() const { return fdl_clip_id_has_sequence(cid_) != 0; }
    std::optional<FileSequenceRef> sequence() const;

    // --- Collection traversal ---

    /** Serialize to canonical JSON string. */
    std::string to_json(int indent = 2) const {
        char* ptr = fdl_clip_id_to_json(cid_, indent);
        if (!ptr) {
            throw std::runtime_error("fdl_clip_id_to_json returned NULL");
        }
        std::string json(ptr);
        fdl_free(ptr);
        return json;
    }

    // --- Builder methods ---

    // --- Lifecycle methods ---
    /** Validate this clip_id for mutual exclusion rules. */
    void validate() const {
        auto json = to_json(0);
        const char* err = ::fdl_clip_id_validate_json(json.c_str(), json.size());
        if (err) {
            std::string msg(err);
            fdl_free(const_cast<char*>(err));
            throw std::runtime_error(msg);
        }
    }

    // --- Custom attributes ---

    /** Set a string custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, const std::string& value) {
        return fdl_clip_id_set_custom_attr_string(cid_, name.c_str(), value.c_str());
    }
    /** Set an integer custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, int64_t value) {
        return fdl_clip_id_set_custom_attr_int(cid_, name.c_str(), value);
    }
    /** Set a float custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, double value) {
        return fdl_clip_id_set_custom_attr_float(cid_, name.c_str(), value);
    }
    /** Set a boolean custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, bool value) {
        return fdl_clip_id_set_custom_attr_bool(cid_, name.c_str(), value ? FDL_TRUE : FDL_FALSE);
    }
    /** Get a string custom attribute. */
    std::optional<std::string> get_custom_attr_string(const std::string& name) const {
        const char* p = fdl_clip_id_get_custom_attr_string(cid_, name.c_str());
        return p ? std::optional<std::string>(p) : std::nullopt;
    }
    /** Get an integer custom attribute. */
    std::optional<int64_t> get_custom_attr_int(const std::string& name) const {
        int64_t out;
        if (fdl_clip_id_get_custom_attr_int(cid_, name.c_str(), &out) == 0) {
            return out;
        }
        return std::nullopt;
    }
    /** Get a float custom attribute. */
    std::optional<double> get_custom_attr_float(const std::string& name) const {
        double out;
        if (fdl_clip_id_get_custom_attr_float(cid_, name.c_str(), &out) == 0) {
            return out;
        }
        return std::nullopt;
    }
    /** Get a boolean custom attribute. */
    std::optional<bool> get_custom_attr_bool(const std::string& name) const {
        int out;
        if (fdl_clip_id_get_custom_attr_bool(cid_, name.c_str(), &out) == 0) {
            return static_cast<bool>(out);
        }
        return std::nullopt;
    }
    /** Check if a custom attribute exists. */
    bool has_custom_attr(const std::string& name) const { return fdl_clip_id_has_custom_attr(cid_, name.c_str()) != 0; }
    /** Get the type of a custom attribute. */
    fdl_custom_attr_type_t get_custom_attr_type(const std::string& name) const {
        return fdl_clip_id_get_custom_attr_type(cid_, name.c_str());
    }
    /** Remove a custom attribute. Returns true if removed. */
    bool remove_custom_attr(const std::string& name) { return fdl_clip_id_remove_custom_attr(cid_, name.c_str()) == 0; }
    /** Return the number of custom attributes. */
    uint32_t custom_attrs_count() const { return fdl_clip_id_custom_attrs_count(cid_); }
    /** Return the name of the custom attribute at the given index. */
    std::string custom_attr_name_at(uint32_t index) const {
        const char* p = fdl_clip_id_custom_attr_name_at(cid_, index);
        return p ? std::string(p) : std::string();
    }
    /** @brief Set a PointFloat custom attribute. */
    int set_custom_attr(const std::string& name, PointFloat value) {
        fdl_point_f64_t c{value.x(), value.y()};
        return fdl_clip_id_set_custom_attr_point_f64(cid_, name.c_str(), c);
    }
    /** @brief Set a DimensionsFloat custom attribute. */
    int set_custom_attr(const std::string& name, DimensionsFloat value) {
        fdl_dimensions_f64_t c{value.width(), value.height()};
        return fdl_clip_id_set_custom_attr_dims_f64(cid_, name.c_str(), c);
    }
    /** @brief Set a DimensionsInt custom attribute. */
    int set_custom_attr(const std::string& name, DimensionsInt value) {
        fdl_dimensions_i64_t c{value.width(), value.height()};
        return fdl_clip_id_set_custom_attr_dims_i64(cid_, name.c_str(), c);
    }
    /** @brief Get a PointFloat custom attribute. */
    std::optional<PointFloat> get_custom_attr_point_f64(const std::string& name) const {
        fdl_point_f64_t out{};
        if (fdl_clip_id_get_custom_attr_point_f64(cid_, name.c_str(), &out) != 0) {
            return std::nullopt;
        }
        return PointFloat(out.x, out.y);
    }
    /** @brief Get a DimensionsFloat custom attribute. */
    std::optional<DimensionsFloat> get_custom_attr_dims_f64(const std::string& name) const {
        fdl_dimensions_f64_t out{};
        if (fdl_clip_id_get_custom_attr_dims_f64(cid_, name.c_str(), &out) != 0) {
            return std::nullopt;
        }
        return DimensionsFloat(out.width, out.height);
    }
    /** @brief Get a DimensionsInt custom attribute. */
    std::optional<DimensionsInt> get_custom_attr_dims_i64(const std::string& name) const {
        fdl_dimensions_i64_t out{};
        if (fdl_clip_id_get_custom_attr_dims_i64(cid_, name.c_str(), &out) != 0) {
            return std::nullopt;
        }
        return DimensionsInt(out.width, out.height);
    }

    fdl_clip_id_t* get() const noexcept { return cid_; }

private:
    fdl_clip_id_t* cid_;
};

// -----------------------------------------------------------------------
// FileSequenceRef — non-owning
// -----------------------------------------------------------------------
class FileSequenceRef {
public:
    explicit FileSequenceRef(fdl_file_sequence_t* handle) noexcept : seq_(handle) {}

    // --- Property accessors ---
    std::string value() const {
        const char* p = fdl_file_sequence_get_value(seq_);
        return p ? std::string(p) : std::string();
    }

    std::string idx() const {
        const char* p = fdl_file_sequence_get_idx(seq_);
        return p ? std::string(p) : std::string();
    }

    int64_t min() const { return fdl_file_sequence_get_min(seq_); }

    int64_t max() const { return fdl_file_sequence_get_max(seq_); }

    // --- Collection traversal ---

    // --- Builder methods ---

    // --- Custom attributes ---

    /** Set a string custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, const std::string& value) {
        return fdl_file_sequence_set_custom_attr_string(seq_, name.c_str(), value.c_str());
    }
    /** Set an integer custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, int64_t value) {
        return fdl_file_sequence_set_custom_attr_int(seq_, name.c_str(), value);
    }
    /** Set a float custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, double value) {
        return fdl_file_sequence_set_custom_attr_float(seq_, name.c_str(), value);
    }
    /** Set a boolean custom attribute. Returns 0 on success, -1 on type mismatch. */
    int set_custom_attr(const std::string& name, bool value) {
        return fdl_file_sequence_set_custom_attr_bool(seq_, name.c_str(), value ? FDL_TRUE : FDL_FALSE);
    }
    /** Get a string custom attribute. */
    std::optional<std::string> get_custom_attr_string(const std::string& name) const {
        const char* p = fdl_file_sequence_get_custom_attr_string(seq_, name.c_str());
        return p ? std::optional<std::string>(p) : std::nullopt;
    }
    /** Get an integer custom attribute. */
    std::optional<int64_t> get_custom_attr_int(const std::string& name) const {
        int64_t out;
        if (fdl_file_sequence_get_custom_attr_int(seq_, name.c_str(), &out) == 0) {
            return out;
        }
        return std::nullopt;
    }
    /** Get a float custom attribute. */
    std::optional<double> get_custom_attr_float(const std::string& name) const {
        double out;
        if (fdl_file_sequence_get_custom_attr_float(seq_, name.c_str(), &out) == 0) {
            return out;
        }
        return std::nullopt;
    }
    /** Get a boolean custom attribute. */
    std::optional<bool> get_custom_attr_bool(const std::string& name) const {
        int out;
        if (fdl_file_sequence_get_custom_attr_bool(seq_, name.c_str(), &out) == 0) {
            return static_cast<bool>(out);
        }
        return std::nullopt;
    }
    /** Check if a custom attribute exists. */
    bool has_custom_attr(const std::string& name) const {
        return fdl_file_sequence_has_custom_attr(seq_, name.c_str()) != 0;
    }
    /** Get the type of a custom attribute. */
    fdl_custom_attr_type_t get_custom_attr_type(const std::string& name) const {
        return fdl_file_sequence_get_custom_attr_type(seq_, name.c_str());
    }
    /** Remove a custom attribute. Returns true if removed. */
    bool remove_custom_attr(const std::string& name) {
        return fdl_file_sequence_remove_custom_attr(seq_, name.c_str()) == 0;
    }
    /** Return the number of custom attributes. */
    uint32_t custom_attrs_count() const { return fdl_file_sequence_custom_attrs_count(seq_); }
    /** Return the name of the custom attribute at the given index. */
    std::string custom_attr_name_at(uint32_t index) const {
        const char* p = fdl_file_sequence_custom_attr_name_at(seq_, index);
        return p ? std::string(p) : std::string();
    }
    /** @brief Set a PointFloat custom attribute. */
    int set_custom_attr(const std::string& name, PointFloat value) {
        fdl_point_f64_t c{value.x(), value.y()};
        return fdl_file_sequence_set_custom_attr_point_f64(seq_, name.c_str(), c);
    }
    /** @brief Set a DimensionsFloat custom attribute. */
    int set_custom_attr(const std::string& name, DimensionsFloat value) {
        fdl_dimensions_f64_t c{value.width(), value.height()};
        return fdl_file_sequence_set_custom_attr_dims_f64(seq_, name.c_str(), c);
    }
    /** @brief Set a DimensionsInt custom attribute. */
    int set_custom_attr(const std::string& name, DimensionsInt value) {
        fdl_dimensions_i64_t c{value.width(), value.height()};
        return fdl_file_sequence_set_custom_attr_dims_i64(seq_, name.c_str(), c);
    }
    /** @brief Get a PointFloat custom attribute. */
    std::optional<PointFloat> get_custom_attr_point_f64(const std::string& name) const {
        fdl_point_f64_t out{};
        if (fdl_file_sequence_get_custom_attr_point_f64(seq_, name.c_str(), &out) != 0) {
            return std::nullopt;
        }
        return PointFloat(out.x, out.y);
    }
    /** @brief Get a DimensionsFloat custom attribute. */
    std::optional<DimensionsFloat> get_custom_attr_dims_f64(const std::string& name) const {
        fdl_dimensions_f64_t out{};
        if (fdl_file_sequence_get_custom_attr_dims_f64(seq_, name.c_str(), &out) != 0) {
            return std::nullopt;
        }
        return DimensionsFloat(out.width, out.height);
    }
    /** @brief Get a DimensionsInt custom attribute. */
    std::optional<DimensionsInt> get_custom_attr_dims_i64(const std::string& name) const {
        fdl_dimensions_i64_t out{};
        if (fdl_file_sequence_get_custom_attr_dims_i64(seq_, name.c_str(), &out) != 0) {
            return std::nullopt;
        }
        return DimensionsInt(out.width, out.height);
    }

    fdl_file_sequence_t* get() const noexcept { return seq_; }

private:
    fdl_file_sequence_t* seq_;
};

// -----------------------------------------------------------------------
// ResolveCanvasResult
// -----------------------------------------------------------------------
struct ResolveCanvasResult {
    CanvasRef canvas;
    FramingDecisionRef framing_decision;
    bool was_resolved;
};

// -----------------------------------------------------------------------
// Inline implementations requiring full class definitions
// -----------------------------------------------------------------------

// --- Collection traversal ---
inline ContextRef FDL::context_at(uint32_t i) const {
    return ContextRef(fdl_doc_context_at(doc_, i));
}

inline ContextRef FDL::context_find_by_label(const std::string& label) const {
    return ContextRef(fdl_doc_context_find_by_label(doc_, label.c_str()));
}

inline FramingIntentRef FDL::framing_intent_at(uint32_t i) const {
    return FramingIntentRef(fdl_doc_framing_intent_at(doc_, i));
}

inline FramingIntentRef FDL::framing_intent_find_by_id(const std::string& id) const {
    return FramingIntentRef(fdl_doc_framing_intent_find_by_id(doc_, id.c_str()));
}

inline CanvasTemplateRef FDL::canvas_template_at(uint32_t i) const {
    return CanvasTemplateRef(fdl_doc_canvas_template_at(doc_, i));
}

inline CanvasTemplateRef FDL::canvas_template_find_by_id(const std::string& id) const {
    return CanvasTemplateRef(fdl_doc_canvas_template_find_by_id(doc_, id.c_str()));
}

inline CanvasRef ContextRef::canvas_at(uint32_t i) const {
    return CanvasRef(fdl_context_canvas_at(ctx_, i));
}

inline CanvasRef ContextRef::canvas_find_by_id(const std::string& id) const {
    return CanvasRef(fdl_context_find_canvas_by_id(ctx_, id.c_str()));
}

inline FramingDecisionRef CanvasRef::framing_decision_at(uint32_t i) const {
    return FramingDecisionRef(fdl_canvas_framing_decision_at(canvas_, i));
}

inline FramingDecisionRef CanvasRef::framing_decision_find_by_id(const std::string& id) const {
    return FramingDecisionRef(fdl_canvas_find_framing_decision_by_id(canvas_, id.c_str()));
}

// --- Handle-ref property implementations ---
inline std::optional<ClipIDRef> ContextRef::clip_id() const {
    if (!fdl_context_has_clip_id(ctx_)) {
        return std::nullopt;
    }
    auto* h = fdl_context_clip_id(ctx_);
    if (!h) {
        return std::nullopt;
    }
    return ClipIDRef(h);
}

inline std::optional<FileSequenceRef> ClipIDRef::sequence() const {
    if (!fdl_clip_id_has_sequence(cid_)) {
        return std::nullopt;
    }
    auto* h = fdl_clip_id_sequence(cid_);
    if (!h) {
        return std::nullopt;
    }
    return FileSequenceRef(h);
}

// --- Builder implementations ---
inline FramingIntentRef FDL::add_framing_intent(
    const std::string& id, const std::string& label, const fdl_dimensions_i64_t& aspect_ratio, double protection) {
    auto* handle = fdl_doc_add_framing_intent(
        doc_, id.c_str(), label.c_str(), aspect_ratio.width, aspect_ratio.height, protection);
    if (!handle) {
        throw std::runtime_error("fdl_doc_add_framing_intent returned NULL");
    }
    return FramingIntentRef(handle);
}

inline ContextRef FDL::add_context(const std::string& label, const std::string& context_creator) {
    auto* handle =
        fdl_doc_add_context(doc_, label.c_str(), context_creator.empty() ? nullptr : context_creator.c_str());
    if (!handle) {
        throw std::runtime_error("fdl_doc_add_context returned NULL");
    }
    return ContextRef(handle);
}

inline CanvasTemplateRef FDL::add_canvas_template(
    const std::string& id,
    const std::string& label,
    const fdl_dimensions_i64_t& target_dimensions,
    double target_anamorphic_squeeze,
    fdl_geometry_path_t fit_source,
    fdl_fit_method_t fit_method,
    fdl_halign_t alignment_method_horizontal,
    fdl_valign_t alignment_method_vertical,
    const fdl_round_strategy_t& round) {
    auto* handle = fdl_doc_add_canvas_template(
        doc_,
        id.c_str(),
        label.c_str(),
        target_dimensions.width,
        target_dimensions.height,
        target_anamorphic_squeeze,
        fit_source,
        fit_method,
        alignment_method_horizontal,
        alignment_method_vertical,
        round);
    if (!handle) {
        throw std::runtime_error("fdl_doc_add_canvas_template returned NULL");
    }
    return CanvasTemplateRef(handle);
}

inline CanvasRef ContextRef::add_canvas(
    const std::string& id,
    const std::string& label,
    const std::string& source_canvas_id,
    const fdl_dimensions_i64_t& dimensions,
    double anamorphic_squeeze) {
    auto* handle = fdl_context_add_canvas(
        ctx_,
        id.c_str(),
        label.c_str(),
        source_canvas_id.c_str(),
        dimensions.width,
        dimensions.height,
        anamorphic_squeeze);
    if (!handle) {
        throw std::runtime_error("fdl_context_add_canvas returned NULL");
    }
    return CanvasRef(handle);
}

inline ::fdl::ResolveCanvasResult ContextRef::resolve_canvas_for_dimensions(
    const fdl_dimensions_f64_t& input_dims, const CanvasRef& canvas, const FramingDecisionRef& framing) const {
    auto result = fdl_context_resolve_canvas_for_dimensions(ctx_, input_dims, canvas.get(), framing.get());

    if (result.error) {
        std::string msg(result.error);
        fdl_free(const_cast<char*>(result.error));
        throw std::runtime_error(msg);
    }

    return ResolveCanvasResult{
        CanvasRef(result.canvas), FramingDecisionRef(result.framing_decision), result.was_resolved != 0};
}

inline FramingDecisionRef CanvasRef::add_framing_decision(
    const std::string& id,
    const std::string& label,
    const std::string& framing_intent_id,
    const fdl_dimensions_f64_t& dimensions,
    const fdl_point_f64_t& anchor_point) {
    auto* handle = fdl_canvas_add_framing_decision(
        canvas_,
        id.c_str(),
        label.c_str(),
        framing_intent_id.c_str(),
        dimensions.width,
        dimensions.height,
        anchor_point.x,
        anchor_point.y);
    if (!handle) {
        throw std::runtime_error("fdl_canvas_add_framing_decision returned NULL");
    }
    return FramingDecisionRef(handle);
}

inline void CanvasRef::set_effective(const fdl_dimensions_i64_t& dims, const fdl_point_f64_t& anchor) {
    fdl_canvas_set_effective_dimensions(canvas_, dims, anchor);
}

inline void FramingDecisionRef::set_protection(const fdl_dimensions_f64_t& dims, const fdl_point_f64_t& anchor) {
    fdl_framing_decision_set_protection(fd_, dims, anchor);
}

inline void FramingDecisionRef::adjust_anchor_point(
    const CanvasRef& canvas, fdl_halign_t h_method, fdl_valign_t v_method) {
    fdl_framing_decision_adjust_anchor(fd_, canvas.get(), h_method, v_method);
}

inline void FramingDecisionRef::adjust_protection_anchor_point(
    const CanvasRef& canvas, fdl_halign_t h_method, fdl_valign_t v_method) {
    fdl_framing_decision_adjust_protection_anchor(fd_, canvas.get(), h_method, v_method);
}

inline void FramingDecisionRef::from_framing_intent(
    const CanvasRef& canvas, const FramingIntentRef& framing_intent, const fdl_round_strategy_t& rounding) {
    fdl_framing_decision_populate_from_intent(fd_, canvas.get(), framing_intent.get(), rounding);
}

inline void FramingDecisionRef::populate_from_intent(
    const CanvasRef& canvas, const FramingIntentRef& framing_intent, const fdl_round_strategy_t& rounding) {
    fdl_framing_decision_populate_from_intent(fd_, canvas.get(), framing_intent.get(), rounding);
}

inline ::fdl::TemplateResult CanvasTemplateRef::apply(
    const CanvasRef& source_canvas,
    const FramingDecisionRef& source_framing,
    const std::string& new_canvas_id,
    const std::string& new_fd_name,
    const std::string& source_context_label,
    const std::string& context_creator) const {
    auto result = fdl_apply_canvas_template(
        ct_,
        source_canvas.get(),
        source_framing.get(),
        new_canvas_id.c_str(),
        new_fd_name.c_str(),
        source_context_label.empty() ? nullptr : source_context_label.c_str(),
        context_creator.empty() ? nullptr : context_creator.c_str());

    if (result.error) {
        std::string msg(result.error);
        fdl_free(const_cast<char*>(result.error));
        if (result.output_fdl) {
            fdl_doc_free(result.output_fdl);
        }
        if (result.context_label) {
            fdl_free(const_cast<char*>(result.context_label));
        }
        if (result.canvas_id) {
            fdl_free(const_cast<char*>(result.canvas_id));
        }
        if (result.framing_decision_id) {
            fdl_free(const_cast<char*>(result.framing_decision_id));
        }
        throw std::runtime_error(msg);
    }

    return TemplateResult{
        FDL(result.output_fdl),
        [&] {
            std::string s(result.context_label);
            fdl_free(const_cast<char*>(result.context_label));
            return s;
        }(),
        [&] {
            std::string s(result.canvas_id);
            fdl_free(const_cast<char*>(result.canvas_id));
            return s;
        }(),
        [&] {
            std::string s(result.framing_decision_id);
            fdl_free(const_cast<char*>(result.framing_decision_id));
            return s;
        }()};
}

// --- TemplateResult accessor implementations ---
inline ContextRef TemplateResult::context() const {
    return fdl.context_find_by_label(_context_label);
}
inline CanvasRef TemplateResult::canvas() const {
    return context().canvas_find_by_id(_canvas_id);
}
inline FramingDecisionRef TemplateResult::framing_decision() const {
    return canvas().framing_decision_find_by_id(_framing_decision_id);
}

// --- Value type deferred method implementations ---
inline DimensionsFloat DimensionsInt::normalize(double squeeze) const {
    return DimensionsFloat(::fdl_dimensions_i64_normalize(data_, squeeze));
}

inline bool DimensionsInt::operator==(const DimensionsFloat& other) const {
    return ::fdl_dimensions_equal(fdl_dimensions_f64_t{(double)data_.width, (double)data_.height}, other.raw()) != 0;
}

inline std::pair<DimensionsFloat, PointFloat> DimensionsFloat::clamp_to_dims(const DimensionsFloat& clamp_dims) const {
    fdl_point_f64_t _out_delta;
    auto _r = ::fdl_dimensions_clamp_to_dims(data_, clamp_dims, &_out_delta);
    return {DimensionsFloat(_r), PointFloat(_out_delta)};
}

inline bool DimensionsFloat::operator==(const DimensionsInt& other) const {
    return ::fdl_dimensions_equal(data_, fdl_dimensions_f64_t{(double)other.raw().width, (double)other.raw().height}) !=
           0;
}

// --- Free functions ---
/** Round a single float value according to FDL rounding rules. */
inline int64_t round(double value, fdl_rounding_even_t even, fdl_rounding_mode_t mode) {
    return ::fdl_round(value, even, mode);
}

/** Calculate scale factor based on fit method. */
inline double calculate_scale_factor(
    const DimensionsFloat& fit_norm, const DimensionsFloat& target_norm, fdl_fit_method_t fit_method) {
    return ::fdl_calculate_scale_factor(fit_norm, target_norm, fit_method);
}

/** Return the ABI version of the loaded library as (major, minor, patch). */
inline fdl_abi_version_t abi_version() {
    return ::fdl_abi_version();
}

/** Compute a framing decision from a framing intent without needing existing handles. */
inline fdl_from_intent_result_t compute_framing_from_intent(
    const DimensionsFloat& canvas_dims,
    const DimensionsFloat& working_dims,
    double squeeze,
    const DimensionsInt& aspect_ratio,
    double protection,
    const fdl_round_strategy_t& rounding) {
    return ::fdl_compute_framing_from_intent(canvas_dims, working_dims, squeeze, aspect_ratio, protection, rounding);
}

/** Create a rect from raw coordinates. */
inline fdl_rect_t make_rect(double x, double y, double width, double height) {
    return ::fdl_make_rect(x, y, width, height);
}

// --- Utility functions ---

/** Result of resolve_geometry_layer: dimensions + anchor from a geometry path. */
struct ResolvedLayer {
    DimensionsFloat dimensions;
    PointFloat anchor;
};

/** Get dimensions from a canvas or framing decision using a GeometryPath string. */
inline std::optional<ResolvedLayer> resolve_geometry_layer(
    const CanvasRef& canvas, const FramingDecisionRef& framing, fdl_geometry_path_t path) {
    fdl_dimensions_f64_t dims;
    fdl_point_f64_t anchor;
    int rc = ::fdl_resolve_geometry_layer(canvas.get(), framing.get(), path, &dims, &anchor);
    if (rc != 0) {
        return std::nullopt;
    }
    return ResolvedLayer{DimensionsFloat(dims), PointFloat(anchor)};
}

// --- I/O convenience functions ---

/** Parse an FDL document from a JSON string.
 *  @param json     JSON string to parse.
 *  @param validate Run schema + semantic validation after parsing (default true).
 *  @return Parsed FDL document.
 *  @throws std::runtime_error on parse failure or validation errors.
 */
inline FDL read_from_string(const std::string& json, bool validate = true) {
    auto doc = FDL::parse(json);
    if (validate) {
        auto errors = doc.validate();
        if (!errors.empty()) {
            std::string msg;
            for (size_t i = 0; i < errors.size(); ++i) {
                if (i > 0) {
                    msg += "; ";
                }
                msg += errors[i];
            }
            throw std::runtime_error(msg);
        }
    }
    return doc;
}

/** Read an FDL document from a file on disk.
 *  @param path     Path to the FDL file.
 *  @param validate Run schema + semantic validation after parsing (default true).
 *  @return Parsed FDL document.
 *  @throws std::runtime_error if the file cannot be opened, or on parse/validation errors.
 */
inline FDL read_from_file(const std::string& path, bool validate = true) {
    std::ifstream ifs(path, std::ios::binary);
    if (!ifs) {
        throw std::runtime_error("File not found: " + path);
    }
    std::string json((std::istreambuf_iterator<char>(ifs)), std::istreambuf_iterator<char>());
    return read_from_string(json, validate);
}

/** Serialize an FDL document to a JSON string.
 *  @param doc      The FDL document to serialize.
 *  @param validate Run schema + semantic validation before serializing (default true).
 *  @return JSON string.
 *  @throws std::runtime_error on validation errors.
 */
inline std::string write_to_string(const FDL& doc, bool validate = true) {
    if (validate) {
        auto errors = doc.validate();
        if (!errors.empty()) {
            std::string msg;
            for (size_t i = 0; i < errors.size(); ++i) {
                if (i > 0) {
                    msg += "; ";
                }
                msg += errors[i];
            }
            throw std::runtime_error(msg);
        }
    }
    return doc.as_json();
}

/** Write an FDL document to a file on disk.
 *  @param doc      The FDL document to serialize.
 *  @param path     Destination file path.
 *  @param validate Run schema + semantic validation before writing (default true).
 *  @throws std::runtime_error on validation errors or if the file cannot be opened.
 */
inline void write_to_file(const FDL& doc, const std::string& path, bool validate = true) {
    std::string json = write_to_string(doc, validate);
    std::ofstream ofs(path, std::ios::binary);
    if (!ofs) {
        throw std::runtime_error("Cannot open file for writing: " + path);
    }
    ofs.write(json.data(), static_cast<std::streamsize>(json.size()));
}

} // namespace fdl

#endif // FDL_HPP

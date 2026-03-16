// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_validate.h
 * @brief Internal validation — JSON Schema + semantic checks.
 *
 * Schema validation (Draft 2020-12) runs first using embedded schema data.
 * Semantic validators (referential integrity, value range checks) run only
 * if the document passes schema validation.
 */
#ifndef FDL_VALIDATE_INTERNAL_H
#define FDL_VALIDATE_INTERNAL_H

#include <jsoncons/json.hpp>
#include <string>
#include <vector>

namespace fdl::detail {

using ojson = jsoncons::ojson;

/** Result of schema + semantic validation. */
struct ValidationResult {
    std::vector<std::string> errors; /**< Error messages (empty = valid). */
};

/**
 * Run schema validation followed by semantic validators.
 *
 * Schema errors are prefixed with "Schema Error:".
 * Semantic errors are only run if schema validation passes.
 *
 * @param fdl  JSON document to validate.
 * @return Validation result with collected errors.
 */
ValidationResult validate(const ojson& fdl);

} // namespace fdl::detail

#endif // FDL_VALIDATE_INTERNAL_H

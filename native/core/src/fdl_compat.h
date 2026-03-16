// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_compat.h
 * @brief Cross-platform portability macros.
 *
 * Provides fdl_strdup as a portable wrapper for strdup (POSIX) / _strdup (MSVC).
 */
#ifndef FDL_COMPAT_H
#define FDL_COMPAT_H

#include <cstring>

#ifdef _MSC_VER
#define fdl_strdup _strdup /**< MSVC-compatible strdup. */
#else
#define fdl_strdup strdup /**< POSIX strdup. */
#endif

#endif // FDL_COMPAT_H

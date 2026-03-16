// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_tl_cache.h
 * @brief Bounded thread-local string cache with automatic eviction.
 *
 * Provides a simple size-bounded wrapper around std::unordered_map that
 * auto-clears when the entry count exceeds a threshold.  This prevents
 * unbounded memory growth in long-running threads that access many
 * different documents or nodes.
 *
 * The eviction strategy is a full clear (rather than LRU) because:
 * - Entries are only string caches, not correctness-critical data.
 * - The cost of repopulation is a single string copy per subsequent access.
 * - A full clear is cheaper than LRU bookkeeping for these small strings.
 */
#ifndef FDL_TL_CACHE_H
#define FDL_TL_CACHE_H

#include <string>
#include <unordered_map>

#include "fdl_constants.h"

namespace fdl::detail {

/**
 * @brief Bounded thread-local string cache with auto-eviction.
 *
 * When the number of cached entries reaches @c fdl::constants::kTlCacheMaxEntries,
 * the cache is cleared entirely before the new entry is inserted.
 *
 * @tparam Key   Cache key type (must be hashable and equality-comparable).
 * @tparam Hash  Hash functor for @p Key.
 */
template<typename Key, typename Hash> class TlStringCache {
public:
    /**
     * @brief Get or create a cached string entry for the given key.
     *
     * If the cache exceeds the size limit, it is cleared first.
     * The returned reference is valid until the next call to get() that
     * triggers eviction.
     *
     * @param key  The cache key to look up.
     * @return Reference to the cached string (may be empty if newly created).
     */
    std::string& get(const Key& key) {
        if (map_.size() >= fdl::constants::kTlCacheMaxEntries) {
            map_.clear();
        }
        return map_[key];
    }

private:
    std::unordered_map<Key, std::string, Hash> map_;
};

} // namespace fdl::detail

#endif // FDL_TL_CACHE_H

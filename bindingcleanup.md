# Binding Cleanup Plan

## Goal
Reduce custom per-language templating drift while preserving the C ABI boundary by design.

## Current Findings
- The C ABI contract is clean and should remain the source of truth:
  - `native/core/include/fdl/fdl_core.h`
  - `native/api/fdl_api.yaml` function list is currently aligned.
- Codegen has hidden language coupling:
  - "Language-neutral" layers import Python maps and Python converter names.
  - C++ generation depends on Python-shaped context (`python_type`) then remaps.
  - IDL contains Python-specific defaults/metadata in shared sections.
- Build/CI does not enforce regeneration drift for bindings.

## Constraints
- Keep C ABI stable and explicit.
- Do not break existing C++, Python user-facing API behavior during cleanup.
- Future Node.js bindings must consume the same semantic model, not ad-hoc templates.
- Every step must pass all linting gates (Ruff for Python, clang-format + clang-tidy for C++).
- Generated C++ headers must maintain Doxygen documentation (Javadoc-style `/** */`).
  Verify with `cd native/core && doxygen Doxyfile` — no undocumented warnings
  (`WARN_IF_UNDOCUMENTED=YES`, `WARN_NO_PARAMDOC=YES` are already strict in Doxyfile).
- Python docstrings in generated facade code must stay accurate through refactoring.

## Target Architecture
- `fdl_core.h` + ABI policy = hard contract.
- `fdl_api.yaml` = semantic API metadata.
- New language-neutral IR = only type keys + semantic ops, no Python/C++ strings.
- Per-language backends:
  - Python backend
  - C++ RAII backend
  - Node backend (future)
- Thin language templates that consume normalized IR.

## Work Plan

### Phase 1: Stabilize Contracts
1. Add ABI compliance gate:
   - Introduce ABI check tooling in CI for `fdl_core` shared library.
   - Fail CI on unintended ABI surface changes.
2. Add codegen drift gate:
   - Add a `codegen check` target that regenerates and verifies zero diff.
   - Run for Python FFI, Python facade, and C++ RAII outputs.

### Phase 2: Decouple Shared IR from Python
1. Remove Python-specific converter injection from IR construction.
2. Move converter/type naming to language adapters only.
3. Replace `python_type`/Python defaults in shared paths with neutral forms:
   - `type_key`
   - structured enum/default tokens
   - structured result field metadata (language-agnostic)

### Phase 3: Normalize Codegen Data Model
1. Define normalized intermediate schema:
   - `classes`, `properties`, `collections`, `methods`, `error_patterns`, `result_fields`.
2. Normalize defaults:
   - Replace string defaults like `FitMethod.WIDTH` with typed default descriptors.
3. Normalize conversion rules:
   - `in_conv`, `out_conv`, `expand`, `nullable`, `ownership` expressed as neutral flags.

### Phase 4: Refactor Generators
1. Python generator:
   - Consume normalized IR via Python adapter layer.
   - Keep current generated API surface unchanged.
2. C++ generator:
   - Stop depending on Python annotations; use neutral IR + C++ adapter map only.
3. Keep templates minimal:
   - Push branchy logic out of templates into backend code.

### Phase 5: Add Node Binding Foundation
1. Add `--target node` entrypoint in generator dispatcher.
2. Use Node-API (`node-addon-api`) backend:
   - ABI-stable JS/C++ boundary
   - generated wrappers around existing C ABI.
3. Start with low-level parity:
   - lifecycle, accessors, collections, template apply path.
4. Add higher-level JS facade incrementally after low-level API tests pass.

### Quality Gates (applies to every step)
1. Linting must pass:
   - `ruff check && ruff format --check` (Python codegen + generated output)
   - `clang-format --dry-run --Werror` (generated C++ headers)
   - `clang-tidy` (generated C++ against compile_commands.json)
2. Doxygen must build cleanly:
   - `cd native/core && doxygen Doxyfile 2>&1 | grep -c warning` should be 0
   - Generated C++ RAII headers (`native/bindings/cpp/fdl/`) carry `@brief`, `@param`, `@return` tags
3. Generated output must be byte-identical (codegen drift gate)

### Phase 6: Test and Validation Matrix
1. Cross-language parity tests driven by shared vectors:
   - Existing template/geometry/pipeline vectors become canonical fixtures.
2. Add generated-surface smoke tests per target:
   - function presence
   - enum mapping
   - error/result semantics
3. Add regression tests for nullable/default/ownership edge cases.

## Deliverables
- `codegen check` command + CI enforcement.
- Refactored neutral IR module and adapters.
- Updated Python and C++ generators using neutral IR.
- Initial Node generator scaffolding + smoke tests.
- Migration notes for contributors.

## Risks and Mitigations
- Risk: behavior drift during IR refactor.
  - Mitigation: golden vector parity tests before/after each phase.
- Risk: generated API breaking changes.
  - Mitigation: surface snapshot tests and semantic version gates.
- Risk: Node backend complexity.
  - Mitigation: phased rollout (low-level first, facade second).

## Immediate Next Steps
1. Implement `codegen check` and wire it into CI.
2. Introduce neutral IR types and adapter interface.
3. Migrate one vertical slice end-to-end (for example `CanvasTemplate.apply`) to validate design before full migration.

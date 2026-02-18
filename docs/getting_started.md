# Getting Started

## Loading & Saving an FDL

The `read_from_file()` and `write_to_file()` functions validate by default, so
the simplest workflow is:

=== "Python"

    ```python
    import fdl
    from fdl import read_from_file, write_to_file
    from pathlib import Path
    from tempfile import NamedTemporaryFile

    # Load from a file (validates automatically)
    sample_dir = Path(fdl.__file__).parents[1] / "tests" / "sample_data"
    my_fdl = read_from_file(sample_dir / "Scenario-9__OriginalFDL_UsedToMakePlate.fdl")

    # Save to a file (validates automatically)
    with NamedTemporaryFile(suffix=".fdl", delete=False) as f:
        write_to_file(my_fdl, f.name)
    ```

=== "C++"

    ```cpp
    #include "fdl/fdl.hpp"
    #include <fstream>

    // Load from a file
    std::ifstream ifs("my_document.fdl");
    std::string json((std::istreambuf_iterator<char>(ifs)),
                      std::istreambuf_iterator<char>());
    auto doc = fdl::FDL::parse(json);

    // Save to a file
    std::ofstream ofs("output.fdl");
    ofs << doc.to_json();
    ```

For string-based workflows (e.g., network transfer), use `read_from_string()` and
`write_to_string()`. Pass `validate=False` if you want to skip validation, or call
`validate()` manually:

=== "Python"

    ```python
    import fdl
    from fdl import read_from_file, read_from_string, write_to_string
    from pathlib import Path

    sample_dir = Path(fdl.__file__).parents[1] / "tests" / "sample_data"
    my_fdl = read_from_file(sample_dir / "Scenario-9__OriginalFDL_UsedToMakePlate.fdl")

    # Serialize to a JSON string (skip validation since we just loaded a valid file)
    json_str = write_to_string(my_fdl, validate=False)
    assert len(json_str) > 0

    # Parse from a JSON string and validate manually
    my_fdl2 = read_from_string(json_str, validate=False)
    my_fdl2.validate()  # raises FDLValidationError on failure
    assert my_fdl2.uuid == my_fdl.uuid
    ```

=== "C++"

    ```cpp
    #include "fdl/fdl.hpp"

    auto doc = fdl::FDL::parse(json_string);

    // Validate explicitly
    auto errors = doc.validate();  // returns vector<string>, empty on success

    // Serialize to string
    std::string json = doc.to_json();
    ```

---

## Creating an FDL from Scratch

=== "Python"

    ```python
    from fdl import FDL, DimensionsInt, DimensionsFloat, PointFloat, write_to_string

    # Create a new FDL document
    my_fdl = FDL()

    # Add a framing intent
    fi = my_fdl.add_framing_intent(
        id="FI178",
        label="1.78-1 Framing",
        aspect_ratio=DimensionsInt(width=16, height=9),
        protection=0.088,
    )

    # Add a context with a canvas
    ctx = my_fdl.add_context(label="PanavisionDXL2")
    canvas = ctx.add_canvas(
        id="CVS001",
        label="Open Gate RAW",
        source_canvas_id="CVS001",
        dimensions=DimensionsInt(width=5184, height=4320),
        anamorphic_squeeze=1.30,
    )

    # Set optional canvas properties
    canvas.set_effective(
        dims=DimensionsInt(width=5184, height=4320),
        anchor=PointFloat(x=0, y=0),
    )
    canvas.photosite_dimensions = DimensionsInt(width=5184, height=4320)
    canvas.physical_dimensions = DimensionsFloat(width=25.92, height=21.60)

    # Add a framing decision referencing the framing intent
    fd = canvas.add_framing_decision(
        id="CVS001-FI178",
        label="1.78-1 Framing",
        framing_intent_id=fi.id,
        dimensions=DimensionsFloat(width=5184.0, height=2916.0),
        anchor_point=PointFloat(x=0.0, y=702.0),
    )

    # Save to file (validates automatically)
    from tempfile import NamedTemporaryFile
    with NamedTemporaryFile(suffix=".fdl", delete=False) as f:
        from fdl import write_to_file
        write_to_file(my_fdl, f.name)
    ```

=== "C++"

    ```cpp
    #include "fdl/fdl.hpp"
    #include <fstream>

    // Create a new FDL document
    auto doc = fdl::FDL::create("00000000-0000-0000-0000-000000000001");

    // Add a framing intent
    auto fi = doc.add_framing_intent(
        "FI178", "1.78-1 Framing",
        fdl_dimensions_i64_t{16, 9}, 0.088);

    // Add a context with a canvas
    auto ctx = doc.add_context("PanavisionDXL2");
    auto canvas = ctx.add_canvas(
        "CVS001", "Open Gate RAW", "CVS001",
        fdl_dimensions_i64_t{5184, 4320}, 1.30);

    // Set optional canvas properties
    canvas.set_effective(
        fdl_dimensions_i64_t{5184, 4320},
        fdl_point_f64_t{0.0, 0.0});
    canvas.set_photosite_dimensions(fdl_dimensions_i64_t{5184, 4320});
    canvas.set_physical_dimensions(fdl_dimensions_f64_t{25.92, 21.60});

    // Add a framing decision
    auto fd = canvas.add_framing_decision(
        "CVS001-FI178", "1.78-1 Framing", "FI178",
        fdl_dimensions_f64_t{5184.0, 2916.0},
        fdl_point_f64_t{0.0, 702.0});

    // Save to file (validates automatically)
    auto errors = doc.validate();
    std::ofstream ofs("output.fdl");
    ofs << doc.to_json();
    ```

---

## Navigating the Object Model

=== "Python"

    ```python
    import fdl
    from fdl import read_from_file
    from pathlib import Path

    sample_dir = Path(fdl.__file__).parents[1] / "tests" / "sample_data"
    my_fdl = read_from_file(sample_dir / "Scenario-9__OriginalFDL_UsedToMakePlate.fdl")

    # Iterate contexts
    for ctx in my_fdl.contexts:
        print(f"Context: {ctx.label}")

        # Iterate canvases within a context
        for canvas in ctx.canvases:
            print(f"  Canvas: {canvas.label} ({canvas.dimensions.width}x{canvas.dimensions.height})")

            # Iterate framing decisions within a canvas
            for fd in canvas.framing_decisions:
                print(f"    FD: {fd.label}")
                print(f"      Dimensions: {fd.dimensions.width}x{fd.dimensions.height}")
                print(f"      Anchor: ({fd.anchor_point.x}, {fd.anchor_point.y})")
                if fd.protection_dimensions:
                    print(f"      Protection: {fd.protection_dimensions.width}x{fd.protection_dimensions.height}")

    # Iterate framing intents
    for fi in my_fdl.framing_intents:
        print(f"Framing Intent: {fi.label} (protection={fi.protection})")

    # Look up by ID
    canvas = my_fdl.contexts[0].canvases[0]
    fd = canvas.framing_decisions.get_by_id("20220310-FDLSMP03")
    if fd:
        print(f"Found FD: {fd.label}")
    ```

=== "C++"

    ```cpp
    #include "fdl/fdl.hpp"

    auto doc = fdl::FDL::parse(json_string);

    // Iterate contexts
    for (uint32_t i = 0; i < doc.contexts_count(); ++i) {
        auto ctx = doc.context_at(i);

        // Iterate canvases
        for (uint32_t j = 0; j < ctx.canvases_count(); ++j) {
            auto canvas = ctx.canvas_at(j);
            auto dims = canvas.dimensions();

            // Iterate framing decisions
            for (uint32_t k = 0; k < canvas.framing_decisions_count(); ++k) {
                auto fd = canvas.framing_decision_at(k);
                auto fd_dims = fd.dimensions();
                auto anchor = fd.anchor_point();
            }
        }
    }

    // Look up by ID
    auto ctx = doc.context_at(0);
    auto canvas = ctx.canvas_at(0);
    auto fd = canvas.framing_decision_find_by_id("20220310-FDLSMP03");
    ```

---

## Applying a Canvas Template

=== "Python"

    ```python
    import fdl
    from fdl import read_from_file, ATTR_SCALE_FACTOR, ATTR_CONTENT_TRANSLATION, ATTR_SCALED_BOUNDING_BOX
    from pathlib import Path

    # Load an FDL that contains canvas templates
    sample_dir = Path(fdl.__file__).parents[1] / "tests" / "sample_data"
    my_fdl = read_from_file(sample_dir / "Scenario-9__OriginalFDL_UsedToMakePlate.fdl")

    # Select the source canvas and framing decision
    context = my_fdl.contexts[0]
    source_canvas = context.canvases[0]
    source_framing = source_canvas.framing_decisions[0]

    # Select a canvas template
    template = my_fdl.canvas_templates[0]
    print(f"Applying template: {template.label}")

    # Apply the template
    result = template.apply(
        source_canvas=source_canvas,
        source_framing=source_framing,
        new_canvas_id="new_canvas",
        new_fd_name="",
        source_context_label=context.label,
    )

    # Access the output
    output_fdl = result.fdl
    output_canvas = result.canvas
    output_framing = result.framing_decision

    print(f"Output canvas: {output_canvas.label}")
    print(f"  Dimensions: {output_canvas.dimensions.width}x{output_canvas.dimensions.height}")

    # Read computed values from canvas custom attributes
    scale_factor = output_canvas.get_custom_attr(ATTR_SCALE_FACTOR)
    content_translation = output_canvas.get_custom_attr(ATTR_CONTENT_TRANSLATION)
    scaled_bbox = output_canvas.get_custom_attr(ATTR_SCALED_BOUNDING_BOX)

    print(f"  Scale factor: {scale_factor}")
    if content_translation:
        print(f"  Content translation: ({content_translation.x}, {content_translation.y})")
    if scaled_bbox:
        print(f"  Scaled bounding box: {scaled_bbox.width}x{scaled_bbox.height}")
    ```

=== "C++"

    ```cpp
    #include "fdl/fdl.hpp"

    auto doc = fdl::FDL::parse(json_string);

    // Select source canvas and framing
    auto ctx = doc.context_at(0);
    auto source_canvas = ctx.canvas_at(0);
    auto source_framing = source_canvas.framing_decision_at(0);

    // Select a canvas template
    auto tmpl = doc.canvas_template_at(0);

    // Apply the template
    auto result = tmpl.apply(
        source_canvas, source_framing,
        "new_canvas", "",
        ctx.label());

    // Access the output
    auto& output_fdl = result.fdl;
    auto output_canvas = result.canvas();
    auto output_framing = result.framing_decision();

    // Read computed values from canvas custom attributes
    auto sf = output_canvas.get_custom_attr_float(fdl::ATTR_SCALE_FACTOR);
    auto ct = output_canvas.get_custom_attr_point_f64(fdl::ATTR_CONTENT_TRANSLATION);
    auto bb = output_canvas.get_custom_attr_dims_f64(fdl::ATTR_SCALED_BOUNDING_BOX);
    ```

---

## Rounding

FDL supports configurable rounding strategies for dimension values.
The rounding strategy has two components:

- **even**: `"even"` (round to nearest even number) or `"whole"` (round to nearest whole number)
- **mode**: `"up"`, `"down"`, or `"round"` (standard rounding)

=== "Python"

    ```python
    from fdl import (
        DimensionsFloat,
        RoundStrategy,
        set_rounding,
        get_rounding,
        DEFAULT_ROUNDING_STRATEGY,
    )

    # Check the default strategy
    default = get_rounding()
    assert default.even == "even"
    assert default.mode == "up"

    # Set a global rounding strategy
    set_rounding(RoundStrategy(even="whole", mode="round"))
    assert get_rounding().even == "whole"

    # Reset to default
    set_rounding(DEFAULT_ROUNDING_STRATEGY)

    # Per-dimension rounding
    dims = DimensionsFloat(width=19.456, height=79.456)

    # Round to nearest even number, rounding up
    rounded_even_up = dims.round(even="even", mode="up")
    assert rounded_even_up.width == 20
    assert rounded_even_up.height == 80

    # Round to nearest whole number, rounding down
    rounded_whole_down = dims.round(even="whole", mode="down")
    assert rounded_whole_down.width == 19
    assert rounded_whole_down.height == 79

    # Scale then round
    dims2 = DimensionsFloat(width=1920.0, height=1080.0)
    scaled = dims2.scale(0.5, 1.0)
    rounded = scaled.round(even="even", mode="up")
    assert rounded.width == 960
    assert rounded.height == 540
    ```

=== "C++"

    ```cpp
    #include "fdl/fdl.hpp"

    // Per-dimension rounding
    fdl::DimensionsFloat dims(19.456, 79.456);

    // Round to nearest even number, rounding up
    auto rounded = dims.round(FDL_ROUNDING_EVEN_EVEN, FDL_ROUNDING_MODE_UP);
    // rounded.width() == 20, rounded.height() == 80

    // Scale then round
    fdl::DimensionsFloat dims2(1920.0, 1080.0);
    auto scaled = dims2.scale(0.5, 1.0);
    auto result = scaled.round(FDL_ROUNDING_EVEN_EVEN, FDL_ROUNDING_MODE_UP);
    // result.width() == 960, result.height() == 540
    ```

---

## Custom Attributes

Custom attributes can be set on FDL documents, contexts, canvases, framing decisions,
and canvas templates. Supported types include scalars (string, int, float, bool) and
composite types (PointFloat, DimensionsFloat, DimensionsInt).

=== "Python"

    ```python
    from fdl import FDL, DimensionsInt, DimensionsFloat, PointFloat

    my_fdl = FDL()

    # Set scalar attributes
    my_fdl.set_custom_attr("project_name", "My Film")
    my_fdl.set_custom_attr("shot_count", 42)
    my_fdl.set_custom_attr("aspect_ratio_value", 1.78)
    my_fdl.set_custom_attr("is_final", True)

    # Set composite attributes
    my_fdl.set_custom_attr("offset", PointFloat(x=128.0, y=256.0))
    my_fdl.set_custom_attr("target_res", DimensionsFloat(width=3840.0, height=2160.0))
    my_fdl.set_custom_attr("sensor_size", DimensionsInt(width=5184, height=4320))

    # Get attributes by name
    assert my_fdl.get_custom_attr("project_name") == "My Film"
    assert my_fdl.get_custom_attr("shot_count") == 42
    assert my_fdl.get_custom_attr("is_final") is True

    offset = my_fdl.get_custom_attr("offset")
    assert isinstance(offset, PointFloat)
    assert offset.x == 128.0

    target = my_fdl.get_custom_attr("target_res")
    assert isinstance(target, DimensionsFloat)
    assert target.width == 3840.0

    # List all custom attributes
    all_attrs = my_fdl.custom_attrs
    assert "project_name" in all_attrs
    assert "offset" in all_attrs

    # Remove an attribute
    my_fdl.remove_custom_attr("is_final")
    assert my_fdl.get_custom_attr("is_final") is None
    ```

=== "C++"

    ```cpp
    #include "fdl/fdl.hpp"

    auto doc = fdl::FDL::create("00000000-0000-0000-0000-000000000001");

    // Set scalar attributes
    doc.set_custom_attr("project_name", std::string("My Film"));
    doc.set_custom_attr("shot_count", int64_t(42));
    doc.set_custom_attr("aspect_ratio_value", 1.78);
    doc.set_custom_attr("is_final", true);

    // Set composite attributes
    doc.set_custom_attr("offset", fdl::PointFloat(128.0, 256.0));
    doc.set_custom_attr("target_res", fdl::DimensionsFloat(3840.0, 2160.0));
    doc.set_custom_attr("sensor_size", fdl::DimensionsInt(5184, 4320));

    // Get attributes by name
    auto name = doc.get_custom_attr_string("project_name");   // optional<string>
    auto count = doc.get_custom_attr_int("shot_count");        // optional<int64_t>
    auto offset = doc.get_custom_attr_point_f64("offset");     // optional<PointFloat>
    auto target = doc.get_custom_attr_dims_f64("target_res");  // optional<DimensionsFloat>

    // Remove an attribute
    doc.remove_custom_attr("is_final");
    ```

---

## Canvas Custom Attributes on Template Results

When you apply a canvas template, the computed transformation values are stored as
custom attributes on the output canvas. Use the named constants to access them:

| Constant | Type | Description |
|----------|------|-------------|
| `ATTR_SCALE_FACTOR` | float | The scale factor applied by the template |
| `ATTR_CONTENT_TRANSLATION` | PointFloat | The (x, y) translation of content within the canvas |
| `ATTR_SCALED_BOUNDING_BOX` | DimensionsFloat | The bounding box dimensions after scaling |

=== "Python"

    ```python
    from fdl import ATTR_SCALE_FACTOR, ATTR_CONTENT_TRANSLATION, ATTR_SCALED_BOUNDING_BOX
    print(ATTR_SCALE_FACTOR)          # "scale_factor"
    print(ATTR_CONTENT_TRANSLATION)   # "content_translation"
    print(ATTR_SCALED_BOUNDING_BOX)   # "scaled_bounding_box"
    ```

=== "C++"

    ```cpp
    #include "fdl/fdl.hpp"

    // fdl::ATTR_SCALE_FACTOR          == "scale_factor"
    // fdl::ATTR_CONTENT_TRANSLATION   == "content_translation"
    // fdl::ATTR_SCALED_BOUNDING_BOX   == "scaled_bounding_box"

    auto sf = output_canvas.get_custom_attr_float(fdl::ATTR_SCALE_FACTOR);
    auto ct = output_canvas.get_custom_attr_point_f64(fdl::ATTR_CONTENT_TRANSLATION);
    auto bb = output_canvas.get_custom_attr_dims_f64(fdl::ATTR_SCALED_BOUNDING_BOX);
    ```

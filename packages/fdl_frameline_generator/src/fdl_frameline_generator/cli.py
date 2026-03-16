# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Command-line interface for the FDL Frameline Generator.

Provides a CLI tool to generate frameline overlay images from FDL files.
"""

import argparse
import sys
from pathlib import Path

from fdl_frameline_generator.colors import hex_to_rgba
from fdl_frameline_generator.config import LayerVisibility, RenderConfig
from fdl_frameline_generator.renderer import FramelineRenderer


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Parameters
    ----------
    args : list of str, optional
        Arguments to parse. If None, uses sys.argv.

    Returns
    -------
    argparse.Namespace
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        prog="fdl-frameline",
        description="Generate pixel-accurate frameline overlay images from FDL files.",
        epilog="Example: fdl-frameline input.fdl output.exr --show-protection --show-effective",
    )

    # Required arguments
    parser.add_argument(
        "input",
        type=Path,
        help="Path to the input FDL file",
    )
    parser.add_argument(
        "output",
        type=Path,
        help="Path for the output image (format determined by extension: .exr, .png, .tif, .jpg, .dpx, .svg)",
    )

    # Selection arguments
    selection_group = parser.add_argument_group("FDL Selection")
    selection_group.add_argument(
        "--context",
        type=str,
        default=None,
        help="Context label to use (default: first context)",
    )
    selection_group.add_argument(
        "--canvas",
        type=str,
        default=None,
        help="Canvas ID to use (default: first canvas)",
    )
    selection_group.add_argument(
        "--framing",
        type=str,
        default=None,
        help="Framing decision ID to use (default: first framing decision)",
    )

    # Layer visibility arguments
    visibility_group = parser.add_argument_group("Layer Visibility")
    visibility_group.add_argument(
        "--show-canvas",
        action="store_true",
        default=True,
        help="Show canvas outline (default: on)",
    )
    visibility_group.add_argument(
        "--hide-canvas",
        action="store_true",
        help="Hide canvas outline",
    )
    visibility_group.add_argument(
        "--show-effective",
        action="store_true",
        default=True,
        help="Show effective dimensions (default: on)",
    )
    visibility_group.add_argument(
        "--hide-effective",
        action="store_true",
        help="Hide effective dimensions",
    )
    visibility_group.add_argument(
        "--show-protection",
        action="store_true",
        default=True,
        help="Show protection area (default: on)",
    )
    visibility_group.add_argument(
        "--hide-protection",
        action="store_true",
        help="Hide protection area",
    )
    visibility_group.add_argument(
        "--show-framing",
        action="store_true",
        default=True,
        help="Show framing decision (default: on)",
    )
    visibility_group.add_argument(
        "--hide-framing",
        action="store_true",
        help="Hide framing decision",
    )
    visibility_group.add_argument(
        "--show-squeeze-circle",
        action="store_true",
        default=True,
        help="Show anamorphic squeeze reference circle (default: on)",
    )
    visibility_group.add_argument(
        "--hide-squeeze-circle",
        action="store_true",
        help="Hide squeeze reference circle",
    )
    visibility_group.add_argument(
        "--show-labels",
        action="store_true",
        default=True,
        help="Show dimension and anchor labels (default: on)",
    )
    visibility_group.add_argument(
        "--hide-labels",
        action="store_true",
        help="Hide all labels",
    )
    visibility_group.add_argument(
        "--show-crosshair",
        action="store_true",
        default=True,
        help="Show crosshair at framing center (default: on)",
    )
    visibility_group.add_argument(
        "--hide-crosshair",
        action="store_true",
        help="Hide crosshair",
    )
    visibility_group.add_argument(
        "--show-grid",
        action="store_true",
        help="Show grid overlay (default: off)",
    )
    visibility_group.add_argument(
        "--show-logo",
        action="store_true",
        default=True,
        help="Show ASC FDL logo (default: on)",
    )
    visibility_group.add_argument(
        "--hide-logo",
        action="store_true",
        help="Hide logo",
    )

    # Logo arguments
    logo_group = parser.add_argument_group("Logo")
    logo_group.add_argument(
        "--logo-path",
        type=Path,
        default=None,
        help="Path to custom logo image (default: bundled ASC FDL logo)",
    )
    logo_group.add_argument(
        "--logo-scale",
        type=float,
        default=1.0 / 3.0,
        help="Scale factor for logo (default: 0.333, i.e., 1/3)",
    )

    # Metadata overlay arguments
    metadata_group = parser.add_argument_group("Metadata Overlay")
    metadata_group.add_argument(
        "--show-metadata",
        action="store_true",
        default=True,
        help="Show metadata overlay (default: on)",
    )
    metadata_group.add_argument(
        "--hide-metadata",
        action="store_true",
        help="Hide metadata overlay",
    )
    metadata_group.add_argument(
        "--camera",
        type=str,
        default=None,
        help="Camera Make & Model (e.g., 'ARRI Alexa Mini LF'). Defaults to 'Unknown'",
    )
    metadata_group.add_argument(
        "--show-name",
        type=str,
        default=None,
        dest="show_name",
        help="Show name (e.g., 'Stranger Things')",
    )
    metadata_group.add_argument(
        "--dop",
        type=str,
        default=None,
        help="Director of Photography name",
    )
    metadata_group.add_argument(
        "--sensor-mode",
        type=str,
        default=None,
        help="Sensor mode (e.g., '4K', 'Open Gate')",
    )

    # Style arguments
    style_group = parser.add_argument_group("Styling")
    style_group.add_argument(
        "--line-width",
        type=int,
        default=None,
        help="Line width in pixels for all outlines (overrides individual widths)",
    )
    style_group.add_argument(
        "--font-size",
        type=int,
        default=None,
        help="Font size for labels in pixels (overrides individual sizes)",
    )
    style_group.add_argument(
        "--font-path",
        type=Path,
        default=None,
        help="Path to a TrueType font file for labels",
    )
    style_group.add_argument(
        "--grid-spacing",
        type=int,
        default=100,
        help="Grid line spacing in pixels (default: 100)",
    )

    # Color arguments
    color_group = parser.add_argument_group("Colors (hex format, e.g., #FF0000)")
    color_group.add_argument(
        "--color-canvas",
        type=str,
        default=None,
        help="Color for canvas outline (default: #808080)",
    )
    color_group.add_argument(
        "--color-effective",
        type=str,
        default=None,
        help="Color for effective dimensions (default: #0066CC)",
    )
    color_group.add_argument(
        "--color-protection",
        type=str,
        default=None,
        help="Color for protection area (default: #FF9900)",
    )
    color_group.add_argument(
        "--color-framing",
        type=str,
        default=None,
        help="Color for framing decision (default: #00CC66)",
    )

    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )

    return parser.parse_args(args)


def build_config(args: argparse.Namespace) -> RenderConfig:
    """
    Build a RenderConfig from parsed arguments.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments

    Returns
    -------
    RenderConfig
        Configuration object
    """
    # Build visibility settings
    visibility = LayerVisibility(
        canvas=args.show_canvas and not args.hide_canvas,
        effective=args.show_effective and not args.hide_effective,
        protection=args.show_protection and not args.hide_protection,
        framing=args.show_framing and not args.hide_framing,
        squeeze_circle=args.show_squeeze_circle and not args.hide_squeeze_circle,
        dimension_labels=args.show_labels and not args.hide_labels,
        anchor_labels=args.show_labels and not args.hide_labels,
        crosshair=args.show_crosshair and not args.hide_crosshair,
        grid=args.show_grid,
    )

    # Start with default config
    config = RenderConfig(visibility=visibility)

    # Apply line width override
    if args.line_width is not None:
        config.line_width_canvas = args.line_width
        config.line_width_effective = args.line_width
        config.line_width_protection = args.line_width
        config.line_width_framing = args.line_width

    # Apply font settings
    if args.font_size is not None:
        config.font_size_dimension = args.font_size
        config.font_size_anchor = args.font_size
    if args.font_path is not None:
        config.font_path = str(args.font_path)

    # Apply grid spacing
    config.grid_spacing = args.grid_spacing

    # Apply color overrides
    if args.color_canvas is not None:
        config.color_canvas = hex_to_rgba(args.color_canvas)
    if args.color_effective is not None:
        config.color_effective = hex_to_rgba(args.color_effective)
    if args.color_protection is not None:
        config.color_protection = hex_to_rgba(args.color_protection)
    if args.color_framing is not None:
        config.color_framing = hex_to_rgba(args.color_framing)

    # Apply logo settings
    config.show_logo = args.show_logo and not args.hide_logo
    if args.logo_path is not None:
        config.logo_path = args.logo_path
    config.logo_scale = args.logo_scale

    # Apply metadata settings
    config.show_metadata = args.show_metadata and not args.hide_metadata
    config.metadata_camera = args.camera
    config.metadata_show = args.show_name
    config.metadata_dop = args.dop
    config.metadata_sensor_mode = args.sensor_mode

    return config


def main(args: list[str] | None = None) -> int:
    """
    Main entry point for the CLI.

    Parameters
    ----------
    args : list of str, optional
        Arguments to parse. If None, uses sys.argv.

    Returns
    -------
    int
        Exit code (0 for success, non-zero for errors)
    """
    parsed_args = parse_args(args)

    # Validate input file exists
    if not parsed_args.input.exists():
        print(f"Error: Input file not found: {parsed_args.input}", file=sys.stderr)
        return 1

    # Build configuration
    config = build_config(parsed_args)

    # Create renderer
    renderer = FramelineRenderer(config)

    if parsed_args.verbose:
        print(f"Loading FDL: {parsed_args.input}")
        if parsed_args.context:
            print(f"  Context: {parsed_args.context}")
        if parsed_args.canvas:
            print(f"  Canvas: {parsed_args.canvas}")
        if parsed_args.framing:
            print(f"  Framing: {parsed_args.framing}")

    try:
        success = renderer.render_from_fdl(
            fdl_path=parsed_args.input,
            output_path=parsed_args.output,
            context_label=parsed_args.context,
            canvas_id=parsed_args.canvas,
            framing_id=parsed_args.framing,
        )

        if success:
            if parsed_args.verbose:
                print(f"Output written to: {parsed_args.output}")
            return 0
        else:
            print("Error: Rendering failed", file=sys.stderr)
            return 1

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"Error writing output: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if parsed_args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

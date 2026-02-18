# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Shared scenario configuration for FDL tests (unit tests and UI tests).

This module defines data-driven configurations for all test scenarios (1-31),
enabling parameterized tests that cover all variants across all scenarios.

Note: Scenarios 21 and 22 are error validation tests (expecting ValueError)
and are handled separately via is_error_test flag.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SourceVariant:
    """
    Configuration for a single source file variant.

    Attributes
    ----------
    letter : str
        Single letter identifier (e.g., "B", "D", "G").
    fdl_basename : str
        Base filename without extension (e.g., "B_4448x3096_1x_FramingChart").
    has_tif : bool
        Whether this variant has a TIF source image.
    input_dims : Optional[Tuple[float, float]]
        Source image dimensions (width, height) for unit tests.
    context_label : Optional[str]
        Override context label for this variant (if different from scenario default).
    canvas_label : Optional[str]
        Override canvas label for this variant (if different from scenario default).
    """

    letter: str
    fdl_basename: str
    has_tif: bool = True
    input_dims: tuple[float, float] | None = None
    context_label: str | None = None
    canvas_label: str | None = None
    test_name_suffix: str | None = None  # Custom suffix for test name (e.g., "uhd_b" instead of just "b")


@dataclass
class ScenarioConfig:
    """
    Configuration for a test scenario.

    Attributes
    ----------
    number : int
        Scenario number (1-31).
    name : str
        Human-readable scenario name.
    dir_name : str
        Directory name for this scenario.
    template_filename : str
        Template FDL filename.
    variants : List[SourceVariant]
        List of source variants for this scenario.
    result_pattern : str
        Pattern for result filenames with {variant} placeholder.
    context_label : str
        Default label for context selection (default: "VFX Pull").
    canvas_label : str
        Default label for canvas selection (default: "Custom").
    custom_template_dir : Optional[str]
        Custom directory for template file (relative to sample_files_dir).
        If None, uses dir_name.
    custom_template_path : Optional[str]
        Full path for template file (relative to FDL resources root).
        Takes precedence over custom_template_dir if set.
    custom_source_dir : Optional[str]
        Custom directory for source files (relative to FDL resources root).
        If None, uses dir_name/Source_Files.
    custom_results_dir : Optional[str]
        Custom directory for result files (relative to FDL resources root).
        If None, uses dir_name/Results.
    framing_intent_id : str
        FD to select (default: "1").
    context_creator : str
        Creator string for context (default: "ASC FDL Tools").
    template_label : str
        Label of the template to use (default: "VFX Pull - Custom").
    is_error_test : bool
        True for scenarios 21, 22 that expect ValueError.
    """

    number: int
    name: str
    dir_name: str
    template_filename: str
    variants: list[SourceVariant]
    result_pattern: str
    context_label: str = "VFX Pull"
    canvas_label: str = "Custom"
    custom_template_dir: str | None = None
    custom_template_path: str | None = None
    custom_source_dir: str | None = None
    custom_results_dir: str | None = None
    framing_intent_id: str = "1"
    context_creator: str = "ASC FDL Tools"
    template_label: str = "VFX Pull - Custom"
    is_error_test: bool = False


# =============================================================================
# Standard source variant definitions with unit test data
# =============================================================================

# Variant A: ARRI ALEXA Mini LF, 4.5K LF Open Gate, 1.3x anamorphic
VARIANT_A = SourceVariant(
    letter="A",
    fdl_basename="A_4448x3096_1-3x_FramingChart",
    input_dims=(4448.0, 3096.0),
    context_label="ARRI ALEXA Mini LF",
    canvas_label="4.5K LF Open Gate",
)

# Variant B: ARRI ALEXA Mini LF, 4.5K LF Open Gate, 1x spherical
VARIANT_B = SourceVariant(
    letter="B",
    fdl_basename="B_4448x3096_1x_FramingChart",
    input_dims=(4448.0, 3096.0),
    context_label="ARRI ALEXA Mini LF",
    canvas_label="4.5K LF Open Gate",
)

# Variant C: ARRI ALEXA Mini LF, 4.5K LF Open Gate, 2x anamorphic
VARIANT_C = SourceVariant(
    letter="C",
    fdl_basename="C_4448x3096_2x_FramingChart",
    input_dims=(4448.0, 3096.0),
    context_label="ARRI ALEXA Mini LF",
    canvas_label="4.5K LF Open Gate",
)

# Variant D: Sony VENICE 2 8K, 8.6K 3:2, 10% safety
VARIANT_D = SourceVariant(
    letter="D",
    fdl_basename="D_8640x5760_1x_10PercentSafety-FramingChart",
    input_dims=(8640.0, 5760.0),
    context_label="Sony VENICE 2 8K",
    canvas_label="8.6K 3:2",
)

# Variant E: Sony VENICE 2 8K, 8.6K 3:2, 15% safety
VARIANT_E = SourceVariant(
    letter="E",
    fdl_basename="E_8640x5760_1x_15PercentSafety-FramingChart",
    input_dims=(8640.0, 5760.0),
    context_label="Sony VENICE 2 8K",
    canvas_label="8.6K 3:2",
)

# Variant F: Sony VENICE 2 8K, 8.6K 3:2, 20% safety
VARIANT_F = SourceVariant(
    letter="F",
    fdl_basename="F_8640x5760_1x_20PercentSafety-FramingChart",
    input_dims=(8640.0, 5760.0),
    context_label="Sony VENICE 2 8K",
    canvas_label="8.6K 3:2",
)

# Variant G: RED V-RAPTOR 8K S35, 7K 4:3 2x, top-aligned
VARIANT_G = SourceVariant(
    letter="G",
    fdl_basename="G_5040x3780_1x_TopAligned-FramingChart",
    input_dims=(5040.0, 3780.0),
    context_label="RED V-RAPTOR 8K S35",
    canvas_label="7K 4:3 2x",
)

# Variant J: RED DSMC2 MONSTRO 8K VV, 4.5K 5:4, 2x anamorphic
VARIANT_J = SourceVariant(
    letter="J",
    fdl_basename="J_4320x3456_2x_FramingChart",
    input_dims=(4320.0, 3456.0),
    context_label="RED DSMC2 MONSTRO 8K VV",
    canvas_label="4.5K 5:4",
)

# =============================================================================
# Custom variants for New_Source_Files scenarios
# =============================================================================

# Scenario 19: RED EPIC Dragon 6K, 2x anamorphic
VARIANT_RED_EPIC = SourceVariant(
    letter="RED_EPIC",
    fdl_basename="Test_06_RED_EPIC_Dragon_6K",
    input_dims=(4096.0, 2048.0),
    context_label="RED EPIC DRAGON 6K S35",
    canvas_label="4K 2:1",
)

# Scenario 20: Sony FX3, 1.5x anamorphic
VARIANT_SONY_FX3 = SourceVariant(
    letter="SONY_FX3",
    fdl_basename="Test_01_Sony_FX3",
    input_dims=(3840.0, 2160.0),
    context_label="Sony FX3",
    canvas_label="4K",
)

# Scenario 23: Blackmagic URSA Cine 17K 65, 12K 16:9
VARIANT_BLACKMAGIC_17K_65 = SourceVariant(
    letter="BLACKMAGIC_17K_65",
    fdl_basename="Test_09_Blackmagic_URSA_Cine_17K_65",
    input_dims=(12288.0, 6912.0),
    context_label="Blackmagic Design URSA Cine 17K 65",
    canvas_label="12K 16:9",
)

# Scenario 24: ARRI Alexa 65, 6500, 1.65x anamorphic
VARIANT_ARRI_ALEXA_65_19 = SourceVariant(
    letter="ARRI_ALEXA_65_19",
    fdl_basename="Test_19_ARRI_Alexa_65",
    input_dims=(6580.0, 5020.0),
    context_label="ARRI Alexa 65",
    canvas_label="6500",
)

# Scenario 25: ARRI Alexa 65, 6500, 1x spherical
VARIANT_ARRI_ALEXA_65_20 = SourceVariant(
    letter="ARRI_ALEXA_65_20",
    fdl_basename="Test_20_ARRI_Alexa_65",
    input_dims=(6580.0, 5020.0),
    context_label="ARRI Alexa 65",
    canvas_label="6500",
)

# Scenario 26: Blackmagic URSA Cine 12K LF, 2x anamorphic with custom framing
VARIANT_BLACKMAGIC_12K_LF_CUSTOM = SourceVariant(
    letter="BLACKMAGIC_12K_LF_CUSTOM",
    fdl_basename="Test_58_Blackmagic_URSA_Cine_12K_LF_CustomFraming",
    input_dims=(12288.0, 6912.0),
    context_label="Blackmagic URSA Cine 12K LF",
    canvas_label="12K 16:9",
)

# Scenario 27: RED EPIC Dragon 6K, 1.5x anamorphic with custom framing
VARIANT_RED_EPIC_CUSTOM = SourceVariant(
    letter="RED_EPIC_CUSTOM",
    fdl_basename="Test_60_RED_EPIC_Dragon_6K_CustomFraming",
    input_dims=(4096.0, 2048.0),
    context_label="RED EPIC Dragon 6K",
    canvas_label="4K 2:1",
)

# Scenario 28: ARRI Alexa 65, 1.65x anamorphic with custom framing
VARIANT_ARRI_ALEXA_65_CUSTOM = SourceVariant(
    letter="ARRI_ALEXA_65_CUSTOM",
    fdl_basename="Test_62_ARRI_Alexa_65_CustomFraming",
    input_dims=(6580.0, 5020.0),
    context_label="ARRI Alexa 65",
    canvas_label="6500",
)

# Scenario 29: Sony FX3 Test_01, 1.5x anamorphic
VARIANT_SONY_FX3_01 = SourceVariant(
    letter="SONY_FX3_01",
    fdl_basename="Test_01_Sony_FX3",
    input_dims=(3840.0, 2160.0),
    context_label="Sony FX3",
    canvas_label="4K",
)

# Scenario 30: Sony FX3 Test_02, 1.5x anamorphic
VARIANT_SONY_FX3_02 = SourceVariant(
    letter="SONY_FX3_02",
    fdl_basename="Test_02_Sony_FX3",
    input_dims=(3840.0, 2160.0),
    context_label="Sony FX3",
    canvas_label="4K",
)

# Scenario 31: EdgeCases alignment combo
VARIANT_TOPLEFT_TOPCENTER = SourceVariant(
    letter="TOPLEFT_TOPCENTER",
    fdl_basename="combo_src_topleft_tpl_topcenter_source",
    input_dims=(4096.0, 3072.0),
    context_label="Off-Center Source top-left",
    canvas_label="4K Canvas - Source top-left",
)


# =============================================================================
# Scenario configuration registry with full test data
# =============================================================================


def _make_scen1_variants() -> list[SourceVariant]:
    """Create variants for scenario 1 with expected values."""
    return [
        SourceVariant(
            letter="B",
            fdl_basename="B_4448x3096_1x_FramingChart",
            input_dims=(4448.0, 3096.0),
            context_label="ARRI ALEXA Mini LF",
            canvas_label="4.5K LF Open Gate",
            test_name_suffix="uhd_b",  # Special naming for this variant
        ),
        SourceVariant(
            letter="D",
            fdl_basename="D_8640x5760_1x_10PercentSafety-FramingChart",
            input_dims=(8640.0, 5760.0),
            context_label="Sony VENICE 2 8K",
            canvas_label="8.6K 3:2",
        ),
    ]


def _make_scen2_variants() -> list[SourceVariant]:
    """Create variants for scenario 2 with expected values."""
    return [
        SourceVariant(
            letter="B",
            fdl_basename="B_4448x3096_1x_FramingChart",
            input_dims=(4448.0, 3096.0),
            context_label="ARRI ALEXA Mini LF",
            canvas_label="4.5K LF Open Gate",
        ),
        SourceVariant(
            letter="D",
            fdl_basename="D_8640x5760_1x_10PercentSafety-FramingChart",
            input_dims=(8640.0, 5760.0),
            context_label="Sony VENICE 2 8K",
            canvas_label="8.6K 3:2",
        ),
    ]


def _make_scen3_variants() -> list[SourceVariant]:
    """Create variants for scenario 3 with expected values."""
    return [
        SourceVariant(
            letter="D",
            fdl_basename="D_8640x5760_1x_10PercentSafety-FramingChart",
            input_dims=(8640.0, 5760.0),
            context_label="Sony VENICE 2 8K",
            canvas_label="8.6K 3:2",
        ),
        SourceVariant(
            letter="E",
            fdl_basename="E_8640x5760_1x_15PercentSafety-FramingChart",
            input_dims=(8640.0, 5760.0),
            context_label="Sony VENICE 2 8K",
            canvas_label="8.6K 3:2",
        ),
        SourceVariant(
            letter="F",
            fdl_basename="F_8640x5760_1x_20PercentSafety-FramingChart",
            input_dims=(8640.0, 5760.0),
            context_label="Sony VENICE 2 8K",
            canvas_label="8.6K 3:2",
        ),
    ]


def _make_scen4_variants() -> list[SourceVariant]:
    """Create variants for scenario 4 with expected values."""
    return [
        SourceVariant(
            letter="D",
            fdl_basename="D_8640x5760_1x_10PercentSafety-FramingChart",
            input_dims=(8640.0, 5760.0),
            context_label="Sony VENICE 2 8K",
            canvas_label="8.6K 3:2",
        ),
        SourceVariant(
            letter="E",
            fdl_basename="E_8640x5760_1x_15PercentSafety-FramingChart",
            input_dims=(8640.0, 5760.0),
            context_label="Sony VENICE 2 8K",
            canvas_label="8.6K 3:2",
        ),
        SourceVariant(
            letter="F",
            fdl_basename="F_8640x5760_1x_20PercentSafety-FramingChart",
            input_dims=(8640.0, 5760.0),
            context_label="Sony VENICE 2 8K",
            canvas_label="8.6K 3:2",
        ),
    ]


def _make_scen5_variants() -> list[SourceVariant]:
    """Create variants for scenario 5 with expected values."""
    return [
        SourceVariant(
            letter="A",
            fdl_basename="A_4448x3096_1-3x_FramingChart",
            input_dims=(4448.0, 3096.0),
            context_label="ARRI ALEXA Mini LF",
            canvas_label="4.5K LF Open Gate",
        ),
        SourceVariant(
            letter="B",
            fdl_basename="B_4448x3096_1x_FramingChart",
            input_dims=(4448.0, 3096.0),
            context_label="ARRI ALEXA Mini LF",
            canvas_label="4.5K LF Open Gate",
        ),
        SourceVariant(
            letter="C",
            fdl_basename="C_4448x3096_2x_FramingChart",
            input_dims=(4448.0, 3096.0),
            context_label="ARRI ALEXA Mini LF",
            canvas_label="4.5K LF Open Gate",
        ),
    ]


def _make_scen6_variants() -> list[SourceVariant]:
    """Create variants for scenario 6 with expected values."""
    return [
        SourceVariant(
            letter="A",
            fdl_basename="A_4448x3096_1-3x_FramingChart",
            input_dims=(4448.0, 3096.0),
            context_label="ARRI ALEXA Mini LF",
            canvas_label="4.5K LF Open Gate",
        ),
        SourceVariant(
            letter="B",
            fdl_basename="B_4448x3096_1x_FramingChart",
            input_dims=(4448.0, 3096.0),
            context_label="ARRI ALEXA Mini LF",
            canvas_label="4.5K LF Open Gate",
        ),
        SourceVariant(
            letter="C",
            fdl_basename="C_4448x3096_2x_FramingChart",
            input_dims=(4448.0, 3096.0),
            context_label="ARRI ALEXA Mini LF",
            canvas_label="4.5K LF Open Gate",
        ),
    ]


def _make_scen9_variants() -> list[SourceVariant]:
    """Create variants for scenario 9 with expected values."""
    return [
        SourceVariant(
            letter="B",
            fdl_basename="B_4448x3096_1x_FramingChart",
            input_dims=(4448.0, 3096.0),
            context_label="ARRI ALEXA Mini LF",
            canvas_label="4.5K LF Open Gate",
        ),
        SourceVariant(
            letter="G",
            fdl_basename="G_5040x3780_1x_TopAligned-FramingChart",
            input_dims=(5040.0, 3780.0),
            context_label="RED V-RAPTOR 8K S35",
            canvas_label="7K 4:3 2x",
        ),
    ]


def _make_scen10_variants() -> list[SourceVariant]:
    """Create variants for scenario 10 with expected values."""
    return [
        SourceVariant(
            letter="B",
            fdl_basename="B_4448x3096_1x_FramingChart",
            input_dims=(4448.0, 3096.0),
            context_label="ARRI ALEXA Mini LF",
            canvas_label="4.5K LF Open Gate",
        ),
        SourceVariant(
            letter="J",
            fdl_basename="J_4320x3456_2x_FramingChart",
            input_dims=(4320.0, 3456.0),
            context_label="RED DSMC2 MONSTRO 8K VV",
            canvas_label="4.5K 5:4",
        ),
    ]


def _make_scen11_variants() -> list[SourceVariant]:
    """Create variants for scenario 11 with expected values."""
    return [
        SourceVariant(
            letter="B",
            fdl_basename="B_4448x3096_1x_FramingChart",
            input_dims=(4448.0, 3096.0),
            context_label="ARRI ALEXA Mini LF",
            canvas_label="4.5K LF Open Gate",
        ),
        SourceVariant(
            letter="J",
            fdl_basename="J_4320x3456_2x_FramingChart",
            input_dims=(4320.0, 3456.0),
            context_label="RED DSMC2 MONSTRO 8K VV",
            canvas_label="4.5K 5:4",
        ),
    ]


def _make_scen14_variants() -> list[SourceVariant]:
    """Create variants for scenario 14 with expected values."""
    return [
        SourceVariant(
            letter="D",
            fdl_basename="D_8640x5760_1x_10PercentSafety-FramingChart",
            input_dims=(8640.0, 5760.0),
            context_label="Sony VENICE 2 8K",
            canvas_label="8.6K 3:2",
        ),
        SourceVariant(
            letter="E",
            fdl_basename="E_8640x5760_1x_15PercentSafety-FramingChart",
            input_dims=(8640.0, 5760.0),
            context_label="Sony VENICE 2 8K",
            canvas_label="8.6K 3:2",
        ),
        SourceVariant(
            letter="F",
            fdl_basename="F_8640x5760_1x_20PercentSafety-FramingChart",
            input_dims=(8640.0, 5760.0),
            context_label="Sony VENICE 2 8K",
            canvas_label="8.6K 3:2",
        ),
    ]


def _make_scen15_variants() -> list[SourceVariant]:
    """Create variants for scenario 15 with expected values."""
    return [
        SourceVariant(
            letter="A",
            fdl_basename="A_4448x3096_1-3x_FramingChart",
            input_dims=(4448.0, 3096.0),
            context_label="ARRI ALEXA Mini LF",
            canvas_label="4.5K LF Open Gate",
        ),
        SourceVariant(
            letter="B",
            fdl_basename="B_4448x3096_1x_FramingChart",
            input_dims=(4448.0, 3096.0),
            context_label="ARRI ALEXA Mini LF",
            canvas_label="4.5K LF Open Gate",
        ),
        SourceVariant(
            letter="C",
            fdl_basename="C_4448x3096_2x_FramingChart",
            input_dims=(4448.0, 3096.0),
            context_label="ARRI ALEXA Mini LF",
            canvas_label="4.5K LF Open Gate",
        ),
    ]


def _make_scen16_variants() -> list[SourceVariant]:
    """Create variants for scenario 16 with expected values."""
    return [
        SourceVariant(
            letter="A",
            fdl_basename="A_4448x3096_1-3x_FramingChart",
            input_dims=(4448.0, 3096.0),
            context_label="ARRI ALEXA Mini LF",
            canvas_label="4.5K LF Open Gate",
        ),
        SourceVariant(
            letter="B",
            fdl_basename="B_4448x3096_1x_FramingChart",
            input_dims=(4448.0, 3096.0),
            context_label="ARRI ALEXA Mini LF",
            canvas_label="4.5K LF Open Gate",
        ),
        SourceVariant(
            letter="C",
            fdl_basename="C_4448x3096_2x_FramingChart",
            input_dims=(4448.0, 3096.0),
            context_label="ARRI ALEXA Mini LF",
            canvas_label="4.5K LF Open Gate",
        ),
    ]


def _make_scen17_variants() -> list[SourceVariant]:
    """Create variants for scenario 17 with expected values."""
    return [
        SourceVariant(
            letter="A",
            fdl_basename="A_4448x3096_1-3x_FramingChart",
            input_dims=(4448.0, 3096.0),
            context_label="ARRI ALEXA Mini LF",
            canvas_label="4.5K LF Open Gate",
        ),
        SourceVariant(
            letter="B",
            fdl_basename="B_4448x3096_1x_FramingChart",
            input_dims=(4448.0, 3096.0),
            context_label="ARRI ALEXA Mini LF",
            canvas_label="4.5K LF Open Gate",
        ),
        SourceVariant(
            letter="C",
            fdl_basename="C_4448x3096_2x_FramingChart",
            input_dims=(4448.0, 3096.0),
            context_label="ARRI ALEXA Mini LF",
            canvas_label="4.5K LF Open Gate",
        ),
    ]


def _make_scen18_variants() -> list[SourceVariant]:
    """Create variants for scenario 18 with expected values."""
    return [
        SourceVariant(
            letter="A",
            fdl_basename="A_4448x3096_1-3x_FramingChart",
            input_dims=(4448.0, 3096.0),
            context_label="ARRI ALEXA Mini LF",
            canvas_label="4.5K LF Open Gate",
        ),
        SourceVariant(
            letter="B",
            fdl_basename="B_4448x3096_1x_FramingChart",
            input_dims=(4448.0, 3096.0),
            context_label="ARRI ALEXA Mini LF",
            canvas_label="4.5K LF Open Gate",
        ),
        SourceVariant(
            letter="C",
            fdl_basename="C_4448x3096_2x_FramingChart",
            input_dims=(4448.0, 3096.0),
            context_label="ARRI ALEXA Mini LF",
            canvas_label="4.5K LF Open Gate",
        ),
    ]


SCENARIO_CONFIGS: dict[int, ScenarioConfig] = {
    1: ScenarioConfig(
        number=1,
        name="FitDecision-into-UHD",
        dir_name="Scen_1_FitDecision-into-UHD",
        template_filename="Scen_1_FitDecision-into-UHD-CANVAS-TEMPLATE.fdl",
        variants=_make_scen1_variants(),
        result_pattern="Scen1-RESULT-{variant}.fdl",
        custom_source_dir="Original_Source_Files",
    ),
    2: ScenarioConfig(
        number=2,
        name="FitProtection-into-UHD",
        dir_name="Scen_2_FitProtection-into-UHD",
        template_filename="Scen_2_FitProtection-into-UHD-CANVAS-TEMPLATE.fdl",
        variants=_make_scen2_variants(),
        result_pattern="Scen2-RESULT-{variant}.fdl",
        custom_source_dir="Original_Source_Files",
    ),
    3: ScenarioConfig(
        number=3,
        name="Preserving-Protection",
        dir_name="Scen_3_Preserving-Protection",
        template_filename="Scen_3_Preserving-Protection-CANVAS-TEMPLATE.fdl",
        variants=_make_scen3_variants(),
        result_pattern="Scen3-RESULT-{variant}.fdl",
        custom_source_dir="Original_Source_Files",
    ),
    4: ScenarioConfig(
        number=4,
        name="Preserving-Canvas",
        dir_name="Scen_4_Preserving-Canvas",
        template_filename="Scen_4_Preserving-Canvas-CANVAS-TEMPLATE.fdl",
        variants=_make_scen4_variants(),
        result_pattern="Scen4-RESULT-{variant}.fdl",
        custom_source_dir="Original_Source_Files",
    ),
    5: ScenarioConfig(
        number=5,
        name="Normalizing_LensSqueezeTo1",
        dir_name="Scen_5_Normalizing_LensSqueezeTo1",
        template_filename="Scen_5_Normalizing_LensSqueezeTo1-CANVAS-TEMPLATE.fdl",
        variants=_make_scen5_variants(),
        result_pattern="Scen5-RESULT-{variant}.fdl",
        custom_source_dir="Original_Source_Files",
    ),
    6: ScenarioConfig(
        number=6,
        name="Normalizing_LensSqueezeTo2",
        dir_name="Scen_6_Normalizing_LensSqueezeTo2",
        template_filename="Scen_6_Normalizing_LensSqueezeTo2-CANVAS-TEMPLATE.fdl",
        variants=_make_scen6_variants(),
        result_pattern="Scen6-RESULT-{variant}.fdl",
        custom_source_dir="Original_Source_Files",
    ),
    7: ScenarioConfig(
        number=7,
        name="TopAlignedSource-PreserveProtection-Centered",
        dir_name="Scen_7_TopAlignedSource-PreserveProtection-Centered",
        template_filename="Scen_7_TopAlignedSource-PreserveProtection-Centered-CANVAS-TEMPLATE.fdl",
        variants=[
            SourceVariant(
                letter="G",
                fdl_basename="G_5040x3780_1x_TopAligned-FramingChart",
                input_dims=(5040.0, 3780.0),
                context_label="RED V-RAPTOR 8K S35",
                canvas_label="7K 4:3 2x",
            ),
        ],
        result_pattern="Scen7-RESULT-{variant}.fdl",
        custom_source_dir="Original_Source_Files",
    ),
    8: ScenarioConfig(
        number=8,
        name="TopAlignedSource-PreserveCanvas-Centered",
        dir_name="Scen_8_TopAlignedSource-PreserveCanvas-Centered",
        template_filename="Scen_8_TopAlignedSource-PreserveCanvas-Centered-CANVAS-TEMPLATE.fdl",
        variants=[
            SourceVariant(
                letter="G",
                fdl_basename="G_5040x3780_1x_TopAligned-FramingChart",
                input_dims=(5040.0, 3780.0),
                context_label="RED V-RAPTOR 8K S35",
                canvas_label="7K 4:3 2x",
            ),
        ],
        result_pattern="Scen8-RESULT-{variant}.fdl",
        custom_source_dir="Original_Source_Files",
    ),
    9: ScenarioConfig(
        number=9,
        name="PadToMax",
        dir_name="Scen_9_PadToMax",
        template_filename="Scen_9_PadToMax-CANVAS-TEMPLATE.fdl",
        variants=_make_scen9_variants(),
        result_pattern="Scen9-RESULT-{variant}.fdl",
        custom_source_dir="Original_Source_Files",
    ),
    10: ScenarioConfig(
        number=10,
        name="FitWidth_MaintainAspectRatio",
        dir_name="Scen_10_FitWidth_MaintainAspectRatio",
        template_filename="Scen_10_FitWidth_MaintainAspectRatio-CANVAS-TEMPLATE.fdl",
        variants=_make_scen10_variants(),
        result_pattern="{variant}.fdl",  # Scen 10 uses just the variant name
        custom_source_dir="Original_Source_Files",
    ),
    11: ScenarioConfig(
        number=11,
        name="FitHeight_MaintainAspectRatio",
        dir_name="Scen_11_FitHeight_MaintainAspectRatio",
        template_filename="Scen_11_FitHeight_MaintainAspectRatio-CANVAS-TEMPLATE.fdl",
        variants=_make_scen11_variants(),
        result_pattern="{variant}.fdl",  # Scen 11 uses just the variant name
        custom_source_dir="Original_Source_Files",
    ),
    12: ScenarioConfig(
        number=12,
        name="FitDecision_Fill",
        dir_name="Scen_12_FitDecision_Fill",
        template_filename="Scen_12_FitDecision-Fill.fdl",
        variants=[
            SourceVariant(
                letter="D",
                fdl_basename="D_8640x5760_1x_10PercentSafety-FramingChart",
                input_dims=(8640.0, 5760.0),
                context_label="Sony VENICE 2 8K",
                canvas_label="8.6K 3:2",
            ),
        ],
        result_pattern="Scen12-RESULT{variant}.fdl",  # Note: no dash before variant
        custom_source_dir="Original_Source_Files",
    ),
    13: ScenarioConfig(
        number=13,
        name="FitDecision_With_Protection_Fill",
        dir_name="Scen_13_FitDecision_With_Protection_Fill",
        template_filename="Scen_13_FitDecision-With-ProtectionFill.fdl",
        variants=[
            SourceVariant(
                letter="D",
                fdl_basename="D_8640x5760_1x_10PercentSafety-FramingChart",
                input_dims=(8640.0, 5760.0),
                context_label="Sony VENICE 2 8K",
                canvas_label="8.6K 3:2",
            ),
        ],
        result_pattern="Scen13-RESULT{variant}.fdl",  # Note: no dash before variant
        custom_source_dir="Original_Source_Files",
    ),
    14: ScenarioConfig(
        number=14,
        name="Preserving-Protection-WithMaxDim-Cropping",
        dir_name="Scen_14_Preserving-Protection-WithMaxDim-Cropping",
        template_filename="Scen_14_Preserving-Protection-WithMaxDim-Cropping-TEMPLATE.fdl",
        variants=_make_scen14_variants(),
        result_pattern="Scen14-RESULT-{variant}.fdl",
        custom_source_dir="Original_Source_Files",
    ),
    15: ScenarioConfig(
        number=15,
        name="Retention_Of_Relative_Anchors",
        dir_name="Scen_15_Retention_Of_Relative_Anchors",
        template_filename="Scen_15_Retention_of_relative_anchors.fdl",
        variants=_make_scen15_variants(),
        result_pattern="Scen15-RESULT-{variant}.fdl",
        custom_source_dir="Original_Source_Files",
    ),
    16: ScenarioConfig(
        number=16,
        name="Retention_Of_Relative_Anchors_pad_to_max_top_left",
        dir_name="Scen_16_Retention_Of_Relative_Anchors_pad_to_max_top_left",
        template_filename="Scen_16_Retention_Of_Relative_Anchors_pad_to_max_top_left.fdl",
        variants=_make_scen16_variants(),
        result_pattern="Scen16-RESULT-{variant}.fdl",
        custom_source_dir="Original_Source_Files",
    ),
    17: ScenarioConfig(
        number=17,
        name="Retention_Of_Relative_Anchors_pad_to_max_bottom_left",
        dir_name="Scen_17_Retention_Of_Relative_Anchors_pad_to_max_bottom_left",
        template_filename="Scen_17_Retention_Of_Relative_Anchors_pad_to_max_bottom_left.fdl",
        variants=_make_scen17_variants(),
        result_pattern="Scen17-RESULT-{variant}.fdl",
        custom_source_dir="Original_Source_Files",
    ),
    18: ScenarioConfig(
        number=18,
        name="Normalizing_LensSqueezeTo2_PadToMax_NonUniform_Crop",
        dir_name="Scen_18_Normalizing_LensSqueezeTo2_PadToMax_NonUniform_Crop",
        template_filename="Scen_18_Normalizing_LensSqueezeTo2-CANVAS-TEMPLATE.fdl",
        variants=_make_scen18_variants(),
        result_pattern="Scen18-RESULT-{variant}.fdl",
        custom_source_dir="Original_Source_Files",
    ),
    19: ScenarioConfig(
        number=19,
        name="PadToMax_RED_EPIC_Dragon_6K",
        dir_name="Scen_19_PadToMax_RED_EPIC_Dragon_6K",
        template_filename="Scen_9_PadToMax-CANVAS-TEMPLATE.fdl",
        variants=[
            SourceVariant(
                letter="RED_EPIC",
                fdl_basename="Test_06_RED_EPIC_Dragon_6K",
                input_dims=(4096.0, 2048.0),
                context_label="RED EPIC DRAGON 6K S35",
                canvas_label="4K 2:1",
                test_name_suffix="red_epic_dragon_6k",
            ),
        ],
        result_pattern="Scen19-RESULT-{variant}.fdl",
        custom_template_dir="Scen_9_PadToMax",
        custom_source_dir="New_Source_Files",
    ),
    20: ScenarioConfig(
        number=20,
        name="Preserving_Protection_WithMaxDim_Cropping_Sony_FX3",
        dir_name="Scen_20_Preserving_Protection_WithMaxDim_Cropping_Sony_FX3",
        template_filename="Scen_14_Preserving-Protection-WithMaxDim-Cropping-TEMPLATE.fdl",
        variants=[
            SourceVariant(
                letter="SONY_FX3",
                fdl_basename="Test_01_Sony_FX3",
                input_dims=(3840.0, 2160.0),
                context_label="Sony FX3",
                canvas_label="4K",
                test_name_suffix="sony_fx3",
            ),
        ],
        result_pattern="Scen20-RESULT-{variant}.fdl",
        custom_template_dir="Scen_14_Preserving-Protection-WithMaxDim-Cropping",
        custom_source_dir="New_Source_Files",
    ),
    # Scenarios 21 and 22 are error validation tests
    21: ScenarioConfig(
        number=21,
        name="Error_FitSource_ProtectionDimensions_Missing",
        dir_name="Scen_2_FitProtection-into-UHD",
        template_filename="Scen_2_FitProtection-into-UHD-CANVAS-TEMPLATE.fdl",
        variants=[],  # No variants - error test
        result_pattern="",
        is_error_test=True,
    ),
    22: ScenarioConfig(
        number=22,
        name="Error_PreserveFromSourceCanvas_ProtectionDimensions_Missing",
        dir_name="Scen_3_Preserving-Protection",
        template_filename="Scen_3_Preserving-Protection-CANVAS-TEMPLATE.fdl",
        variants=[],  # No variants - error test
        result_pattern="",
        is_error_test=True,
    ),
    23: ScenarioConfig(
        number=23,
        name="FitDecision_With_Protection_Fill_Blackmagic_17K_65",
        dir_name="Scen_23_FitDecision_With_Protection_Fill_Blackmagic_17K_65",
        template_filename="Scen_13_FitDecision-With-ProtectionFill.fdl",
        variants=[
            SourceVariant(
                letter="BLACKMAGIC_17K_65",
                fdl_basename="Test_09_Blackmagic_URSA_Cine_17K_65",
                input_dims=(12288.0, 6912.0),
                context_label="Blackmagic Design URSA Cine 17K 65",
                canvas_label="12K 16:9",
                test_name_suffix="blackmagic_ursa_cine_17k_65",
            ),
        ],
        result_pattern="Scen23-RESULT-{variant}.fdl",
        custom_template_dir="Scen_13_FitDecision_With_Protection_Fill",
        custom_source_dir="New_Source_Files",
    ),
    24: ScenarioConfig(
        number=24,
        name="Preserving_Protection_WithMaxDim_Cropping_ARRI_Alexa_65",
        dir_name="Scen_24_Preserving_Protection_WithMaxDim_Cropping_ARRI_Alexa_65",
        template_filename="Scen_14_Preserving-Protection-WithMaxDim-Cropping-TEMPLATE.fdl",
        variants=[
            SourceVariant(
                letter="ARRI_ALEXA_65_19",
                fdl_basename="Test_19_ARRI_Alexa_65",
                input_dims=(6580.0, 5020.0),
                context_label="ARRI Alexa 65",
                canvas_label="6500",
                test_name_suffix="arri_alexa_65",
            ),
        ],
        result_pattern="Scen24-RESULT-{variant}.fdl",
        custom_template_dir="Scen_14_Preserving-Protection-WithMaxDim-Cropping",
        custom_source_dir="New_Source_Files",
    ),
    25: ScenarioConfig(
        number=25,
        name="FitDecision_With_Protection_Fill_ARRI_Alexa_65",
        dir_name="Scen_25_FitDecision_With_Protection_Fill_ARRI_Alexa_65",
        template_filename="Scen_13_FitDecision-With-ProtectionFill.fdl",
        variants=[
            SourceVariant(
                letter="ARRI_ALEXA_65_20",
                fdl_basename="Test_20_ARRI_Alexa_65",
                input_dims=(6580.0, 5020.0),
                context_label="ARRI Alexa 65",
                canvas_label="6500",
                test_name_suffix="arri_alexa_65",
            ),
        ],
        result_pattern="Scen25-RESULT-{variant}.fdl",
        custom_template_dir="Scen_13_FitDecision_With_Protection_Fill",
        custom_source_dir="New_Source_Files",
    ),
    26: ScenarioConfig(
        number=26,
        name="FitHeight_MaintainAspectRatio_Blackmagic_12K_LF_CustomFraming",
        dir_name="Scen_26_FitHeight_MaintainAspectRatio_Blackmagic_12K_LF_CustomFraming",
        template_filename="Scen_11_FitHeight_MaintainAspectRatio-CANVAS-TEMPLATE.fdl",
        variants=[
            SourceVariant(
                letter="BLACKMAGIC_12K_LF_CUSTOM",
                fdl_basename="Test_58_Blackmagic_URSA_Cine_12K_LF_CustomFraming",
                input_dims=(12288.0, 6912.0),
                context_label="Blackmagic URSA Cine 12K LF",
                canvas_label="12K 16:9",
                test_name_suffix="blackmagic_ursa_cine_12k_lf",
            ),
        ],
        result_pattern="Scen26-RESULT-{variant}.fdl",
        custom_template_dir="Scen_11_FitHeight_MaintainAspectRatio",
        custom_source_dir="New_Source_Files",
    ),
    27: ScenarioConfig(
        number=27,
        name="FitHeight_MaintainAspectRatio_RED_EPIC_CustomFraming",
        dir_name="Scen_27_FitHeight_MaintainAspectRatio_RED_EPIC_CustomFraming",
        template_filename="Scen_11_FitHeight_MaintainAspectRatio-CANVAS-TEMPLATE.fdl",
        variants=[
            SourceVariant(
                letter="RED_EPIC_CUSTOM",
                fdl_basename="Test_60_RED_EPIC_Dragon_6K_CustomFraming",
                input_dims=(4096.0, 2048.0),
                context_label="RED EPIC Dragon 6K",
                canvas_label="4K 2:1",
                test_name_suffix="red_epic_dragon_6k",
            ),
        ],
        result_pattern="Scen27-RESULT-{variant}.fdl",
        custom_template_dir="Scen_11_FitHeight_MaintainAspectRatio",
        custom_source_dir="New_Source_Files",
    ),
    28: ScenarioConfig(
        number=28,
        name="FitHeight_MaintainAspectRatio_ARRI_Alexa_65_CustomFraming",
        dir_name="Scen_28_FitHeight_MaintainAspectRatio_ARRI_Alexa_65_CustomFraming",
        template_filename="Scen_11_FitHeight_MaintainAspectRatio-CANVAS-TEMPLATE.fdl",
        variants=[
            SourceVariant(
                letter="ARRI_ALEXA_65_CUSTOM",
                fdl_basename="Test_62_ARRI_Alexa_65_CustomFraming",
                input_dims=(6580.0, 5020.0),
                context_label="ARRI Alexa 65",
                canvas_label="6500",
                test_name_suffix="arri_alexa_65",
            ),
        ],
        result_pattern="Scen28-RESULT-{variant}.fdl",
        custom_template_dir="Scen_11_FitHeight_MaintainAspectRatio",
        custom_source_dir="New_Source_Files",
    ),
    29: ScenarioConfig(
        number=29,
        name="FitDecision_With_Protection_Fill_Sony_FX3_01",
        dir_name="Scen_29_FitDecision_With_Protection_Fill_Sony_FX3_01",
        template_filename="Scen_13_FitDecision-With-ProtectionFill.fdl",
        variants=[
            SourceVariant(
                letter="SONY_FX3_01",
                fdl_basename="Test_01_Sony_FX3",
                input_dims=(3840.0, 2160.0),
                context_label="Sony FX3",
                canvas_label="4K",
                test_name_suffix="sony_fx3",
            ),
        ],
        result_pattern="Scen29-RESULT-{variant}.fdl",
        context_label="Sony FX3",
        canvas_label="4K",
        custom_template_dir="Scen_13_FitDecision_With_Protection_Fill",
        custom_source_dir="New_Source_Files",
    ),
    30: ScenarioConfig(
        number=30,
        name="FitDecision_With_Protection_Fill_Sony_FX3_02",
        dir_name="Scen_30_FitDecision_With_Protection_Fill_Sony_FX3_02",
        template_filename="Scen_13_FitDecision-With-ProtectionFill.fdl",
        variants=[
            SourceVariant(
                letter="SONY_FX3_02",
                fdl_basename="Test_02_Sony_FX3",
                input_dims=(3840.0, 2160.0),
                context_label="Sony FX3",
                canvas_label="4K",
                test_name_suffix="sony_fx3",
            ),
        ],
        result_pattern="Scen30-RESULT-{variant}.fdl",
        context_label="Sony FX3",
        canvas_label="4K",
        custom_template_dir="Scen_13_FitDecision_With_Protection_Fill",
        custom_source_dir="New_Source_Files",
    ),
    31: ScenarioConfig(
        number=31,
        name="Alignment_Combo_TopLeft_To_TopCenter",
        dir_name="EdgeCases",
        template_filename="combo_src_topleft_tpl_topcenter_template.fdl",
        variants=[
            SourceVariant(
                letter="TOPLEFT_TOPCENTER",
                fdl_basename="combo_src_topleft_tpl_topcenter_source",
                input_dims=(4096.0, 3072.0),
                context_label="Off-Center Source top-left",
                canvas_label="4K Canvas - Source top-left",
                test_name_suffix="topleft_to_topcenter",
            ),
        ],
        result_pattern="Scen31-RESULT-combo_src_topleft_tpl_topcenter.fdl",
        context_label="Off-Center Source top-left",
        canvas_label="4K Canvas - Source top-left",
        template_label="Template: top-center alignment",
        framing_intent_id="combo_intent",
        context_creator="Edge Case Generator",
        custom_template_path="EdgeCases/alignment_combos/templates",
        custom_source_dir="EdgeCases/alignment_combos/source",
        custom_results_dir="EdgeCases/alignment_combos/Results",
    ),
    32: ScenarioConfig(
        number=32,
        name="EffTopLeft_To_BottomRight",
        dir_name="Scen_32_EffTopLeft_To_BottomRight",
        template_filename="eff_topleft_to_bottomright_template.fdl",
        variants=[
            SourceVariant(
                letter="EFF_TOPLEFT_BOTTOMRIGHT",
                fdl_basename="eff_topleft_to_bottomright_source",
                input_dims=(6144.0, 4096.0),
                context_label="Effective Area eff_topleft_to_bottomright",
                canvas_label="6K with offset effective area",
                test_name_suffix="eff_topleft_to_bottomright",
            ),
        ],
        result_pattern="Scen32-RESULT-eff_topleft_to_bottomright.fdl",
        context_label="Effective Area eff_topleft_to_bottomright",
        canvas_label="6K with offset effective area",
        template_label="Template: bottom-right from effective",
        framing_intent_id="eff_combo_intent",
        context_creator="Edge Case Generator",
        custom_template_path="EdgeCases/alignment_combos/templates",
        custom_source_dir="EdgeCases/alignment_combos/source",
    ),
}


def build_test_params() -> list[tuple[int, str]]:
    """
    Build (scen_num, variant_letter) tuples for parameterization.

    Returns
    -------
    List[Tuple[int, str]]
        List of (scenario_number, variant_letter) tuples.
    """
    params = []
    for scen_num, config in SCENARIO_CONFIGS.items():
        for variant in config.variants:
            params.append((scen_num, variant.letter))
    return params


def get_scenario_test_id(param: tuple[int, str]) -> str:
    """
    Generate a pytest test ID from scenario parameters.

    Parameters
    ----------
    param : Tuple[int, str]
        (scenario_number, variant_letter) tuple.

    Returns
    -------
    str
        Test ID string like "scen2_B".
    """
    return f"scen{param[0]}_{param[1]}"


def get_scenario_paths(sample_files_dir: Path, config: ScenarioConfig, variant: SourceVariant) -> dict[str, Path]:
    """
    Get all file paths for a scenario/variant combination.

    Parameters
    ----------
    sample_files_dir : Path
        Root path to Scenarios_For_Implementers.
    config : ScenarioConfig
        Scenario configuration.
    variant : SourceVariant
        Source variant configuration.

    Returns
    -------
    Dict[str, Path]
        Dictionary with keys: template, source_fdl, source_tif, expected_fdl, expected_exr.
    """
    # Get the FDL resources root (parent of Scenarios_For_Implementers)
    fdl_resources_root = sample_files_dir.parent

    # Determine template directory
    # custom_template_path takes precedence (relative to fdl_resources_root)
    # custom_template_dir is relative to sample_files_dir
    if config.custom_template_path:
        template_dir = fdl_resources_root / config.custom_template_path
    elif config.custom_template_dir:
        template_dir = sample_files_dir / config.custom_template_dir
    else:
        template_dir = sample_files_dir / config.dir_name

    # Determine source directory
    if config.custom_source_dir:
        source_dir = fdl_resources_root / config.custom_source_dir
    else:
        source_dir = sample_files_dir / config.dir_name / "Source_Files"

    # Determine results directory
    if config.custom_results_dir:
        results_dir = fdl_resources_root / config.custom_results_dir
    else:
        results_dir = sample_files_dir / config.dir_name / "Results"

    # Build result filename using pattern
    result_fdl_name = config.result_pattern.format(variant=variant.fdl_basename)
    result_exr_name = result_fdl_name.replace(".fdl", ".001001.exr")
    # Some scenarios use different exr naming
    if not (results_dir / result_exr_name).exists():
        result_exr_name = result_fdl_name.replace(".fdl", ".exr")

    # Handle .tiff extension for custom source directories
    source_tif_path = source_dir / f"{variant.fdl_basename}.tif"
    if not source_tif_path.exists():
        source_tif_path = source_dir / f"{variant.fdl_basename}.tiff"

    return {
        "template": template_dir / config.template_filename,
        "source_fdl": source_dir / f"{variant.fdl_basename}.fdl",
        "source_tif": source_tif_path,
        "expected_fdl": results_dir / result_fdl_name,
        "expected_exr": results_dir / result_exr_name,
    }


def get_variant_by_letter(config: ScenarioConfig, letter: str) -> SourceVariant | None:
    """
    Get a variant from a scenario config by its letter.

    Parameters
    ----------
    config : ScenarioConfig
        Scenario configuration.
    letter : str
        Variant letter (e.g., "B").

    Returns
    -------
    Optional[SourceVariant]
        The matching variant, or None if not found.
    """
    for variant in config.variants:
        if variant.letter == letter:
            return variant
    return None


# Import and merge exported scenarios
# This allows user-exported scenarios from FDL Viewer to be included in tests
try:
    from fdl.testing.exported_scenarios import EXPORTED_SCENARIO_CONFIGS

    SCENARIO_CONFIGS.update(EXPORTED_SCENARIO_CONFIGS)
except ImportError:
    pass  # No exported scenarios yet

# AUTO-GENERATED — DO NOT EDIT
"""Pydantic v2 data models for the ASC Framing Decision List.

These models provide a pure-data DTO (Data Transfer Object) layer for
interoperability with web services and frameworks like FastAPI, Django REST
Framework, and other Pydantic-native tools.

**Data vs Logic**: The Pydantic models in this subpackage are data-only classes
for serialization, validation, and transport. Business logic (compute framing,
resolve canvas, round dimensions, etc.) lives on the bound facade classes in the
parent ``fdl`` package (``FDL``, ``Canvas``, ``Context``, etc.).

**Validation**: These models provide full semantic validation. Pydantic validates
types and JSON Schema constraints first, then the C core validates semantic rules
(ID reference integrity, dependent required fields, version constraints, etc.).

**Converting between models and facades**::

    from fdl import FDL
    from fdl.models import FramingDecisionList

    # Facade -> Model (for API responses, serialization)
    doc = FDL.parse(json_bytes)
    model = doc.to_model()

    # Model -> Facade (for computation after receiving API input)
    doc = FDL.from_model(model)
"""

from ._generated import (  # noqa: F401
    CanvasModel,
    CanvasTemplateModel,
    ClipIDModel,
    ContextModel,
    DimensionsFloatModel,
    DimensionsIntModel,
    FileSequenceModel,
    FramingDecisionList,
    FramingDecisionModel,
    FramingIntentModel,
    PointFloatModel,
    RoundModel,
    VersionModel,
)

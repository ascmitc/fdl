import type {
  CanvasData,
  FramingDecisionData,
  TemplateParams,
  TransformResultData,
} from "@/api/types";
import type { HudData } from "./canvas-renderer";

export function buildHudData(
  sourceCanvas: CanvasData | null,
  sourceFraming: FramingDecisionData | null,
  outputCanvas: CanvasData | null,
  outputFraming: FramingDecisionData | null,
  template: TemplateParams,
  transformResult: TransformResultData | null,
): HudData {
  return {
    sourceLines: buildCanvasLines(sourceCanvas, sourceFraming),
    outputLines: buildCanvasLines(outputCanvas, outputFraming),
    templateLines: buildTemplateLines(template, transformResult),
  };
}

function buildCanvasLines(
  canvas: CanvasData | null,
  fd: FramingDecisionData | null,
): [string, string][] {
  const lines: [string, string][] = [];
  if (canvas) {
    lines.push([
      "Canvas",
      `${Math.round(canvas.dimensions.width)} x ${Math.round(canvas.dimensions.height)}`,
    ]);
    if (canvas.effectiveDimensions) {
      lines.push([
        "Effective",
        `${Math.round(canvas.effectiveDimensions.width)} x ${Math.round(canvas.effectiveDimensions.height)}`,
      ]);
    }
    if (canvas.effectiveAnchorPoint) {
      lines.push([
        "Eff. Anchor",
        `(${Math.round(canvas.effectiveAnchorPoint.x)}, ${Math.round(canvas.effectiveAnchorPoint.y)})`,
      ]);
    }
  }
  if (fd) {
    lines.push([
      "Framing",
      `${Math.round(fd.dimensions.width)} x ${Math.round(fd.dimensions.height)}`,
    ]);
    lines.push([
      "Anchor",
      `(${Math.round(fd.anchorPoint.x)}, ${Math.round(fd.anchorPoint.y)})`,
    ]);
    if (fd.protectionDimensions) {
      lines.push([
        "Protection",
        `${Math.round(fd.protectionDimensions.width)} x ${Math.round(fd.protectionDimensions.height)}`,
      ]);
    }
  }
  return lines;
}

function buildTemplateLines(
  template: TemplateParams,
  result: TransformResultData | null,
): [string, string][] {
  const lines: [string, string][] = [];
  lines.push(["Target", `${template.targetWidth} x ${template.targetHeight}`]);
  if (template.targetAnamorphicSqueeze !== 1.0) {
    lines.push(["Squeeze", template.targetAnamorphicSqueeze.toFixed(2)]);
  }
  lines.push([
    "Fit Source",
    template.fitSource.replace("framing_decision.", "").replace("canvas.", ""),
  ]);
  lines.push(["Fit Method", template.fitMethod]);
  lines.push(["Align H", template.alignmentMethodHorizontal]);
  if (template.alignmentMethodVertical !== "center") {
    lines.push(["Align V", template.alignmentMethodVertical]);
  }
  if (template.preserveFromSourceCanvas) {
    lines.push([
      "Preserve",
      template.preserveFromSourceCanvas
        .replace("framing_decision.", "")
        .replace("canvas.", ""),
    ]);
  }
  if (result?.scaleFactor != null) {
    lines.push(["Scale", result.scaleFactor.toFixed(4)]);
  }
  if (result?.contentTranslation) {
    lines.push([
      "Translation",
      `(${result.contentTranslation.x.toFixed(1)}, ${result.contentTranslation.y.toFixed(1)})`,
    ]);
  }
  return lines;
}

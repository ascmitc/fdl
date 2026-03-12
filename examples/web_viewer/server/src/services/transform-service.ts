import {
  CanvasTemplate,
  DimensionsInt,
  FitMethod,
  GeometryPath,
  HAlign,
  VAlign,
  RoundStrategy,
  RoundingEven,
  RoundingMode,
} from "@asc-mitc/fdl";
import type { Canvas, FramingDecision, FDL } from "@asc-mitc/fdl";
import type {
  TemplateParams,
  TransformResultData,
  TransformResponse,
} from "../types/api.js";
import {
  storeFdl,
  computeGeometry,
  findCanvasAndFraming,
  getSession,
} from "./fdl-service.js";

const GEOMETRY_PATH_MAP: Record<string, GeometryPath> = {
  "canvas.dimensions": GeometryPath.CANVAS_DIMENSIONS,
  "canvas.effective_dimensions": GeometryPath.CANVAS_EFFECTIVE_DIMENSIONS,
  "framing_decision.dimensions": GeometryPath.FRAMING_DIMENSIONS,
  "framing_decision.protection_dimensions":
    GeometryPath.FRAMING_PROTECTION_DIMENSIONS,
};

const FIT_METHOD_MAP: Record<string, FitMethod> = {
  width: FitMethod.WIDTH,
  height: FitMethod.HEIGHT,
  fit_all: FitMethod.FIT_ALL,
  fill: FitMethod.FILL,
};

const H_ALIGN_MAP: Record<string, HAlign> = {
  left: HAlign.LEFT,
  center: HAlign.CENTER,
  right: HAlign.RIGHT,
};

const V_ALIGN_MAP: Record<string, VAlign> = {
  top: VAlign.TOP,
  center: VAlign.CENTER,
  bottom: VAlign.BOTTOM,
};

const ROUND_EVEN_MAP: Record<string, RoundingEven> = {
  whole: RoundingEven.WHOLE,
  even: RoundingEven.EVEN,
};

const ROUND_MODE_MAP: Record<string, RoundingMode> = {
  up: RoundingMode.UP,
  down: RoundingMode.DOWN,
  round: RoundingMode.ROUND,
};

function createTemplate(params: TemplateParams): CanvasTemplate {
  return new CanvasTemplate({
    id: "web_template",
    label: "Web Viewer Template",
    targetDimensions: new DimensionsInt(params.targetWidth, params.targetHeight),
    targetAnamorphicSqueeze: params.targetAnamorphicSqueeze,
    fitSource: GEOMETRY_PATH_MAP[params.fitSource] ?? GeometryPath.FRAMING_DIMENSIONS,
    fitMethod: FIT_METHOD_MAP[params.fitMethod] ?? FitMethod.FIT_ALL,
    alignmentMethodHorizontal:
      H_ALIGN_MAP[params.alignmentMethodHorizontal] ?? HAlign.CENTER,
    alignmentMethodVertical:
      V_ALIGN_MAP[params.alignmentMethodVertical] ?? VAlign.CENTER,
    round: new RoundStrategy(
      ROUND_EVEN_MAP[params.roundEven] ?? RoundingEven.EVEN,
      ROUND_MODE_MAP[params.roundMode] ?? RoundingMode.UP,
    ),
    preserveFromSourceCanvas: params.preserveFromSourceCanvas
      ? GEOMETRY_PATH_MAP[params.preserveFromSourceCanvas] ?? null
      : null,
    maximumDimensions: params.maximumDimensions
      ? new DimensionsInt(params.maximumDimensions.width, params.maximumDimensions.height)
      : null,
    padToMaximum: params.padToMaximum,
  });
}

export function applyTransform(
  sourceSessionId: string,
  contextLabel: string,
  canvasId: string,
  framingId: string,
  templateParams: TemplateParams,
): TransformResponse {
  const session = getSession(sourceSessionId);
  if (!session) {
    throw new Error(`Session not found: ${sourceSessionId}`);
  }

  const found = findCanvasAndFraming(
    session.fdl,
    contextLabel,
    canvasId,
    framingId,
  );
  if (!found) {
    throw new Error(
      `Could not find context="${contextLabel}", canvas="${canvasId}", framing="${framingId}"`,
    );
  }

  const sourceGeometry = computeGeometry(found.canvas, found.framing);

  const template = createTemplate(templateParams);
  const result = template.apply(
    found.canvas,
    found.framing,
    `${canvasId}_output`,
    `${framingId}_output`,
    contextLabel,
  );

  // Store the output FDL
  const { sessionId: outputSessionId, hierarchy: outputHierarchy } = storeFdl(
    result.fdl,
  );

  // Navigate to the output canvas/framing for geometry
  const outputFound = findCanvasAndFraming(
    result.fdl,
    result._context_label,
    result._canvas_id,
    result._framing_decision_id,
  );

  const outputGeometry = outputFound
    ? computeGeometry(outputFound.canvas, outputFound.framing)
    : {
        canvasRect: { x: 0, y: 0, width: 0, height: 0 },
        effectiveRect: null,
        framingRect: null,
        protectionRect: null,
        anchorPoint: null,
      };

  // Extract transform result metadata from output canvas custom attrs
  let scaleFactor: number | null = null;
  let contentTranslation = null;
  let scaledBoundingBox = null;

  if (outputFound) {
    const canvas = outputFound.canvas;
    if (canvas.hasCustomAttr("scale_factor")) {
      scaleFactor = canvas.getCustomAttr("scale_factor") as number;
    }
    if (canvas.hasCustomAttr("content_translation_x")) {
      contentTranslation = {
        x: canvas.getCustomAttr("content_translation_x") as number,
        y: canvas.getCustomAttr("content_translation_y") as number,
      };
    }
    if (canvas.hasCustomAttr("scaled_bounding_box_width")) {
      scaledBoundingBox = {
        width: canvas.getCustomAttr("scaled_bounding_box_width") as number,
        height: canvas.getCustomAttr("scaled_bounding_box_height") as number,
      };
    }
  }

  return {
    outputSessionId,
    outputContextLabel: result._context_label,
    outputCanvasId: result._canvas_id,
    outputFramingId: result._framing_decision_id,
    hierarchy: outputHierarchy,
    sourceGeometry,
    outputGeometry,
    transformResult: {
      scaleFactor,
      contentTranslation,
      scaledBoundingBox,
    },
  };
}

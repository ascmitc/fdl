// Client-side API types (mirrors server/src/types/api.ts)

export interface Dimensions {
  width: number;
  height: number;
}

export interface Point {
  x: number;
  y: number;
}

export interface Rect {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface FramingDecisionData {
  id: string;
  label: string;
  framingIntentId: string;
  dimensions: Dimensions;
  anchorPoint: Point;
  protectionDimensions: Dimensions | null;
  protectionAnchorPoint: Point | null;
}

export interface CanvasData {
  id: string;
  label: string;
  dimensions: Dimensions;
  effectiveDimensions: Dimensions | null;
  effectiveAnchorPoint: Point | null;
  anamorphicSqueeze: number;
  framingDecisions: FramingDecisionData[];
}

export interface ContextData {
  label: string;
  contextCreator: string;
  canvases: CanvasData[];
}

export interface FramingIntentData {
  id: string;
  label: string;
  aspectRatio: Dimensions;
  protection: number;
}

export interface CanvasTemplateData {
  id: string;
  label: string;
  targetDimensions: Dimensions;
  targetAnamorphicSqueeze: number;
  fitSource: string;
  fitMethod: string;
  alignmentMethodHorizontal: string;
  alignmentMethodVertical: string;
  preserveFromSourceCanvas: string | null;
  maximumDimensions: Dimensions | null;
  padToMaximum: boolean;
  roundEven: string;
  roundMode: string;
}

export interface FdlHierarchy {
  uuid: string;
  version: { major: number; minor: number };
  fdlCreator: string;
  defaultFramingIntent: string | null;
  framingIntents: FramingIntentData[];
  contexts: ContextData[];
  canvasTemplates: CanvasTemplateData[];
}

export interface GeometryData {
  canvasRect: Rect;
  effectiveRect: Rect | null;
  framingRect: Rect | null;
  protectionRect: Rect | null;
  anchorPoint: Point | null;
}

export interface TemplateParams {
  targetWidth: number;
  targetHeight: number;
  targetAnamorphicSqueeze: number;
  fitSource: string;
  fitMethod: string;
  alignmentMethodHorizontal: string;
  alignmentMethodVertical: string;
  preserveFromSourceCanvas: string | null;
  maximumDimensions: Dimensions | null;
  padToMaximum: boolean;
  roundEven: string;
  roundMode: string;
}

export interface TransformResultData {
  scaleFactor: number | null;
  contentTranslation: Point | null;
  scaledBoundingBox: Dimensions | null;
}

export interface TransformResponse {
  outputSessionId: string;
  outputContextLabel: string;
  outputCanvasId: string;
  outputFramingId: string;
  hierarchy: FdlHierarchy;
  sourceGeometry: GeometryData;
  outputGeometry: GeometryData;
  transformResult: TransformResultData;
}

export interface ParseResponse {
  sessionId: string;
  hierarchy: FdlHierarchy;
}

export interface PresetInfo {
  name: string;
  id: string;
  label: string;
  targetDimensions: Dimensions;
}

export interface SelectOption {
  value: string;
  label: string;
}

export interface TemplateOptions {
  fitSource: SelectOption[];
  fitMethod: SelectOption[];
  alignmentHorizontal: SelectOption[];
  alignmentVertical: SelectOption[];
  preserve: SelectOption[];
  roundEven: SelectOption[];
  roundMode: SelectOption[];
}

import { create } from "zustand";
import type {
  FdlHierarchy,
  GeometryData,
  TemplateParams,
  TransformResultData,
  CanvasData,
  CanvasTemplateData,
  ContextData,
  FramingDecisionData,
} from "@/api/types";

interface AppState {
  // FDL state
  sourceFdl: FdlHierarchy | null;
  sourceSessionId: string | null;
  outputFdl: FdlHierarchy | null;
  outputSessionId: string | null;
  outputContextLabel: string | null;
  outputCanvasId: string | null;
  outputFramingId: string | null;

  // Geometry (computed by server)
  sourceGeometry: GeometryData | null;
  outputGeometry: GeometryData | null;

  // Selection state
  selectedContext: string;
  selectedCanvas: string;
  selectedFraming: string;

  // Template state
  currentTemplate: TemplateParams;
  presetMode: boolean;
  selectedPreset: string;
  templateFdl: FdlHierarchy | null;
  templateFdlSessionId: string | null;
  selectedTemplateId: string;

  // Transform result
  transformResult: TransformResultData | null;
  templateModifiedSinceTransform: boolean;

  // UI state
  activeTab: number;
  sidebarCollapsed: boolean;
  gridVisible: boolean;

  // Layer visibility
  canvasVisible: boolean;
  effectiveVisible: boolean;
  framingVisible: boolean;
  protectionVisible: boolean;
  imageVisible: boolean;
  hudVisible: boolean;

  // Image state
  sourceImageId: string | null;
  sourceImageUrl: string | null;
  sourceImageDimensions: { width: number; height: number } | null;
  outputImageId: string | null;
  outputImageUrl: string | null;
  imageOpacity: number;

  // Status
  statusMessage: string;
  error: string | null;
  loading: boolean;

  // Actions
  setSourceFdl: (fdl: FdlHierarchy, sessionId: string) => void;
  setOutputFdl: (
    fdl: FdlHierarchy,
    sessionId: string,
    geometry: GeometryData,
    result: TransformResultData,
    contextLabel: string,
    canvasId: string,
    framingId: string,
  ) => void;
  clearOutput: () => void;
  setSourceGeometry: (geometry: GeometryData) => void;
  setSelectedContext: (label: string) => void;
  setSelectedCanvas: (id: string) => void;
  setSelectedFraming: (id: string) => void;
  setCurrentTemplate: (template: TemplateParams) => void;
  updateTemplate: (updates: Partial<TemplateParams>) => void;
  setPresetMode: (mode: boolean) => void;
  setSelectedPreset: (name: string) => void;
  setTemplateFdl: (fdl: FdlHierarchy, sessionId: string) => void;
  setSelectedTemplateId: (id: string) => void;
  clearTemplateFdl: () => void;
  setActiveTab: (tab: number) => void;
  toggleSidebar: () => void;
  toggleGrid: () => void;
  setLayerVisibility: (
    layer:
      | "canvas"
      | "effective"
      | "framing"
      | "protection"
      | "image"
      | "hud",
    visible: boolean,
  ) => void;
  setSourceImage: (
    id: string,
    url: string,
    dims: { width: number; height: number },
  ) => void;
  clearSourceImage: () => void;
  setOutputImage: (id: string, url: string) => void;
  clearOutputImage: () => void;
  setImageOpacity: (opacity: number) => void;
  setStatus: (message: string) => void;
  setError: (error: string | null) => void;
  setLoading: (loading: boolean) => void;
}

export function canvasTemplateToParams(tpl: CanvasTemplateData): TemplateParams {
  return {
    targetWidth: tpl.targetDimensions.width,
    targetHeight: tpl.targetDimensions.height,
    targetAnamorphicSqueeze: tpl.targetAnamorphicSqueeze,
    fitSource: tpl.fitSource,
    fitMethod: tpl.fitMethod,
    alignmentMethodHorizontal: tpl.alignmentMethodHorizontal,
    alignmentMethodVertical: tpl.alignmentMethodVertical,
    preserveFromSourceCanvas: tpl.preserveFromSourceCanvas,
    maximumDimensions: tpl.maximumDimensions,
    padToMaximum: tpl.padToMaximum,
    roundEven: tpl.roundEven,
    roundMode: tpl.roundMode,
  };
}

const DEFAULT_TEMPLATE: TemplateParams = {
  targetWidth: 1920,
  targetHeight: 1080,
  targetAnamorphicSqueeze: 1.0,
  fitSource: "framing_decision.dimensions",
  fitMethod: "fit_all",
  alignmentMethodHorizontal: "center",
  alignmentMethodVertical: "center",
  preserveFromSourceCanvas: null,
  maximumDimensions: null,
  padToMaximum: false,
  roundEven: "even",
  roundMode: "up",
};

// Stable empty arrays to avoid re-render loops with Zustand selectors
const EMPTY_CONTEXTS: ContextData[] = [];
const EMPTY_CANVASES: CanvasData[] = [];
const EMPTY_FRAMINGS: FramingDecisionData[] = [];

// Helpers to get derived data
export function getContexts(state: AppState): ContextData[] {
  return state.sourceFdl?.contexts ?? EMPTY_CONTEXTS;
}

export function getCanvases(state: AppState): CanvasData[] {
  const ctx = state.sourceFdl?.contexts.find(
    (c) => c.label === state.selectedContext,
  );
  return ctx?.canvases ?? EMPTY_CANVASES;
}

export function getFramingDecisions(state: AppState): FramingDecisionData[] {
  const ctx = state.sourceFdl?.contexts.find(
    (c) => c.label === state.selectedContext,
  );
  const canvas = ctx?.canvases.find((c) => c.id === state.selectedCanvas);
  return canvas?.framingDecisions ?? EMPTY_FRAMINGS;
}

export function getSelectedCanvas(state: AppState): CanvasData | null {
  const ctx = state.sourceFdl?.contexts.find(
    (c) => c.label === state.selectedContext,
  );
  return ctx?.canvases.find((c) => c.id === state.selectedCanvas) ?? null;
}

export function getOutputContext(state: AppState): ContextData | null {
  if (!state.outputFdl || !state.outputContextLabel) return null;
  return state.outputFdl.contexts.find(
    (c) => c.label === state.outputContextLabel,
  ) ?? null;
}

export function getOutputCanvas(state: AppState): CanvasData | null {
  const ctx = getOutputContext(state);
  if (!ctx || !state.outputCanvasId) return null;
  return ctx.canvases.find((c) => c.id === state.outputCanvasId) ?? null;
}

export function getOutputFraming(state: AppState): FramingDecisionData | null {
  const canvas = getOutputCanvas(state);
  if (!canvas || !state.outputFramingId) return null;
  return canvas.framingDecisions.find(
    (fd) => fd.id === state.outputFramingId,
  ) ?? null;
}

export function canTransform(state: AppState): boolean {
  return !!(
    state.sourceFdl &&
    state.sourceSessionId &&
    state.selectedContext &&
    state.selectedCanvas &&
    state.selectedFraming &&
    state.currentTemplate.targetWidth > 0 &&
    state.currentTemplate.targetHeight > 0
  );
}

export const useAppStore = create<AppState>((set) => ({
  // Initial state
  sourceFdl: null,
  sourceSessionId: null,
  outputFdl: null,
  outputSessionId: null,
  outputContextLabel: null,
  outputCanvasId: null,
  outputFramingId: null,
  sourceGeometry: null,
  outputGeometry: null,
  selectedContext: "",
  selectedCanvas: "",
  selectedFraming: "",
  currentTemplate: { ...DEFAULT_TEMPLATE },
  presetMode: false,
  selectedPreset: "",
  templateFdl: null,
  templateFdlSessionId: null,
  selectedTemplateId: "",
  transformResult: null,
  templateModifiedSinceTransform: false,
  activeTab: 0,
  sidebarCollapsed: false,
  gridVisible: true,
  canvasVisible: true,
  effectiveVisible: true,
  framingVisible: true,
  protectionVisible: true,
  imageVisible: true,
  hudVisible: false,
  sourceImageId: null,
  sourceImageUrl: null,
  sourceImageDimensions: null,
  outputImageId: null,
  outputImageUrl: null,
  imageOpacity: 0.7,
  statusMessage: "Ready",
  error: null,
  loading: false,

  // Actions
  setSourceFdl: (fdl, sessionId) =>
    set({
      sourceFdl: fdl,
      sourceSessionId: sessionId,
      selectedContext: fdl.contexts.length > 0 ? fdl.contexts[0].label : "",
      selectedCanvas:
        fdl.contexts[0]?.canvases?.[0]?.id ?? "",
      selectedFraming:
        fdl.contexts[0]?.canvases?.[0]?.framingDecisions?.[0]?.id ?? "",
      outputFdl: null,
      outputSessionId: null,
      outputContextLabel: null,
      outputCanvasId: null,
      outputFramingId: null,
      outputGeometry: null,
      transformResult: null,
      statusMessage: `Loaded FDL: ${fdl.uuid}`,
      error: null,
    }),

  setOutputFdl: (fdl, sessionId, geometry, result, contextLabel, canvasId, framingId) =>
    set({
      outputFdl: fdl,
      outputSessionId: sessionId,
      outputContextLabel: contextLabel,
      outputCanvasId: canvasId,
      outputFramingId: framingId,
      outputGeometry: geometry,
      transformResult: result,
      templateModifiedSinceTransform: false,
      outputImageId: null,
      outputImageUrl: null,
      activeTab: 1,
      statusMessage: "Transform complete",
    }),

  clearOutput: () =>
    set({
      outputFdl: null,
      outputSessionId: null,
      outputContextLabel: null,
      outputCanvasId: null,
      outputFramingId: null,
      outputGeometry: null,
      transformResult: null,
    }),

  setSourceGeometry: (geometry) => set({ sourceGeometry: geometry }),

  setSelectedContext: (label) =>
    set((state) => {
      const ctx = state.sourceFdl?.contexts.find((c) => c.label === label);
      const firstCanvas = ctx?.canvases?.[0];
      return {
        selectedContext: label,
        selectedCanvas: firstCanvas?.id ?? "",
        selectedFraming: firstCanvas?.framingDecisions?.[0]?.id ?? "",
        outputFdl: null,
        outputSessionId: null,
        outputContextLabel: null,
        outputCanvasId: null,
        outputFramingId: null,
        outputGeometry: null,
        transformResult: null,
      };
    }),

  setSelectedCanvas: (id) =>
    set((state) => {
      const ctx = state.sourceFdl?.contexts.find(
        (c) => c.label === state.selectedContext,
      );
      const canvas = ctx?.canvases.find((c) => c.id === id);
      return {
        selectedCanvas: id,
        selectedFraming: canvas?.framingDecisions?.[0]?.id ?? "",
        outputFdl: null,
        outputSessionId: null,
        outputContextLabel: null,
        outputCanvasId: null,
        outputFramingId: null,
        outputGeometry: null,
        transformResult: null,
      };
    }),

  setSelectedFraming: (id) =>
    set({
      selectedFraming: id,
      outputFdl: null,
      outputSessionId: null,
      outputContextLabel: null,
      outputCanvasId: null,
      outputFramingId: null,
      outputGeometry: null,
      transformResult: null,
    }),

  setCurrentTemplate: (template) =>
    set((state) => ({
      currentTemplate: template,
      templateModifiedSinceTransform: state.transformResult !== null,
    })),

  updateTemplate: (updates) =>
    set((state) => ({
      currentTemplate: { ...state.currentTemplate, ...updates },
      templateModifiedSinceTransform: state.transformResult !== null,
    })),

  setPresetMode: (mode) => set({ presetMode: mode }),
  setSelectedPreset: (name) => set({ selectedPreset: name }),

  setTemplateFdl: (fdl, sessionId) => {
    const firstTemplate = fdl.canvasTemplates[0] ?? null;
    set({
      templateFdl: fdl,
      templateFdlSessionId: sessionId,
      selectedTemplateId: firstTemplate?.id ?? "",
      ...(firstTemplate
        ? {
            currentTemplate: canvasTemplateToParams(firstTemplate),
            presetMode: false,
            selectedPreset: "",
          }
        : {}),
      statusMessage: `Loaded template FDL: ${fdl.uuid}`,
    });
  },

  setSelectedTemplateId: (id) =>
    set((state) => {
      const tpl = state.templateFdl?.canvasTemplates.find(
        (t) => t.id === id,
      );
      return {
        selectedTemplateId: id,
        ...(tpl ? { currentTemplate: canvasTemplateToParams(tpl) } : {}),
      };
    }),

  clearTemplateFdl: () =>
    set({
      templateFdl: null,
      templateFdlSessionId: null,
      selectedTemplateId: "",
    }),
  setActiveTab: (tab) => set({ activeTab: tab }),
  toggleSidebar: () =>
    set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
  toggleGrid: () =>
    set((state) => ({ gridVisible: !state.gridVisible })),

  setLayerVisibility: (layer, visible) => {
    const key = `${layer}Visible` as const;
    set({ [key]: visible } as Partial<AppState>);
  },

  setSourceImage: (id, url, dims) =>
    set({
      sourceImageId: id,
      sourceImageUrl: url,
      sourceImageDimensions: dims,
    }),

  clearSourceImage: () =>
    set({
      sourceImageId: null,
      sourceImageUrl: null,
      sourceImageDimensions: null,
    }),

  setOutputImage: (id, url) =>
    set({ outputImageId: id, outputImageUrl: url }),

  clearOutputImage: () =>
    set({ outputImageId: null, outputImageUrl: null }),

  setImageOpacity: (opacity) => set({ imageOpacity: opacity }),
  setStatus: (message) => set({ statusMessage: message }),
  setError: (error) => set({ error }),
  setLoading: (loading) => set({ loading }),
}));

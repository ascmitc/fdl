import {
  FDL,
  readFromString,
  readFromFile,
  writeToString,
} from "@asc-mitc/fdl";
import type { Canvas, Context, FramingDecision } from "@asc-mitc/fdl";
import { v4 as uuidv4 } from "uuid";
import type {
  FdlHierarchy,
  ContextData,
  CanvasData,
  FramingDecisionData,
  FramingIntentData,
  CanvasTemplateData,
  GeometryData,
  Rect,
} from "../types/api.js";

interface FdlSession {
  fdl: FDL;
  hierarchy: FdlHierarchy;
  createdAt: number;
}

const sessions = new Map<string, FdlSession>();
const SESSION_TTL_MS = 30 * 60 * 1000; // 30 minutes

// Cleanup expired sessions every 5 minutes
setInterval(() => {
  const now = Date.now();
  for (const [id, session] of sessions) {
    if (now - session.createdAt > SESSION_TTL_MS) {
      sessions.delete(id);
    }
  }
}, 5 * 60 * 1000);

function extractFramingDecision(fd: FramingDecision): FramingDecisionData {
  const protDims = fd.protectionDimensions;
  const protAnchor = fd.protectionAnchorPoint;
  return {
    id: fd.id,
    label: fd.label,
    framingIntentId: fd.framingIntentId,
    dimensions: { width: fd.dimensions.width, height: fd.dimensions.height },
    anchorPoint: { x: fd.anchorPoint.x, y: fd.anchorPoint.y },
    protectionDimensions: protDims
      ? { width: protDims.width, height: protDims.height }
      : null,
    protectionAnchorPoint: protAnchor
      ? { x: protAnchor.x, y: protAnchor.y }
      : null,
  };
}

function extractCanvas(canvas: Canvas): CanvasData {
  const effDims = canvas.effectiveDimensions;
  const effAnchor = canvas.effectiveAnchorPoint;
  const fds: FramingDecisionData[] = [];
  for (const fd of canvas.framingDecisions) {
    fds.push(extractFramingDecision(fd));
  }
  return {
    id: canvas.id,
    label: canvas.label,
    dimensions: {
      width: canvas.dimensions.width,
      height: canvas.dimensions.height,
    },
    effectiveDimensions: effDims
      ? { width: effDims.width, height: effDims.height }
      : null,
    effectiveAnchorPoint: effAnchor
      ? { x: effAnchor.x, y: effAnchor.y }
      : null,
    anamorphicSqueeze: canvas.anamorphicSqueeze,
    framingDecisions: fds,
  };
}

function extractContext(ctx: Context): ContextData {
  const canvases: CanvasData[] = [];
  for (const canvas of ctx.canvases) {
    canvases.push(extractCanvas(canvas));
  }
  return {
    label: ctx.label,
    contextCreator: ctx.contextCreator ?? "",
    canvases,
  };
}

function extractHierarchy(fdl: FDL): FdlHierarchy {
  const contexts: ContextData[] = [];
  for (const ctx of fdl.contexts) {
    contexts.push(extractContext(ctx));
  }

  const framingIntents: FramingIntentData[] = [];
  for (const fi of fdl.framingIntents) {
    framingIntents.push({
      id: fi.id,
      label: fi.label,
      aspectRatio: {
        width: fi.aspectRatio.width,
        height: fi.aspectRatio.height,
      },
      protection: fi.protection,
    });
  }

  const canvasTemplates: CanvasTemplateData[] = [];
  for (const ct of fdl.canvasTemplates) {
    const round = ct.round;
    canvasTemplates.push({
      id: ct.id,
      label: ct.label,
      targetDimensions: {
        width: ct.targetDimensions.width,
        height: ct.targetDimensions.height,
      },
      targetAnamorphicSqueeze: ct.targetAnamorphicSqueeze,
      fitSource: ct.fitSource,
      fitMethod: ct.fitMethod,
      alignmentMethodHorizontal: ct.alignmentMethodHorizontal,
      alignmentMethodVertical: ct.alignmentMethodVertical,
      preserveFromSourceCanvas: ct.preserveFromSourceCanvas,
      maximumDimensions: ct.maximumDimensions
        ? {
            width: ct.maximumDimensions.width,
            height: ct.maximumDimensions.height,
          }
        : null,
      padToMaximum: ct.padToMaximum,
      roundEven: round.even,
      roundMode: round.mode,
    });
  }

  return {
    uuid: fdl.uuid ?? "",
    version: { major: fdl.version.major, minor: fdl.version.minor },
    fdlCreator: fdl.fdlCreator ?? "",
    defaultFramingIntent: fdl.defaultFramingIntent,
    framingIntents,
    contexts,
    canvasTemplates,
  };
}

export function parseFdlFromString(json: string): {
  sessionId: string;
  hierarchy: FdlHierarchy;
} {
  const fdl = readFromString(json, true);
  const hierarchy = extractHierarchy(fdl);
  const sessionId = uuidv4();
  sessions.set(sessionId, { fdl, hierarchy, createdAt: Date.now() });
  return { sessionId, hierarchy };
}

export function parseFdlFromFile(filePath: string): {
  sessionId: string;
  hierarchy: FdlHierarchy;
} {
  const fdl = readFromFile(filePath, true);
  const hierarchy = extractHierarchy(fdl);
  const sessionId = uuidv4();
  sessions.set(sessionId, { fdl, hierarchy, createdAt: Date.now() });
  return { sessionId, hierarchy };
}

export function getSession(sessionId: string): FdlSession | undefined {
  return sessions.get(sessionId);
}

export function getFdlJson(sessionId: string, indent = 2): string | null {
  const session = sessions.get(sessionId);
  if (!session) return null;
  return session.fdl.asJson(indent);
}

export function storeFdl(fdl: FDL): {
  sessionId: string;
  hierarchy: FdlHierarchy;
} {
  const hierarchy = extractHierarchy(fdl);
  const sessionId = uuidv4();
  sessions.set(sessionId, { fdl, hierarchy, createdAt: Date.now() });
  return { sessionId, hierarchy };
}

export function computeGeometry(
  canvas: Canvas,
  framing: FramingDecision | null,
): GeometryData {
  const cRect = canvas.getRect();
  const canvasRect: Rect = {
    x: cRect.x,
    y: cRect.y,
    width: cRect.width,
    height: cRect.height,
  };

  const eRect = canvas.getEffectiveRect();
  const effectiveRect: Rect | null = eRect
    ? { x: eRect.x, y: eRect.y, width: eRect.width, height: eRect.height }
    : null;

  let framingRect: Rect | null = null;
  let protectionRect: Rect | null = null;
  let anchorPoint = null;

  if (framing) {
    const fRect = framing.getRect();
    framingRect = {
      x: fRect.x,
      y: fRect.y,
      width: fRect.width,
      height: fRect.height,
    };

    const pRect = framing.getProtectionRect();
    protectionRect = pRect
      ? { x: pRect.x, y: pRect.y, width: pRect.width, height: pRect.height }
      : null;

    anchorPoint = { x: framing.anchorPoint.x, y: framing.anchorPoint.y };
  }

  return { canvasRect, effectiveRect, framingRect, protectionRect, anchorPoint };
}

export function findCanvasAndFraming(
  fdl: FDL,
  contextLabel: string,
  canvasId: string,
  framingId: string,
): { context: Context; canvas: Canvas; framing: FramingDecision } | null {
  let targetContext: Context | null = null;
  for (const ctx of fdl.contexts) {
    if (ctx.label === contextLabel) {
      targetContext = ctx;
      break;
    }
  }
  if (!targetContext) return null;

  let targetCanvas: Canvas | null = null;
  for (const c of targetContext.canvases) {
    if (c.id === canvasId) {
      targetCanvas = c;
      break;
    }
  }
  if (!targetCanvas) return null;

  let targetFraming: FramingDecision | null = null;
  for (const fd of targetCanvas.framingDecisions) {
    if (fd.id === framingId) {
      targetFraming = fd;
      break;
    }
  }
  if (!targetFraming) return null;

  return {
    context: targetContext,
    canvas: targetCanvas,
    framing: targetFraming,
  };
}

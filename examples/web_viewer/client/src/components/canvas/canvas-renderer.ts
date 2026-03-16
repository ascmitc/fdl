// Canvas rendering engine — port of Python CanvasRenderer
// (packages/fdl_viewer/src/fdl_viewer/views/canvas/canvas_renderer.py)

import type { Rect, GeometryData, Dimensions, Point } from "@/api/types";
import {
  COLORS,
  LINE_WIDTHS,
  FILL_OPACITY,
  GRID_SPACING,
  CROSSHAIR_SIZE,
  colorWithAlpha,
} from "./geometry";

export interface Viewport {
  offsetX: number;
  offsetY: number;
  scale: number;
}

export interface HudData {
  sourceLines: [string, string][];
  outputLines: [string, string][];
  templateLines: [string, string][];
}

export interface RenderOptions {
  geometry: GeometryData | null;
  showGrid: boolean;
  showCanvas: boolean;
  showEffective: boolean;
  showFraming: boolean;
  showProtection: boolean;
  showImage: boolean;
  showHud: boolean;
  imageOpacity: number;
  isSource: boolean;
  image: HTMLImageElement | null;
  canvasDimensions: Dimensions | null;
  effectiveDimensions: Dimensions | null;
  framingDimensions: Dimensions | null;
  protectionDimensions: Dimensions | null;
  effectiveAnchorPoint: Point | null;
  framingAnchorPoint: Point | null;
  protectionAnchorPoint: Point | null;
  hudData?: HudData;
}

export function render(
  ctx: CanvasRenderingContext2D,
  canvasWidth: number,
  canvasHeight: number,
  viewport: Viewport,
  options: RenderOptions,
): void {
  const dpr = window.devicePixelRatio || 1;

  // Clear
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.fillStyle = COLORS.BACKGROUND;
  ctx.fillRect(0, 0, canvasWidth, canvasHeight);

  if (!options.geometry) return;
  const g = options.geometry;

  // Apply viewport transform
  ctx.setTransform(
    viewport.scale * dpr,
    0,
    0,
    viewport.scale * dpr,
    viewport.offsetX * dpr,
    viewport.offsetY * dpr,
  );

  // 1. Draw grid
  if (options.showGrid && g.canvasRect) {
    drawGrid(ctx, g.canvasRect, viewport.scale);
  }

  // 2. Draw image underlay
  if (options.showImage && options.image) {
    ctx.globalAlpha = options.imageOpacity;
    ctx.drawImage(options.image, 0, 0);
    ctx.globalAlpha = 1;
  }

  // 3. Draw canvas rect
  if (options.showCanvas && g.canvasRect) {
    drawRect(ctx, g.canvasRect, COLORS.CANVAS, LINE_WIDTHS.CANVAS, false, viewport.scale);
  }

  // 4. Draw effective rect
  if (options.showEffective && g.effectiveRect) {
    drawRect(ctx, g.effectiveRect, COLORS.EFFECTIVE, LINE_WIDTHS.EFFECTIVE, false, viewport.scale);
  }

  // 5. Draw protection rect (dashed)
  if (options.showProtection && g.protectionRect) {
    drawRect(ctx, g.protectionRect, COLORS.PROTECTION, LINE_WIDTHS.PROTECTION, true, viewport.scale);
  }

  // 6. Draw framing rect
  if (options.showFraming && g.framingRect) {
    const color = options.isSource ? COLORS.FRAMING_SOURCE : COLORS.FRAMING_OUTPUT;
    drawRect(ctx, g.framingRect, color, LINE_WIDTHS.FRAMING, false, viewport.scale);
    // Crosshair at framing center
    const cx = g.framingRect.x + g.framingRect.width / 2;
    const cy = g.framingRect.y + g.framingRect.height / 2;
    drawCrosshair(ctx, cx, cy, viewport.scale);
  }

  // 7. Draw dimension labels
  drawDimensionLabels(ctx, options, viewport.scale);

  // 8. Draw anchor labels
  drawAnchorLabels(ctx, options, viewport.scale);

  // 9. Draw HUD (in screen space, after resetting transform)
  if (options.showHud && options.hudData) {
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    drawHud(ctx, canvasWidth / dpr, canvasHeight / dpr, options.hudData);
  }
}

function drawGrid(ctx: CanvasRenderingContext2D, bounds: Rect, scale: number): void {
  ctx.strokeStyle = COLORS.GRID;
  ctx.lineWidth = LINE_WIDTHS.GRID / scale;
  ctx.beginPath();

  for (let x = 0; x <= bounds.width; x += GRID_SPACING) {
    ctx.moveTo(x, 0);
    ctx.lineTo(x, bounds.height);
  }
  for (let y = 0; y <= bounds.height; y += GRID_SPACING) {
    ctx.moveTo(0, y);
    ctx.lineTo(bounds.width, y);
  }
  ctx.stroke();
}

function drawRect(
  ctx: CanvasRenderingContext2D,
  rect: Rect,
  color: string,
  lineWidth: number,
  dashed: boolean,
  scale: number,
): void {
  // Fill
  ctx.fillStyle = colorWithAlpha(color, FILL_OPACITY);
  ctx.fillRect(rect.x, rect.y, rect.width, rect.height);

  // Stroke
  ctx.strokeStyle = color;
  ctx.lineWidth = lineWidth / scale;
  if (dashed) {
    ctx.setLineDash([8 / scale, 4 / scale]);
  } else {
    ctx.setLineDash([]);
  }
  ctx.strokeRect(rect.x, rect.y, rect.width, rect.height);
  ctx.setLineDash([]);
}

function drawCrosshair(ctx: CanvasRenderingContext2D, cx: number, cy: number, scale: number): void {
  const size = CROSSHAIR_SIZE / scale;
  ctx.strokeStyle = COLORS.CROSSHAIR;
  ctx.lineWidth = 1 / scale;
  ctx.beginPath();
  ctx.moveTo(cx - size, cy);
  ctx.lineTo(cx + size, cy);
  ctx.moveTo(cx, cy - size);
  ctx.lineTo(cx, cy + size);
  ctx.stroke();
}

function drawDimensionLabels(
  ctx: CanvasRenderingContext2D,
  options: RenderOptions,
  scale: number,
): void {
  const fontSize = 30 / scale;
  ctx.font = `bold ${fontSize}px Arial`;
  ctx.textBaseline = "top";

  const g = options.geometry!;
  const labelOffset = 10 / scale;

  // Canvas dimensions (right-aligned)
  if (options.showCanvas && g.canvasRect && options.canvasDimensions) {
    const text = `${Math.round(options.canvasDimensions.width)} x ${Math.round(options.canvasDimensions.height)}`;
    ctx.fillStyle = COLORS.CANVAS;
    const metrics = ctx.measureText(text);
    ctx.fillText(
      text,
      g.canvasRect.x + g.canvasRect.width - metrics.width,
      g.canvasRect.y + g.canvasRect.height + labelOffset,
    );
  }

  // Effective dimensions (left-aligned)
  if (options.showEffective && g.effectiveRect && options.effectiveDimensions) {
    const text = `${Math.round(options.effectiveDimensions.width)} x ${Math.round(options.effectiveDimensions.height)}`;
    ctx.fillStyle = COLORS.EFFECTIVE;
    ctx.fillText(
      text,
      g.effectiveRect.x,
      g.effectiveRect.y + g.effectiveRect.height + labelOffset,
    );
  }

  // Protection dimensions (right-aligned)
  if (options.showProtection && g.protectionRect && options.protectionDimensions) {
    const text = `${Math.round(options.protectionDimensions.width)} x ${Math.round(options.protectionDimensions.height)}`;
    ctx.fillStyle = COLORS.PROTECTION;
    const metrics = ctx.measureText(text);
    ctx.fillText(
      text,
      g.protectionRect.x + g.protectionRect.width - metrics.width,
      g.protectionRect.y + g.protectionRect.height + labelOffset,
    );
  }

  // Framing dimensions (centered)
  if (options.showFraming && g.framingRect && options.framingDimensions) {
    const text = `${Math.round(options.framingDimensions.width)} x ${Math.round(options.framingDimensions.height)}`;
    ctx.fillStyle = options.isSource ? COLORS.FRAMING_SOURCE : COLORS.FRAMING_OUTPUT;
    const metrics = ctx.measureText(text);
    ctx.fillText(
      text,
      g.framingRect.x + g.framingRect.width / 2 - metrics.width / 2,
      g.framingRect.y + g.framingRect.height + labelOffset,
    );
  }
}

function drawAnchorLabels(
  ctx: CanvasRenderingContext2D,
  options: RenderOptions,
  scale: number,
): void {
  const fontSize = 20 / scale;
  ctx.font = `${fontSize}px Arial`;
  ctx.textBaseline = "bottom";
  const offsetStep = 30 / scale;
  const padX = 5 / scale;
  const padY = 5 / scale;

  const g = options.geometry!;

  // Effective anchor (2x offset up)
  if (options.showEffective && g.effectiveRect && options.effectiveAnchorPoint) {
    const text = `(${Math.round(options.effectiveAnchorPoint.x)}, ${Math.round(options.effectiveAnchorPoint.y)})`;
    ctx.fillStyle = COLORS.EFFECTIVE;
    ctx.fillText(
      text,
      g.effectiveRect.x - padX,
      g.effectiveRect.y - padY - offsetStep * 2,
    );
  }

  // Protection anchor (1x offset up)
  if (options.showProtection && g.protectionRect && options.protectionAnchorPoint) {
    const text = `(${Math.round(options.protectionAnchorPoint.x)}, ${Math.round(options.protectionAnchorPoint.y)})`;
    ctx.fillStyle = COLORS.PROTECTION;
    ctx.fillText(
      text,
      g.protectionRect.x - padX,
      g.protectionRect.y - padY - offsetStep,
    );
  }

  // Framing anchor (no offset)
  if (options.showFraming && g.framingRect && options.framingAnchorPoint) {
    const text = `(${Math.round(options.framingAnchorPoint.x)}, ${Math.round(options.framingAnchorPoint.y)})`;
    ctx.fillStyle = options.isSource ? COLORS.FRAMING_SOURCE : COLORS.FRAMING_OUTPUT;
    ctx.fillText(
      text,
      g.framingRect.x - padX,
      g.framingRect.y - padY,
    );
  }
}

function drawHud(
  ctx: CanvasRenderingContext2D,
  screenWidth: number,
  screenHeight: number,
  data: HudData,
): void {
  const fontSize = 11;
  const lineHeight = 16;
  const padding = 10;
  const colGap = 24;
  const headerFont = `bold ${fontSize}px monospace`;
  const bodyFont = `${fontSize}px monospace`;

  ctx.textBaseline = "top";

  // Measure column widths
  const measureCol = (lines: [string, string][], header: string): number => {
    ctx.font = headerFont;
    let maxW = ctx.measureText(header).width;
    ctx.font = bodyFont;
    for (const [label, value] of lines) {
      maxW = Math.max(maxW, ctx.measureText(`${label}: ${value}`).width);
    }
    return maxW;
  };

  const col1W = measureCol(data.sourceLines, "SOURCE");
  const col2W = measureCol(data.outputLines, "OUTPUT");
  const col3W = measureCol(data.templateLines, "TEMPLATE");

  const totalW = col1W + col2W + col3W + colGap * 2 + padding * 2;
  const maxLines = Math.max(
    data.sourceLines.length,
    data.outputLines.length,
    data.templateLines.length,
  );
  const totalH = (maxLines + 1) * lineHeight + padding * 2 + 4; // +1 for header, +4 for separator

  // Position at bottom-center of the canvas area
  const boxX = (screenWidth - totalW) / 2;
  const boxY = screenHeight - totalH - 8;

  // Draw background
  ctx.fillStyle = "rgba(0, 0, 0, 0.75)";
  ctx.beginPath();
  const r = 4;
  ctx.moveTo(boxX + r, boxY);
  ctx.lineTo(boxX + totalW - r, boxY);
  ctx.quadraticCurveTo(boxX + totalW, boxY, boxX + totalW, boxY + r);
  ctx.lineTo(boxX + totalW, boxY + totalH - r);
  ctx.quadraticCurveTo(boxX + totalW, boxY + totalH, boxX + totalW - r, boxY + totalH);
  ctx.lineTo(boxX + r, boxY + totalH);
  ctx.quadraticCurveTo(boxX, boxY + totalH, boxX, boxY + totalH - r);
  ctx.lineTo(boxX, boxY + r);
  ctx.quadraticCurveTo(boxX, boxY, boxX + r, boxY);
  ctx.fill();

  // Column x positions
  const x1 = boxX + padding;
  const x2 = x1 + col1W + colGap;
  const x3 = x2 + col2W + colGap;

  let y = boxY + padding;

  // Draw headers
  ctx.font = headerFont;
  ctx.fillStyle = "rgba(255, 255, 255, 0.5)";
  ctx.fillText("SOURCE", x1, y);
  ctx.fillText("OUTPUT", x2, y);
  ctx.fillText("TEMPLATE", x3, y);
  y += lineHeight;

  // Separator line
  ctx.strokeStyle = "rgba(255, 255, 255, 0.2)";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(boxX + padding, y);
  ctx.lineTo(boxX + totalW - padding, y);
  ctx.stroke();
  y += 4;

  // Draw data rows
  ctx.font = bodyFont;
  for (let i = 0; i < maxLines; i++) {
    if (i < data.sourceLines.length) {
      const [label, value] = data.sourceLines[i];
      ctx.fillStyle = "rgba(255, 255, 255, 0.4)";
      ctx.fillText(`${label}: `, x1, y);
      const labelW = ctx.measureText(`${label}: `).width;
      ctx.fillStyle = "rgba(255, 255, 255, 0.85)";
      ctx.fillText(value, x1 + labelW, y);
    }
    if (i < data.outputLines.length) {
      const [label, value] = data.outputLines[i];
      ctx.fillStyle = "rgba(255, 255, 255, 0.4)";
      ctx.fillText(`${label}: `, x2, y);
      const labelW = ctx.measureText(`${label}: `).width;
      ctx.fillStyle = "rgba(255, 255, 255, 0.85)";
      ctx.fillText(value, x2 + labelW, y);
    }
    if (i < data.templateLines.length) {
      const [label, value] = data.templateLines[i];
      ctx.fillStyle = "rgba(255, 255, 255, 0.4)";
      ctx.fillText(`${label}: `, x3, y);
      const labelW = ctx.measureText(`${label}: `).width;
      ctx.fillStyle = "rgba(255, 255, 255, 0.85)";
      ctx.fillText(value, x3 + labelW, y);
    }
    y += lineHeight;
  }
}

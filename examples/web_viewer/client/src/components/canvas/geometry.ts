// Color constants and drawing styles matching the Python GeometryHelper
// (packages/fdl_viewer/src/fdl_viewer/utils/geometry.py)

export const COLORS = {
  CANVAS: "#808080",
  EFFECTIVE: "#0066CC",
  PROTECTION: "#FF9900",
  FRAMING_SOURCE: "#00CC66",
  FRAMING_OUTPUT: "#00CC66",
  GRID: "#505050",
  CROSSHAIR: "rgba(255,255,255,0.5)",
  HUD_TEXT: "rgba(255,255,255,0.6)",
  BACKGROUND: "#1a1a1a",
} as const;

export const LINE_WIDTHS = {
  CANVAS: 2,
  EFFECTIVE: 1.5,
  PROTECTION: 1.5,
  FRAMING: 2,
  GRID: 0.5,
} as const;

export const FILL_OPACITY = 0.15;
export const GRID_SPACING = 100;
export const CROSSHAIR_SIZE = 20;

export function colorWithAlpha(hex: string, alpha: number): string {
  if (hex.startsWith("rgba")) return hex;
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${alpha})`;
}

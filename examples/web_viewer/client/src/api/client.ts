import type {
  ParseResponse,
  TransformResponse,
  TemplateParams,
  PresetInfo,
  CanvasTemplateData,
  TemplateOptions,
  GeometryData,
} from "./types";

const BASE = "/api";

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init);
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(body.error || `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

// FDL endpoints
export async function parseFdlFile(file: File): Promise<ParseResponse> {
  const form = new FormData();
  form.append("file", file);
  return fetchJson<ParseResponse>(`${BASE}/fdl/parse`, {
    method: "POST",
    body: form,
  });
}

export async function parseFdlString(json: string): Promise<ParseResponse> {
  return fetchJson<ParseResponse>(`${BASE}/fdl/parse-string`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fdl: JSON.parse(json) }),
  });
}

export async function getFdlHierarchy(
  sessionId: string,
): Promise<ParseResponse> {
  return fetchJson<ParseResponse>(`${BASE}/fdl/${sessionId}`);
}

export async function getFdlJson(sessionId: string): Promise<string> {
  const res = await fetchJson<{ json: string }>(
    `${BASE}/fdl/${sessionId}/json`,
  );
  return res.json;
}

export async function getGeometry(
  sessionId: string,
  context: string,
  canvas: string,
  framing: string,
): Promise<GeometryData> {
  const params = new URLSearchParams({ context, canvas, framing });
  return fetchJson<GeometryData>(
    `${BASE}/fdl/${sessionId}/geometry?${params}`,
  );
}

export async function transform(
  sourceSessionId: string,
  contextLabel: string,
  canvasId: string,
  framingId: string,
  template: TemplateParams,
): Promise<TransformResponse> {
  return fetchJson<TransformResponse>(`${BASE}/fdl/transform`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sourceSessionId,
      contextLabel,
      canvasId,
      framingId,
      template,
    }),
  });
}

export function getExportUrl(sessionId: string): string {
  return `${BASE}/fdl/${sessionId}/export`;
}

// Presets
export async function getPresets(): Promise<PresetInfo[]> {
  return fetchJson<PresetInfo[]>(`${BASE}/presets`);
}

export async function getPreset(name: string): Promise<CanvasTemplateData> {
  return fetchJson<CanvasTemplateData>(`${BASE}/presets/${encodeURIComponent(name)}`);
}

export async function getTemplateOptions(): Promise<TemplateOptions> {
  return fetchJson<TemplateOptions>(`${BASE}/presets/options/all`);
}

// Image endpoints
export async function uploadImage(
  file: File,
): Promise<{ id: string; url: string; width: number; height: number }> {
  const form = new FormData();
  form.append("file", file);
  return fetchJson(`${BASE}/image/upload`, { method: "POST", body: form });
}

export function getImageUrl(imageId: string): string {
  return `${BASE}/image/${imageId}`;
}

export async function transformImage(
  imageId: string,
  sourceSessionId: string,
  contextLabel: string,
  canvasId: string,
  framingId: string,
  template: TemplateParams,
): Promise<{ id: string; url: string; width: number; height: number }> {
  return fetchJson(`${BASE}/image/transform`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      imageId,
      sourceSessionId,
      contextLabel,
      canvasId,
      framingId,
      template,
    }),
  });
}

export function getImageDownloadUrl(imageId: string): string {
  return `${BASE}/image/${imageId}/download`;
}

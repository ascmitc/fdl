import { Router } from "express";
import { fdlUpload } from "../middleware/upload.js";
import {
  parseFdlFromString,
  getSession,
  getFdlJson,
  computeGeometry,
  findCanvasAndFraming,
} from "../services/fdl-service.js";
import { applyTransform } from "../services/transform-service.js";
import type { TransformRequest } from "../types/api.js";

const router = Router();

// Parse FDL from uploaded file
router.post("/parse", fdlUpload.single("file"), (req, res) => {
  try {
    if (!req.file) {
      res.status(400).json({ error: "No file uploaded" });
      return;
    }
    const json = req.file.buffer.toString("utf-8");
    const result = parseFdlFromString(json);
    res.json(result);
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : "Failed to parse FDL";
    res.status(400).json({ error: message });
  }
});

// Parse FDL from JSON string body
router.post("/parse-string", (req, res) => {
  try {
    const json =
      typeof req.body === "string" ? req.body : JSON.stringify(req.body.fdl);
    const result = parseFdlFromString(json);
    res.json(result);
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : "Failed to parse FDL";
    res.status(400).json({ error: message });
  }
});

// Get stored FDL hierarchy
router.get("/:id", (req, res) => {
  const session = getSession(req.params.id);
  if (!session) {
    res.status(404).json({ error: "Session not found" });
    return;
  }
  res.json({ sessionId: req.params.id, hierarchy: session.hierarchy });
});

// Get FDL as formatted JSON
router.get("/:id/json", (req, res) => {
  const indent = parseInt(req.query.indent as string) || 2;
  const json = getFdlJson(req.params.id, indent);
  if (!json) {
    res.status(404).json({ error: "Session not found" });
    return;
  }
  res.json({ json });
});

// Get geometry for a specific selection
router.get("/:id/geometry", (req, res) => {
  const session = getSession(req.params.id);
  if (!session) {
    res.status(404).json({ error: "Session not found" });
    return;
  }

  const { context, canvas, framing } = req.query as {
    context: string;
    canvas: string;
    framing: string;
  };

  if (!context || !canvas) {
    res.status(400).json({ error: "context and canvas query params required" });
    return;
  }

  const found = findCanvasAndFraming(
    session.fdl,
    context,
    canvas,
    framing || "",
  );
  if (!found) {
    res.status(404).json({ error: "Selection not found in FDL" });
    return;
  }

  const geometry = computeGeometry(found.canvas, framing ? found.framing : null);
  res.json(geometry);
});

// Apply template transform
router.post("/transform", (req, res) => {
  try {
    const body = req.body as TransformRequest;
    const result = applyTransform(
      body.sourceSessionId,
      body.contextLabel,
      body.canvasId,
      body.framingId,
      body.template,
    );
    res.json(result);
  } catch (err: unknown) {
    const message =
      err instanceof Error ? err.message : "Transform failed";
    res.status(400).json({ error: message });
  }
});

// Export FDL as downloadable file
router.get("/:id/export", (req, res) => {
  const json = getFdlJson(req.params.id, 2);
  if (!json) {
    res.status(404).json({ error: "Session not found" });
    return;
  }
  res.setHeader("Content-Type", "application/json");
  res.setHeader(
    "Content-Disposition",
    `attachment; filename="output.fdl"`,
  );
  res.send(json);
});

export default router;

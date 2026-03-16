import { Router } from "express";
import { imageUpload } from "../middleware/upload.js";
import {
  storeImage,
  getImage,
  getImageMetadata,
  transformImage,
} from "../services/image-service.js";
import { getFdlJson } from "../services/fdl-service.js";

const router = Router();

// Upload an image
router.post("/upload", imageUpload.single("file"), async (req, res) => {
  try {
    if (!req.file) {
      res.status(400).json({ error: "No file uploaded" });
      return;
    }
    const result = await storeImage(req.file.path, req.file.originalname);
    res.json(result);
  } catch (err: unknown) {
    const message =
      err instanceof Error ? err.message : "Failed to upload image";
    res.status(400).json({ error: message });
  }
});

// Serve an uploaded image
router.get("/:id", (req, res) => {
  const meta = getImageMetadata(req.params.id);
  if (!meta) {
    res.status(404).json({ error: "Image not found" });
    return;
  }
  res.sendFile(meta.filePath);
});

// Transform image with FDL parameters via Python OIIO bridge
router.post("/transform", async (req, res) => {
  try {
    const { imageId, sourceSessionId, contextLabel, canvasId, framingId, template } =
      req.body;
    const fdlJson = getFdlJson(sourceSessionId);
    if (!fdlJson) {
      res.status(404).json({ error: "Source FDL session not found" });
      return;
    }
    const result = await transformImage(
      imageId,
      fdlJson,
      contextLabel,
      canvasId,
      framingId,
      template,
    );
    res.json(result);
  } catch (err: unknown) {
    const message =
      err instanceof Error ? err.message : "Failed to transform image";
    res.status(400).json({ error: message });
  }
});

// Download transformed image
router.get("/:id/download", (req, res) => {
  const meta = getImageMetadata(req.params.id);
  if (!meta) {
    res.status(404).json({ error: "Image not found" });
    return;
  }
  res.setHeader("Content-Type", meta.mimeType);
  res.setHeader(
    "Content-Disposition",
    `attachment; filename="${meta.originalName}"`,
  );
  res.sendFile(meta.filePath);
});

export default router;

import { Router } from "express";
import type { PresetInfo, CanvasTemplateData } from "../types/api.js";

interface PresetDef {
  name: string;
  id: string;
  label: string;
  width: number;
  height: number;
}

const STANDARD_PRESETS: PresetDef[] = [
  { name: "HD 1080p", id: "preset_hd_1080p", label: "HD 1080p", width: 1920, height: 1080 },
  { name: "UHD 4K", id: "preset_uhd_4k", label: "UHD 4K", width: 3840, height: 2160 },
  { name: "DCI 2K", id: "preset_dci_2k", label: "DCI 2K", width: 2048, height: 1080 },
  { name: "DCI 4K", id: "preset_dci_4k", label: "DCI 4K", width: 4096, height: 2160 },
  { name: "DCI 2K Flat", id: "preset_dci_2k_flat", label: "DCI 2K Flat", width: 1998, height: 1080 },
  { name: "DCI 4K Flat", id: "preset_dci_4k_flat", label: "DCI 4K Flat", width: 3996, height: 2160 },
  { name: "DCI 2K Scope", id: "preset_dci_2k_scope", label: "DCI 2K Scope", width: 2048, height: 858 },
  { name: "DCI 4K Scope", id: "preset_dci_4k_scope", label: "DCI 4K Scope", width: 4096, height: 1716 },
];

function presetToTemplate(p: PresetDef): CanvasTemplateData {
  return {
    id: p.id,
    label: p.label,
    targetDimensions: { width: p.width, height: p.height },
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
}

const router = Router();

router.get("/", (_req, res) => {
  const presets: PresetInfo[] = STANDARD_PRESETS.map((p) => ({
    name: p.name,
    id: p.id,
    label: p.label,
    targetDimensions: { width: p.width, height: p.height },
  }));
  res.json(presets);
});

router.get("/:name", (req, res) => {
  const preset = STANDARD_PRESETS.find(
    (p) => p.name === req.params.name || p.id === req.params.name,
  );
  if (!preset) {
    res.status(404).json({ error: `Preset not found: ${req.params.name}` });
    return;
  }
  res.json(presetToTemplate(preset));
});

// Dropdown options matching Python template_presets.py
router.get("/options/all", (_req, res) => {
  res.json({
    fitSource: [
      { value: "framing_decision.dimensions", label: "Framing Decision" },
      { value: "framing_decision.protection_dimensions", label: "Protection Dimensions" },
      { value: "canvas.effective_dimensions", label: "Effective Canvas" },
      { value: "canvas.dimensions", label: "Full Canvas" },
    ],
    fitMethod: [
      { value: "fit_all", label: "Fit All (letterbox/pillarbox)" },
      { value: "fill", label: "Fill (may crop)" },
      { value: "width", label: "Fit Width" },
      { value: "height", label: "Fit Height" },
    ],
    alignmentHorizontal: [
      { value: "left", label: "Left" },
      { value: "center", label: "Center" },
      { value: "right", label: "Right" },
    ],
    alignmentVertical: [
      { value: "top", label: "Top" },
      { value: "center", label: "Center" },
      { value: "bottom", label: "Bottom" },
    ],
    preserve: [
      { value: "", label: "None" },
      { value: "canvas.dimensions", label: "Canvas" },
      { value: "canvas.effective_dimensions", label: "Effective Canvas" },
      { value: "framing_decision.protection_dimensions", label: "Protection" },
      { value: "framing_decision.dimensions", label: "Framing Decision" },
    ],
    roundEven: [
      { value: "whole", label: "Whole Numbers" },
      { value: "even", label: "Even Numbers" },
    ],
    roundMode: [
      { value: "up", label: "Round Up" },
      { value: "down", label: "Round Down" },
      { value: "round", label: "Round Nearest" },
    ],
  });
});

export default router;

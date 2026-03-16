import { useCallback, useRef, useState, useEffect } from "react";
import { useAppStore } from "@/store/app-store";
import { parseFdlFile, getPresets, getPreset } from "@/api/client";
import type { PresetInfo } from "@/api/types";

function DropZone({
  label,
  onFile,
  accept = ".fdl,.json",
}: {
  label: string;
  onFile: (file: File) => void;
  accept?: string;
}) {
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) onFile(file);
    },
    [onFile],
  );

  return (
    <div
      className={`border-2 border-dashed rounded-md p-3 text-center cursor-pointer transition-colors ${
        dragOver
          ? "border-primary bg-primary/10"
          : "border-border hover:border-muted-foreground"
      }`}
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
    >
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="text-xs text-muted-foreground/60 mt-1">
        Drop file or click to browse
      </p>
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) onFile(file);
          e.target.value = "";
        }}
      />
    </div>
  );
}

export function FileLoader() {
  const setSourceFdl = useAppStore((s) => s.setSourceFdl);
  const setCurrentTemplate = useAppStore((s) => s.setCurrentTemplate);
  const setError = useAppStore((s) => s.setError);
  const setLoading = useAppStore((s) => s.setLoading);
  const setStatus = useAppStore((s) => s.setStatus);
  const presetMode = useAppStore((s) => s.presetMode);
  const setPresetMode = useAppStore((s) => s.setPresetMode);
  const selectedPreset = useAppStore((s) => s.selectedPreset);
  const setSelectedPreset = useAppStore((s) => s.setSelectedPreset);
  const templateFdl = useAppStore((s) => s.templateFdl);
  const selectedTemplateId = useAppStore((s) => s.selectedTemplateId);
  const setTemplateFdl = useAppStore((s) => s.setTemplateFdl);
  const setSelectedTemplateId = useAppStore((s) => s.setSelectedTemplateId);
  const clearTemplateFdl = useAppStore((s) => s.clearTemplateFdl);

  const [presets, setPresets] = useState<PresetInfo[]>([]);

  useEffect(() => {
    getPresets().then(setPresets).catch(console.error);
  }, []);

  const handleSourceFile = useCallback(
    async (file: File) => {
      try {
        setLoading(true);
        setError(null);
        const result = await parseFdlFile(file);
        setSourceFdl(result.hierarchy, result.sessionId);
        setStatus(`Loaded source: ${file.name}`);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load FDL");
      } finally {
        setLoading(false);
      }
    },
    [setSourceFdl, setError, setLoading, setStatus],
  );

  const handleTemplateFdlFile = useCallback(
    async (file: File) => {
      try {
        setLoading(true);
        setError(null);
        const result = await parseFdlFile(file);
        if (result.hierarchy.canvasTemplates.length === 0) {
          setError("FDL file contains no canvas templates");
          return;
        }
        setTemplateFdl(result.hierarchy, result.sessionId);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load template FDL",
        );
      } finally {
        setLoading(false);
      }
    },
    [setTemplateFdl, setError, setLoading],
  );

  const handlePresetChange = useCallback(
    async (presetName: string) => {
      setSelectedPreset(presetName);
      if (!presetName) return;
      try {
        const tpl = await getPreset(presetName);
        setCurrentTemplate({
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
        });
        setStatus(`Applied preset: ${presetName}`);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load preset");
      }
    },
    [setCurrentTemplate, setSelectedPreset, setError, setStatus],
  );

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-foreground">Files</h3>
      <DropZone label="Source FDL" onFile={handleSourceFile} />

      {/* Template FDL zone — hidden when preset mode is on */}
      {!presetMode && (
        <div className="space-y-1">
          {!templateFdl ? (
            <DropZone label="Template FDL" onFile={handleTemplateFdlFile} />
          ) : (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground">
                  Template: {templateFdl.canvasTemplates.length} template
                  {templateFdl.canvasTemplates.length !== 1 ? "s" : ""}
                </span>
                <button
                  onClick={clearTemplateFdl}
                  className="text-destructive hover:underline text-xs"
                >
                  Clear
                </button>
              </div>
              {templateFdl.canvasTemplates.length > 1 && (
                <select
                  value={selectedTemplateId}
                  onChange={(e) => setSelectedTemplateId(e.target.value)}
                  className="w-full h-8 rounded-md border border-input bg-background px-2 text-sm"
                >
                  {templateFdl.canvasTemplates.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.label || t.id} ({t.targetDimensions.width}x
                      {t.targetDimensions.height})
                    </option>
                  ))}
                </select>
              )}
            </div>
          )}
        </div>
      )}

      {/* Preset mode — disabled when template FDL is loaded */}
      <div className="space-y-2">
        <label className="flex items-center gap-2 text-xs text-muted-foreground">
          <input
            type="checkbox"
            checked={presetMode}
            onChange={(e) => setPresetMode(e.target.checked)}
            disabled={!!templateFdl}
            className="rounded"
          />
          Use preset template
        </label>
        {presetMode && (
          <select
            value={selectedPreset}
            onChange={(e) => handlePresetChange(e.target.value)}
            className="w-full h-9 rounded-md border border-input bg-background px-3 text-sm"
          >
            <option value="">Select preset...</option>
            {presets.map((p) => (
              <option key={p.id} value={p.name}>
                {p.name} ({p.targetDimensions.width}x
                {p.targetDimensions.height})
              </option>
            ))}
          </select>
        )}
      </div>
    </div>
  );
}

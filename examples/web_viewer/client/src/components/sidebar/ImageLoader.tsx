import { useCallback, useRef, useState } from "react";
import { useAppStore, getSelectedCanvas } from "@/store/app-store";
import { uploadImage } from "@/api/client";

export function ImageLoader() {
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const sourceImageUrl = useAppStore((s) => s.sourceImageUrl);
  const sourceImageDimensions = useAppStore((s) => s.sourceImageDimensions);
  const imageOpacity = useAppStore((s) => s.imageOpacity);
  const setSourceImage = useAppStore((s) => s.setSourceImage);
  const clearSourceImage = useAppStore((s) => s.clearSourceImage);
  const setImageOpacity = useAppStore((s) => s.setImageOpacity);
  const sourceCanvas = useAppStore(getSelectedCanvas);
  const setError = useAppStore((s) => s.setError);
  const setStatus = useAppStore((s) => s.setStatus);
  const setLoading = useAppStore((s) => s.setLoading);

  const handleFile = useCallback(
    async (file: File) => {
      try {
        setLoading(true);
        setError(null);
        const result = await uploadImage(file);
        setSourceImage(result.id, result.url, {
          width: result.width,
          height: result.height,
        });
        // Validate dimensions match canvas
        if (sourceCanvas) {
          const cw = Math.round(sourceCanvas.dimensions.width);
          const ch = Math.round(sourceCanvas.dimensions.height);
          if (result.width !== cw || result.height !== ch) {
            setStatus(
              `Warning: Image (${result.width}x${result.height}) does not match canvas (${cw}x${ch})`,
            );
          } else {
            setStatus(`Loaded image: ${file.name} (${result.width}x${result.height})`);
          }
        } else {
          setStatus(`Loaded image: ${file.name} (${result.width}x${result.height})`);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to upload image");
      } finally {
        setLoading(false);
      }
    },
    [setSourceImage, setError, setLoading, setStatus],
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile],
  );

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-foreground">Image Underlay</h3>

      {!sourceImageUrl ? (
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
          <p className="text-xs text-muted-foreground">
            Drop image or click to browse
          </p>
          <p className="text-xs text-muted-foreground/60">
            PNG, JPEG, WebP, TIFF
          </p>
          <input
            ref={inputRef}
            type="file"
            accept="image/png,image/jpeg,image/webp,image/tiff"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleFile(file);
              e.target.value = "";
            }}
          />
        </div>
      ) : (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>
              {sourceImageDimensions?.width}x{sourceImageDimensions?.height}
            </span>
            <button
              onClick={clearSourceImage}
              className="text-destructive hover:underline"
            >
              Clear
            </button>
          </div>

          <div className="space-y-1">
            <label className="text-xs text-muted-foreground">
              Opacity: {Math.round(imageOpacity * 100)}%
            </label>
            <input
              type="range"
              min={0}
              max={100}
              value={Math.round(imageOpacity * 100)}
              onChange={(e) => setImageOpacity(Number(e.target.value) / 100)}
              className="w-full h-2 rounded-lg appearance-none bg-secondary cursor-pointer"
            />
          </div>
        </div>
      )}
    </div>
  );
}

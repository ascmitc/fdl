import { useCallback } from "react";
import { useAppStore, canTransform } from "@/store/app-store";
import { transform, transformImage } from "@/api/client";

export function TransformButton() {
  const ready = useAppStore(canTransform);
  const sourceSessionId = useAppStore((s) => s.sourceSessionId);
  const selectedContext = useAppStore((s) => s.selectedContext);
  const selectedCanvas = useAppStore((s) => s.selectedCanvas);
  const selectedFraming = useAppStore((s) => s.selectedFraming);
  const currentTemplate = useAppStore((s) => s.currentTemplate);
  const setOutputFdl = useAppStore((s) => s.setOutputFdl);
  const setError = useAppStore((s) => s.setError);
  const setLoading = useAppStore((s) => s.setLoading);
  const templateModified = useAppStore(
    (s) => s.templateModifiedSinceTransform,
  );
  const hasOutput = useAppStore((s) => s.transformResult !== null);
  const showReprocess = templateModified && hasOutput;

  const handleTransform = useCallback(async () => {
    if (!sourceSessionId) return;
    try {
      setLoading(true);
      setError(null);
      const result = await transform(
        sourceSessionId,
        selectedContext,
        selectedCanvas,
        selectedFraming,
        currentTemplate,
      );
      setOutputFdl(
        result.hierarchy,
        result.outputSessionId,
        result.outputGeometry,
        result.transformResult,
        result.outputContextLabel,
        result.outputCanvasId,
        result.outputFramingId,
      );

      // If source image is loaded, also transform it via Python OIIO bridge
      const { sourceImageId, setOutputImage } = useAppStore.getState();
      if (sourceImageId) {
        try {
          const imgResult = await transformImage(
            sourceImageId,
            sourceSessionId,
            selectedContext,
            selectedCanvas,
            selectedFraming,
            currentTemplate,
          );
          setOutputImage(imgResult.id, imgResult.url);
        } catch (imgErr) {
          // Non-fatal — FDL transform still succeeded
          console.error("Image transform failed:", imgErr);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Transform failed");
    } finally {
      setLoading(false);
    }
  }, [
    sourceSessionId,
    selectedContext,
    selectedCanvas,
    selectedFraming,
    currentTemplate,
    setOutputFdl,
    setError,
    setLoading,
  ]);

  return (
    <button
      onClick={handleTransform}
      disabled={!ready}
      className={`w-full h-10 rounded-md font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors ${
        showReprocess
          ? "bg-orange-600 text-white hover:bg-orange-500"
          : "bg-primary text-primary-foreground hover:bg-primary/90"
      }`}
    >
      {showReprocess ? "Reprocess & Transform" : "Transform"}
    </button>
  );
}

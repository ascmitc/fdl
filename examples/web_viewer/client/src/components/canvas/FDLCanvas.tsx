import { useRef, useEffect, useCallback, useState, useMemo } from "react";
import { useAppStore, getSelectedCanvas, getFramingDecisions, getOutputCanvas, getOutputFraming } from "@/store/app-store";
import { render, type RenderOptions, type Viewport } from "./canvas-renderer";
import { useCanvasInteraction } from "./use-canvas-interaction";
import { buildHudData } from "./build-hud-data";
import type { GeometryData, CanvasData, FramingDecisionData } from "@/api/types";

interface FDLCanvasProps {
  geometry: GeometryData | null;
  isSource: boolean;
  externalViewport?: Viewport;
  onViewportChange?: (viewport: Viewport) => void;
}

function getFramingData(
  canvasData: CanvasData | null,
  framingId: string,
): FramingDecisionData | null {
  if (!canvasData) return null;
  return canvasData.framingDecisions.find((fd) => fd.id === framingId) ?? null;
}

export function FDLCanvas({
  geometry,
  isSource,
  externalViewport,
  onViewportChange,
}: FDLCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [image, setImage] = useState<HTMLImageElement | null>(null);

  const gridVisible = useAppStore((s) => s.gridVisible);
  const canvasVisible = useAppStore((s) => s.canvasVisible);
  const effectiveVisible = useAppStore((s) => s.effectiveVisible);
  const framingVisible = useAppStore((s) => s.framingVisible);
  const protectionVisible = useAppStore((s) => s.protectionVisible);
  const imageVisible = useAppStore((s) => s.imageVisible);
  const hudVisible = useAppStore((s) => s.hudVisible);
  const imageOpacity = useAppStore((s) => s.imageOpacity);
  const sourceImageUrl = useAppStore((s) => s.sourceImageUrl);
  const outputImageUrl = useAppStore((s) => s.outputImageUrl);
  const selectedFraming = useAppStore((s) => s.selectedFraming);
  const outputFdl = useAppStore((s) => s.outputFdl);
  const currentTemplate = useAppStore((s) => s.currentTemplate);
  const transformResult = useAppStore((s) => s.transformResult);

  // Get canvas/framing data for labels (works for both source and output)
  const sourceCanvasData = useAppStore(getSelectedCanvas);
  const sourceFramings = useAppStore(getFramingDecisions);
  const sourceFramingData =
    sourceFramings.find((f) => f.id === selectedFraming) ?? null;

  // For output, navigate using server-provided identifiers
  const outputCanvasData = useAppStore(getOutputCanvas);
  const outputFramingData = useAppStore(getOutputFraming);

  const canvasData = isSource ? sourceCanvasData : outputCanvasData;
  const framingData = isSource ? sourceFramingData : outputFramingData;

  // Build HUD data for output canvas
  const hudData = useMemo(() => {
    if (isSource || !hudVisible || !outputFdl) return undefined;
    return buildHudData(
      sourceCanvasData,
      sourceFramingData,
      outputCanvasData,
      outputFramingData,
      currentTemplate,
      transformResult,
    );
  }, [
    isSource, hudVisible, outputFdl, sourceCanvasData, sourceFramingData,
    outputCanvasData, outputFramingData, currentTemplate, transformResult,
  ]);

  const {
    viewport: internalViewport,
    fitInView,
    zoomIn,
    zoomOut,
    resetZoom,
  } = useCanvasInteraction(canvasRef, geometry?.canvasRect ?? null);

  const viewport = externalViewport ?? internalViewport;

  // Sync external viewport
  useEffect(() => {
    if (onViewportChange) {
      onViewportChange(internalViewport);
    }
  }, [internalViewport, onViewportChange]);

  // Load image (source image for source canvas, output image for output canvas)
  const imageUrl = isSource ? sourceImageUrl : outputImageUrl;
  useEffect(() => {
    if (!imageUrl) {
      setImage(null);
      return;
    }
    const img = new Image();
    img.onload = () => setImage(img);
    img.src = imageUrl;
  }, [imageUrl]);

  // Render
  const renderFrame = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const options: RenderOptions = {
      geometry,
      showGrid: gridVisible,
      showCanvas: canvasVisible,
      showEffective: effectiveVisible,
      showFraming: framingVisible,
      showProtection: protectionVisible,
      showImage: imageVisible && !!image,
      showHud: hudVisible && !isSource,
      imageOpacity,
      isSource,
      image,
      canvasDimensions: canvasData?.dimensions ?? null,
      effectiveDimensions: canvasData?.effectiveDimensions ?? null,
      framingDimensions: framingData?.dimensions ?? null,
      protectionDimensions: framingData?.protectionDimensions ?? null,
      effectiveAnchorPoint: canvasData?.effectiveAnchorPoint ?? null,
      framingAnchorPoint: framingData?.anchorPoint ?? null,
      protectionAnchorPoint: framingData?.protectionAnchorPoint ?? null,
      hudData,
    };

    render(ctx, canvas.width, canvas.height, viewport, options);
  }, [
    geometry, viewport, gridVisible, canvasVisible, effectiveVisible,
    framingVisible, protectionVisible, imageVisible, hudVisible,
    imageOpacity, isSource, image, canvasData, framingData, hudData,
  ]);

  useEffect(() => {
    renderFrame();
  }, [renderFrame]);

  // Handle resize
  const needsFitRef = useRef(true);
  useEffect(() => {
    needsFitRef.current = true;
  }, [geometry]);

  useEffect(() => {
    const container = containerRef.current;
    const canvas = canvasRef.current;
    if (!container || !canvas) return;

    const observer = new ResizeObserver(() => {
      const dpr = window.devicePixelRatio || 1;
      const rect = container.getBoundingClientRect();
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      canvas.style.width = `${rect.width}px`;
      canvas.style.height = `${rect.height}px`;
      if (needsFitRef.current && rect.width > 0 && rect.height > 0) {
        needsFitRef.current = false;
        fitInView();
      }
      renderFrame();
    });

    observer.observe(container);
    return () => observer.disconnect();
  }, [renderFrame, fitInView]);

  return (
    <div className="flex flex-col h-full">
      {/* Zoom controls */}
      <div className="flex items-center gap-1 px-2 py-1 border-b border-border bg-card flex-shrink-0">
        <button
          onClick={zoomOut}
          className="px-2 py-0.5 text-xs rounded hover:bg-secondary"
        >
          -
        </button>
        <span className="text-xs text-muted-foreground w-12 text-center">
          {Math.round(viewport.scale * 100)}%
        </span>
        <button
          onClick={zoomIn}
          className="px-2 py-0.5 text-xs rounded hover:bg-secondary"
        >
          +
        </button>
        <button
          onClick={fitInView}
          className="px-2 py-0.5 text-xs rounded hover:bg-secondary"
        >
          Fit
        </button>
        <button
          onClick={resetZoom}
          className="px-2 py-0.5 text-xs rounded hover:bg-secondary"
        >
          100%
        </button>
      </div>

      {/* Canvas */}
      <div ref={containerRef} className="flex-1 min-h-0 cursor-grab">
        <canvas ref={canvasRef} />
      </div>
    </div>
  );
}

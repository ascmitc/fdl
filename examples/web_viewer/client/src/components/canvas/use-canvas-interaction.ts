import { useCallback, useRef, useState, useEffect, type RefObject } from "react";
import type { Viewport } from "./canvas-renderer";
import type { Rect } from "@/api/types";

const MIN_SCALE = 0.05;
const MAX_SCALE = 10;
const ZOOM_FACTOR = 1.15;

export function useCanvasInteraction(
  canvasRef: RefObject<HTMLCanvasElement | null>,
  bounds: Rect | null,
) {
  const [viewport, setViewport] = useState<Viewport>({
    offsetX: 50,
    offsetY: 50,
    scale: 0.15,
  });
  const dragging = useRef(false);
  const lastMouse = useRef({ x: 0, y: 0 });

  const fitInView = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || !bounds) return;
    const dpr = window.devicePixelRatio || 1;
    const cw = canvas.width / dpr;
    const ch = canvas.height / dpr;
    const padding = 50;
    const availW = cw - 2 * padding;
    const availH = ch - 2 * padding;
    if (bounds.width <= 0 || bounds.height <= 0) return;
    const scaleX = availW / bounds.width;
    const scaleY = availH / bounds.height;
    const scale = Math.min(scaleX, scaleY);
    const offsetX = (cw - bounds.width * scale) / 2 - bounds.x * scale;
    const offsetY = (ch - bounds.height * scale) / 2 - bounds.y * scale;
    setViewport({ scale, offsetX, offsetY });
  }, [canvasRef, bounds]);

  const resetZoom = useCallback(() => {
    if (!bounds) return;
    setViewport({
      scale: 1,
      offsetX: -bounds.x + 50,
      offsetY: -bounds.y + 50,
    });
  }, [bounds]);

  const zoomIn = useCallback(() => {
    setViewport((v) => ({
      ...v,
      scale: Math.min(MAX_SCALE, v.scale * ZOOM_FACTOR),
    }));
  }, []);

  const zoomOut = useCallback(() => {
    setViewport((v) => ({
      ...v,
      scale: Math.max(MIN_SCALE, v.scale / ZOOM_FACTOR),
    }));
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const handleWheel = (e: WheelEvent) => {
      e.preventDefault();
      const rect = canvas.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      setViewport((v) => {
        const factor = e.deltaY < 0 ? ZOOM_FACTOR : 1 / ZOOM_FACTOR;
        const newScale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, v.scale * factor));
        const newOffsetX = mouseX - (mouseX - v.offsetX) * (newScale / v.scale);
        const newOffsetY = mouseY - (mouseY - v.offsetY) * (newScale / v.scale);
        return { scale: newScale, offsetX: newOffsetX, offsetY: newOffsetY };
      });
    };

    const handleMouseDown = (e: MouseEvent) => {
      if (e.button === 0 || e.button === 1) {
        dragging.current = true;
        lastMouse.current = { x: e.clientX, y: e.clientY };
        canvas.style.cursor = "grabbing";
      }
    };

    const handleMouseMove = (e: MouseEvent) => {
      if (!dragging.current) return;
      const dx = e.clientX - lastMouse.current.x;
      const dy = e.clientY - lastMouse.current.y;
      lastMouse.current = { x: e.clientX, y: e.clientY };
      setViewport((v) => ({
        ...v,
        offsetX: v.offsetX + dx,
        offsetY: v.offsetY + dy,
      }));
    };

    const handleMouseUp = () => {
      dragging.current = false;
      canvas.style.cursor = "grab";
    };

    const handleDblClick = () => {
      fitInView();
    };

    canvas.addEventListener("wheel", handleWheel, { passive: false });
    canvas.addEventListener("mousedown", handleMouseDown);
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    canvas.addEventListener("dblclick", handleDblClick);

    return () => {
      canvas.removeEventListener("wheel", handleWheel);
      canvas.removeEventListener("mousedown", handleMouseDown);
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
      canvas.removeEventListener("dblclick", handleDblClick);
    };
  }, [canvasRef, fitInView]);

  // Auto-fit when bounds change
  useEffect(() => {
    if (bounds) fitInView();
  }, [bounds, fitInView]);

  return { viewport, fitInView, resetZoom, zoomIn, zoomOut, setViewport };
}

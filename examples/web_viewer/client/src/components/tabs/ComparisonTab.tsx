import { useState, useCallback } from "react";
import { useAppStore } from "@/store/app-store";
import { FDLCanvas } from "@/components/canvas/FDLCanvas";
import { VisibilityToolbar } from "@/components/canvas/VisibilityToolbar";
import type { Viewport } from "@/components/canvas/canvas-renderer";

export function ComparisonTab() {
  const sourceGeometry = useAppStore((s) => s.sourceGeometry);
  const outputGeometry = useAppStore((s) => s.outputGeometry);
  const outputFdl = useAppStore((s) => s.outputFdl);

  const [sharedViewport, setSharedViewport] = useState<Viewport | null>(null);

  const handleViewportChange = useCallback((vp: Viewport) => {
    setSharedViewport(vp);
  }, []);

  if (!outputFdl) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        Run a transformation to compare source and output side by side.
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <VisibilityToolbar />
      <div className="flex flex-1 min-h-0">
        {/* Source panel */}
        <div className="flex-1 flex flex-col border-r border-border min-w-0">
          <div className="text-xs text-center py-1 bg-secondary/30 text-muted-foreground font-medium">
            Source
          </div>
          <div className="flex-1 min-h-0">
            <FDLCanvas
              geometry={sourceGeometry}
              isSource={true}
              onViewportChange={handleViewportChange}
            />
          </div>
        </div>

        {/* Output panel */}
        <div className="flex-1 flex flex-col min-w-0">
          <div className="text-xs text-center py-1 bg-secondary/30 text-muted-foreground font-medium">
            Output
          </div>
          <div className="flex-1 min-h-0">
            <FDLCanvas
              geometry={outputGeometry}
              isSource={false}
              externalViewport={sharedViewport ?? undefined}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

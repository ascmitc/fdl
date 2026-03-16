import { useAppStore } from "@/store/app-store";
import { FDLCanvas } from "@/components/canvas/FDLCanvas";
import { VisibilityToolbar } from "@/components/canvas/VisibilityToolbar";

export function OutputTab() {
  const outputGeometry = useAppStore((s) => s.outputGeometry);
  const outputFdl = useAppStore((s) => s.outputFdl);

  if (!outputFdl) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        No transformation result yet. Load a source FDL, configure a template, and click Transform.
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <VisibilityToolbar showHud={true} />
      <FDLCanvas geometry={outputGeometry} isSource={false} />
    </div>
  );
}

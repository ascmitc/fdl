import { useAppStore } from "@/store/app-store";
import { FDLCanvas } from "@/components/canvas/FDLCanvas";
import { VisibilityToolbar } from "@/components/canvas/VisibilityToolbar";

export function SourceTab() {
  const sourceGeometry = useAppStore((s) => s.sourceGeometry);
  const sourceFdl = useAppStore((s) => s.sourceFdl);

  if (!sourceFdl) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        Load a source FDL to begin
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <VisibilityToolbar />
      <FDLCanvas geometry={sourceGeometry} isSource={true} />
    </div>
  );
}

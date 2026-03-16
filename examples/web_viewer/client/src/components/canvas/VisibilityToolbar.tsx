import { useAppStore } from "@/store/app-store";

interface ToggleProps {
  label: string;
  active: boolean;
  color?: string;
  onToggle: () => void;
}

function Toggle({ label, active, color, onToggle }: ToggleProps) {
  return (
    <button
      onClick={onToggle}
      className={`px-2 py-0.5 text-xs rounded transition-colors ${
        active
          ? "bg-secondary text-foreground"
          : "text-muted-foreground hover:bg-secondary/50"
      }`}
      title={`Toggle ${label}`}
    >
      {color && (
        <span
          className="inline-block w-2 h-2 rounded-full mr-1"
          style={{ backgroundColor: active ? color : "#666" }}
        />
      )}
      {label}
    </button>
  );
}

export function VisibilityToolbar({ showHud = false }: { showHud?: boolean }) {
  const gridVisible = useAppStore((s) => s.gridVisible);
  const canvasVisible = useAppStore((s) => s.canvasVisible);
  const effectiveVisible = useAppStore((s) => s.effectiveVisible);
  const framingVisible = useAppStore((s) => s.framingVisible);
  const protectionVisible = useAppStore((s) => s.protectionVisible);
  const imageVisible = useAppStore((s) => s.imageVisible);
  const hudVisible = useAppStore((s) => s.hudVisible);
  const sourceImageUrl = useAppStore((s) => s.sourceImageUrl);
  const toggleGrid = useAppStore((s) => s.toggleGrid);
  const setLayerVisibility = useAppStore((s) => s.setLayerVisibility);

  return (
    <div className="flex items-center gap-1 px-2 py-1 border-b border-border bg-card flex-shrink-0 flex-wrap">
      <Toggle label="Grid" active={gridVisible} onToggle={toggleGrid} />
      <Toggle
        label="Canvas"
        active={canvasVisible}
        color="#808080"
        onToggle={() => setLayerVisibility("canvas", !canvasVisible)}
      />
      <Toggle
        label="Effective"
        active={effectiveVisible}
        color="#0066CC"
        onToggle={() => setLayerVisibility("effective", !effectiveVisible)}
      />
      <Toggle
        label="Protection"
        active={protectionVisible}
        color="#FF9900"
        onToggle={() => setLayerVisibility("protection", !protectionVisible)}
      />
      <Toggle
        label="Framing"
        active={framingVisible}
        color="#00CC66"
        onToggle={() => setLayerVisibility("framing", !framingVisible)}
      />
      {sourceImageUrl && (
        <Toggle
          label="Image"
          active={imageVisible}
          onToggle={() => setLayerVisibility("image", !imageVisible)}
        />
      )}
      {showHud && (
        <Toggle
          label="HUD"
          active={hudVisible}
          onToggle={() => setLayerVisibility("hud", !hudVisible)}
        />
      )}
    </div>
  );
}

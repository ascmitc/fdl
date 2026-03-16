import { useEffect } from "react";
import {
  useAppStore,
  getContexts,
  getCanvases,
  getFramingDecisions,
} from "@/store/app-store";
import { getGeometry } from "@/api/client";

function CascadingSelect({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: { value: string; label: string }[];
  onChange: (value: string) => void;
}) {
  return (
    <div className="space-y-1">
      <label className="text-xs text-muted-foreground">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={options.length === 0}
        className="w-full h-8 rounded-md border border-input bg-background px-2 text-sm disabled:opacity-50"
      >
        {options.length === 0 && <option value="">No options</option>}
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </div>
  );
}

export function SourceSelector() {
  const sourceFdl = useAppStore((s) => s.sourceFdl);
  const sourceSessionId = useAppStore((s) => s.sourceSessionId);
  const selectedContext = useAppStore((s) => s.selectedContext);
  const selectedCanvas = useAppStore((s) => s.selectedCanvas);
  const selectedFraming = useAppStore((s) => s.selectedFraming);
  const setSelectedContext = useAppStore((s) => s.setSelectedContext);
  const setSelectedCanvas = useAppStore((s) => s.setSelectedCanvas);
  const setSelectedFraming = useAppStore((s) => s.setSelectedFraming);
  const setSourceGeometry = useAppStore((s) => s.setSourceGeometry);

  const contexts = useAppStore(getContexts);
  const canvases = useAppStore(getCanvases);
  const framingDecisions = useAppStore(getFramingDecisions);

  // Fetch geometry when selection changes
  useEffect(() => {
    if (!sourceSessionId || !selectedContext || !selectedCanvas || !selectedFraming)
      return;
    getGeometry(sourceSessionId, selectedContext, selectedCanvas, selectedFraming)
      .then(setSourceGeometry)
      .catch(console.error);
  }, [sourceSessionId, selectedContext, selectedCanvas, selectedFraming, setSourceGeometry]);

  if (!sourceFdl) return null;

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-foreground">Source Selection</h3>
      <CascadingSelect
        label="Context"
        value={selectedContext}
        options={contexts.map((c) => ({ value: c.label, label: c.label }))}
        onChange={setSelectedContext}
      />
      <CascadingSelect
        label="Canvas"
        value={selectedCanvas}
        options={canvases.map((c) => ({
          value: c.id,
          label: `${c.label || c.id} (${c.dimensions.width}x${c.dimensions.height})`,
        }))}
        onChange={setSelectedCanvas}
      />
      <CascadingSelect
        label="Framing Decision"
        value={selectedFraming}
        options={framingDecisions.map((f) => ({
          value: f.id,
          label: `${f.label || f.id} (${f.dimensions.width}x${f.dimensions.height})`,
        }))}
        onChange={setSelectedFraming}
      />
    </div>
  );
}

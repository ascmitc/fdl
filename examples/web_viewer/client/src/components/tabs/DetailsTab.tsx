import { useState, useCallback } from "react";
import { useAppStore, getSelectedCanvas, getFramingDecisions, getOutputContext, getOutputCanvas, getOutputFraming } from "@/store/app-store";
import { getFdlJson, getExportUrl, getImageDownloadUrl } from "@/api/client";

function PropertyRow({
  label,
  source,
  output,
}: {
  label: string;
  source: string;
  output: string;
}) {
  const changed = source !== output;
  return (
    <tr className={changed ? "bg-primary/5" : ""}>
      <td className="px-3 py-1.5 text-xs font-medium text-muted-foreground">
        {label}
      </td>
      <td className="px-3 py-1.5 text-xs text-foreground">{source}</td>
      <td
        className={`px-3 py-1.5 text-xs ${changed ? "text-primary font-medium" : "text-foreground"}`}
      >
        {output}
      </td>
    </tr>
  );
}

function fmt(v: number | null | undefined): string {
  if (v == null) return "-";
  return String(Math.round(v));
}

function fmtDims(
  d: { width: number; height: number } | null | undefined,
): string {
  if (!d) return "-";
  return `${Math.round(d.width)} x ${Math.round(d.height)}`;
}

function fmtPoint(p: { x: number; y: number } | null | undefined): string {
  if (!p) return "-";
  return `(${Math.round(p.x)}, ${Math.round(p.y)})`;
}

export function DetailsTab() {
  const outputFdl = useAppStore((s) => s.outputFdl);
  const outputSessionId = useAppStore((s) => s.outputSessionId);
  const outputImageId = useAppStore((s) => s.outputImageId);
  const sourceGeometry = useAppStore((s) => s.sourceGeometry);
  const outputGeometry = useAppStore((s) => s.outputGeometry);
  const transformResult = useAppStore((s) => s.transformResult);
  const selectedContext = useAppStore((s) => s.selectedContext);
  const selectedCanvas = useAppStore((s) => s.selectedCanvas);
  const selectedFraming = useAppStore((s) => s.selectedFraming);

  const sourceCanvas = useAppStore(getSelectedCanvas);
  const sourceFramings = useAppStore(getFramingDecisions);
  const sourceFraming = sourceFramings.find((f) => f.id === selectedFraming);

  // Output canvas/framing — navigate using server-provided identifiers
  const outputCtx = useAppStore(getOutputContext);
  const outputCanvas = useAppStore(getOutputCanvas);
  const outputFraming = useAppStore(getOutputFraming);

  const [jsonPreview, setJsonPreview] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const loadJson = useCallback(async () => {
    if (!outputSessionId) return;
    try {
      const json = await getFdlJson(outputSessionId);
      setJsonPreview(json);
    } catch (err) {
      console.error(err);
    }
  }, [outputSessionId]);

  const copyJson = useCallback(() => {
    if (jsonPreview) {
      navigator.clipboard.writeText(jsonPreview);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }, [jsonPreview]);

  if (!outputFdl) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        Run a transformation to see details.
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full overflow-auto p-4 gap-4">
      {/* Comparison Grid */}
      <div>
        <h3 className="text-sm font-semibold text-foreground mb-2">
          Property Comparison
        </h3>
        <div className="border border-border rounded-md overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="bg-secondary/30">
                <th className="px-3 py-2 text-xs font-medium text-muted-foreground text-left w-1/3">
                  Property
                </th>
                <th className="px-3 py-2 text-xs font-medium text-muted-foreground text-left w-1/3">
                  Source
                </th>
                <th className="px-3 py-2 text-xs font-medium text-muted-foreground text-left w-1/3">
                  Output
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              <PropertyRow
                label="Context"
                source={selectedContext || "-"}
                output={outputCtx?.label || "-"}
              />
              <PropertyRow
                label="Canvas ID"
                source={selectedCanvas || "-"}
                output={outputCanvas?.id || "-"}
              />
              <PropertyRow
                label="Framing ID"
                source={selectedFraming || "-"}
                output={outputFraming?.id || "-"}
              />
              <PropertyRow
                label="Canvas Dimensions"
                source={fmtDims(sourceCanvas?.dimensions)}
                output={fmtDims(outputCanvas?.dimensions)}
              />
              <PropertyRow
                label="Canvas Rect"
                source={
                  sourceGeometry?.canvasRect
                    ? `${fmtDims(sourceGeometry.canvasRect)} at ${fmtPoint(sourceGeometry.canvasRect)}`
                    : "-"
                }
                output={
                  outputGeometry?.canvasRect
                    ? `${fmtDims(outputGeometry.canvasRect)} at ${fmtPoint(outputGeometry.canvasRect)}`
                    : "-"
                }
              />
              <PropertyRow
                label="Effective Dimensions"
                source={fmtDims(sourceCanvas?.effectiveDimensions)}
                output={fmtDims(outputCanvas?.effectiveDimensions)}
              />
              <PropertyRow
                label="Effective Anchor"
                source={fmtPoint(sourceCanvas?.effectiveAnchorPoint)}
                output={fmtPoint(outputCanvas?.effectiveAnchorPoint)}
              />
              <PropertyRow
                label="Framing Dimensions"
                source={fmtDims(sourceFraming?.dimensions)}
                output={fmtDims(outputFraming?.dimensions)}
              />
              <PropertyRow
                label="Framing Anchor"
                source={fmtPoint(sourceFraming?.anchorPoint)}
                output={fmtPoint(outputFraming?.anchorPoint)}
              />
              <PropertyRow
                label="Protection Dimensions"
                source={fmtDims(sourceFraming?.protectionDimensions)}
                output={fmtDims(outputFraming?.protectionDimensions)}
              />
              <PropertyRow
                label="Protection Anchor"
                source={fmtPoint(sourceFraming?.protectionAnchorPoint)}
                output={fmtPoint(outputFraming?.protectionAnchorPoint)}
              />
              <PropertyRow
                label="Anamorphic Squeeze"
                source={fmt(sourceCanvas?.anamorphicSqueeze)}
                output={fmt(outputCanvas?.anamorphicSqueeze)}
              />
            </tbody>
          </table>
        </div>
      </div>

      {/* Transform Result */}
      {transformResult && (
        <div>
          <h3 className="text-sm font-semibold text-foreground mb-2">
            Transform Result
          </h3>
          <div className="text-xs text-muted-foreground space-y-1 p-2 bg-secondary/30 rounded-md">
            {outputFdl?.canvasTemplates[0] && (
              <p>
                Template:{" "}
                {outputFdl.canvasTemplates[0].label ||
                  outputFdl.canvasTemplates[0].id}
              </p>
            )}
            <p>Scale Factor: {transformResult.scaleFactor?.toFixed(6) ?? "-"}</p>
            <p>
              Content Translation:{" "}
              {transformResult.contentTranslation
                ? `(${transformResult.contentTranslation.x.toFixed(2)}, ${transformResult.contentTranslation.y.toFixed(2)})`
                : "-"}
            </p>
            <p>
              Scaled Bounding Box:{" "}
              {transformResult.scaledBoundingBox
                ? `${Math.round(transformResult.scaledBoundingBox.width)} x ${Math.round(transformResult.scaledBoundingBox.height)}`
                : "-"}
            </p>
          </div>
        </div>
      )}

      {/* Export Actions */}
      <div>
        <h3 className="text-sm font-semibold text-foreground mb-2">Export</h3>
        <div className="flex gap-2">
          {outputSessionId && (
            <a
              href={getExportUrl(outputSessionId)}
              download
              className="px-3 py-1.5 text-xs rounded-md bg-primary text-primary-foreground hover:bg-primary/90"
            >
              Download FDL
            </a>
          )}
          <button
            onClick={loadJson}
            className="px-3 py-1.5 text-xs rounded-md bg-secondary text-foreground hover:bg-secondary/80"
          >
            Preview JSON
          </button>
          {outputImageId && (
            <a
              href={getImageDownloadUrl(outputImageId)}
              download
              className="px-3 py-1.5 text-xs rounded-md bg-secondary text-foreground hover:bg-secondary/80"
            >
              Export Image
            </a>
          )}
        </div>
      </div>

      {/* JSON Preview */}
      {jsonPreview && (
        <div>
          <div className="flex items-center justify-between mb-1">
            <h3 className="text-sm font-semibold text-foreground">
              JSON Preview
            </h3>
            <button
              onClick={copyJson}
              className="px-2 py-1 text-xs rounded-md bg-secondary text-foreground hover:bg-secondary/80"
            >
              {copied ? "Copied!" : "Copy"}
            </button>
          </div>
          <pre className="text-xs text-muted-foreground bg-secondary/30 rounded-md p-3 overflow-auto max-h-96 font-mono whitespace-pre">
            {jsonPreview}
          </pre>
        </div>
      )}
    </div>
  );
}

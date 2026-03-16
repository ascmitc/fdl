import { useState, useEffect } from "react";
import { useAppStore } from "@/store/app-store";
import { getTemplateOptions } from "@/api/client";
import type { TemplateOptions, SelectOption } from "@/api/types";

function SelectField({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: SelectOption[];
  onChange: (value: string) => void;
}) {
  return (
    <div className="space-y-1">
      <label className="text-xs text-muted-foreground">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full h-8 rounded-md border border-input bg-background px-2 text-sm"
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </div>
  );
}

function NumberField({
  label,
  value,
  onChange,
  min = 0,
  step = 1,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  step?: number;
}) {
  return (
    <div className="space-y-1">
      <label className="text-xs text-muted-foreground">{label}</label>
      <input
        type="number"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        min={min}
        step={step}
        className="w-full h-8 rounded-md border border-input bg-background px-2 text-sm"
      />
    </div>
  );
}

const DEFAULT_OPTIONS: TemplateOptions = {
  fitSource: [],
  fitMethod: [],
  alignmentHorizontal: [],
  alignmentVertical: [],
  preserve: [],
  roundEven: [],
  roundMode: [],
};

export function TemplateEditor() {
  const template = useAppStore((s) => s.currentTemplate);
  const updateTemplate = useAppStore((s) => s.updateTemplate);
  const presetMode = useAppStore((s) => s.presetMode);
  const [options, setOptions] = useState<TemplateOptions>(DEFAULT_OPTIONS);
  const [maxDimsEnabled, setMaxDimsEnabled] = useState(
    template.maximumDimensions !== null,
  );

  useEffect(() => {
    getTemplateOptions().then(setOptions).catch(console.error);
  }, []);

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-foreground">
        Template {presetMode ? "(Preset)" : "(Custom)"}
      </h3>

      {/* Target Dimensions */}
      <div className="space-y-2 p-2 rounded-md bg-secondary/30">
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Target Dimensions
        </p>
        <div className="grid grid-cols-2 gap-2">
          <NumberField
            label="Width"
            value={template.targetWidth}
            onChange={(v) => updateTemplate({ targetWidth: v })}
            min={1}
          />
          <NumberField
            label="Height"
            value={template.targetHeight}
            onChange={(v) => updateTemplate({ targetHeight: v })}
            min={1}
          />
        </div>
        <NumberField
          label="Anamorphic Squeeze"
          value={template.targetAnamorphicSqueeze}
          onChange={(v) => updateTemplate({ targetAnamorphicSqueeze: v })}
          min={0.1}
          step={0.01}
        />
      </div>

      {/* Fit */}
      <div className="space-y-2 p-2 rounded-md bg-secondary/30">
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Fit
        </p>
        <SelectField
          label="Fit Source"
          value={template.fitSource}
          options={options.fitSource}
          onChange={(v) => updateTemplate({ fitSource: v })}
        />
        <SelectField
          label="Fit Method"
          value={template.fitMethod}
          options={options.fitMethod}
          onChange={(v) => updateTemplate({ fitMethod: v })}
        />
      </div>

      {/* Alignment */}
      <div className="space-y-2 p-2 rounded-md bg-secondary/30">
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Alignment
        </p>
        <div className="grid grid-cols-2 gap-2">
          <SelectField
            label="Horizontal"
            value={template.alignmentMethodHorizontal}
            options={options.alignmentHorizontal}
            onChange={(v) =>
              updateTemplate({ alignmentMethodHorizontal: v })
            }
          />
          <SelectField
            label="Vertical"
            value={template.alignmentMethodVertical}
            options={options.alignmentVertical}
            onChange={(v) =>
              updateTemplate({ alignmentMethodVertical: v })
            }
          />
        </div>
      </div>

      {/* Preserve From Source */}
      <div className="space-y-2 p-2 rounded-md bg-secondary/30">
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Preserve From Source
        </p>
        <SelectField
          label="Preserve"
          value={template.preserveFromSourceCanvas ?? ""}
          options={options.preserve}
          onChange={(v) =>
            updateTemplate({
              preserveFromSourceCanvas: v || null,
            })
          }
        />
      </div>

      {/* Maximum Dimensions */}
      <div className="space-y-2 p-2 rounded-md bg-secondary/30">
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Maximum Dimensions
        </p>
        <label className="flex items-center gap-2 text-xs text-muted-foreground">
          <input
            type="checkbox"
            checked={maxDimsEnabled}
            onChange={(e) => {
              setMaxDimsEnabled(e.target.checked);
              if (!e.target.checked) {
                updateTemplate({ maximumDimensions: null, padToMaximum: false });
              } else {
                updateTemplate({
                  maximumDimensions: {
                    width: template.targetWidth,
                    height: template.targetHeight,
                  },
                });
              }
            }}
            className="rounded"
          />
          Enable maximum dimensions
        </label>
        {maxDimsEnabled && (
          <>
            <div className="grid grid-cols-2 gap-2">
              <NumberField
                label="Max Width"
                value={template.maximumDimensions?.width ?? template.targetWidth}
                onChange={(v) =>
                  updateTemplate({
                    maximumDimensions: {
                      width: v,
                      height:
                        template.maximumDimensions?.height ?? template.targetHeight,
                    },
                  })
                }
                min={1}
              />
              <NumberField
                label="Max Height"
                value={
                  template.maximumDimensions?.height ?? template.targetHeight
                }
                onChange={(v) =>
                  updateTemplate({
                    maximumDimensions: {
                      width:
                        template.maximumDimensions?.width ?? template.targetWidth,
                      height: v,
                    },
                  })
                }
                min={1}
              />
            </div>
            <label className="flex items-center gap-2 text-xs text-muted-foreground">
              <input
                type="checkbox"
                checked={template.padToMaximum}
                onChange={(e) =>
                  updateTemplate({ padToMaximum: e.target.checked })
                }
                className="rounded"
              />
              Pad to maximum
            </label>
          </>
        )}
      </div>

      {/* Rounding */}
      <div className="space-y-2 p-2 rounded-md bg-secondary/30">
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Rounding
        </p>
        <div className="grid grid-cols-2 gap-2">
          <SelectField
            label="Even"
            value={template.roundEven}
            options={options.roundEven}
            onChange={(v) => updateTemplate({ roundEven: v })}
          />
          <SelectField
            label="Mode"
            value={template.roundMode}
            options={options.roundMode}
            onChange={(v) => updateTemplate({ roundMode: v })}
          />
        </div>
      </div>
    </div>
  );
}

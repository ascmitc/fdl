import { useAppStore } from "@/store/app-store";
import { SourceTab } from "./SourceTab";
import { OutputTab } from "./OutputTab";
import { ComparisonTab } from "./ComparisonTab";
import { DetailsTab } from "./DetailsTab";

const TABS = ["Source", "Output", "Comparison", "Details"];

export function TabContainer() {
  const activeTab = useAppStore((s) => s.activeTab);
  const setActiveTab = useAppStore((s) => s.setActiveTab);
  const outputFdl = useAppStore((s) => s.outputFdl);

  return (
    <div className="flex flex-col h-full">
      {/* Tab headers */}
      <div className="flex border-b border-border bg-card flex-shrink-0">
        {TABS.map((tab, i) => (
          <button
            key={tab}
            onClick={() => setActiveTab(i)}
            className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 ${
              activeTab === i
                ? "border-primary text-foreground"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {tab}
            {i > 0 && !outputFdl && (
              <span className="ml-1 text-xs text-muted-foreground/50">
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="flex-1 min-h-0">
        {activeTab === 0 && <SourceTab />}
        {activeTab === 1 && <OutputTab />}
        {activeTab === 2 && <ComparisonTab />}
        {activeTab === 3 && <DetailsTab />}
      </div>
    </div>
  );
}

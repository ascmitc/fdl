import { useAppStore } from "@/store/app-store";

export function StatusBar() {
  const statusMessage = useAppStore((s) => s.statusMessage);
  const error = useAppStore((s) => s.error);
  const loading = useAppStore((s) => s.loading);

  return (
    <div className="h-7 flex items-center px-3 border-t border-border bg-card text-xs text-muted-foreground flex-shrink-0">
      {error ? (
        <span className="text-destructive">{error}</span>
      ) : loading ? (
        <span className="animate-pulse">Processing...</span>
      ) : (
        <span>{statusMessage}</span>
      )}
    </div>
  );
}

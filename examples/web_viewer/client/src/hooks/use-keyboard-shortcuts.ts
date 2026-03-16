import { useEffect } from "react";
import { useAppStore } from "@/store/app-store";

export function useKeyboardShortcuts() {
  const setActiveTab = useAppStore((s) => s.setActiveTab);
  const toggleGrid = useAppStore((s) => s.toggleGrid);
  const toggleSidebar = useAppStore((s) => s.toggleSidebar);

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      const ctrl = e.ctrlKey || e.metaKey;

      // Ctrl+1-4: Switch tabs
      if (ctrl && e.key >= "1" && e.key <= "4") {
        e.preventDefault();
        setActiveTab(parseInt(e.key) - 1);
        return;
      }

      // Ctrl+G: Toggle grid
      if (ctrl && e.key === "g") {
        e.preventDefault();
        toggleGrid();
        return;
      }

      // Ctrl+Alt+S: Toggle sidebar
      if (ctrl && e.altKey && e.key === "s") {
        e.preventDefault();
        toggleSidebar();
        return;
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [setActiveTab, toggleGrid, toggleSidebar]);
}

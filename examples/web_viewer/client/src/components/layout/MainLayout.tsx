import { useRef, useState, useCallback } from "react";
import { useAppStore } from "@/store/app-store";
import { Sidebar } from "./Sidebar";
import { StatusBar } from "./StatusBar";
import { TabContainer } from "@/components/tabs/TabContainer";

export function MainLayout() {
  const sidebarCollapsed = useAppStore((s) => s.sidebarCollapsed);
  const [sidebarWidth, setSidebarWidth] = useState(400);
  const dragging = useRef(false);

  const handleMouseDown = useCallback(() => {
    dragging.current = true;
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";

    const handleMouseMove = (e: MouseEvent) => {
      if (!dragging.current) return;
      const newWidth = Math.max(280, Math.min(600, e.clientX));
      setSidebarWidth(newWidth);
    };

    const handleMouseUp = () => {
      dragging.current = false;
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);
  }, []);

  return (
    <div className="flex flex-col h-screen">
      <div className="flex flex-1 min-h-0">
        {!sidebarCollapsed && (
          <>
            <div
              className="flex-shrink-0 border-r border-border bg-card overflow-y-auto"
              style={{ width: sidebarWidth }}
            >
              <Sidebar />
            </div>
            <div
              className="w-1 cursor-col-resize hover:bg-primary/30 active:bg-primary/50 flex-shrink-0"
              onMouseDown={handleMouseDown}
            />
          </>
        )}
        <div className="flex-1 min-w-0">
          <TabContainer />
        </div>
      </div>
      <StatusBar />
    </div>
  );
}

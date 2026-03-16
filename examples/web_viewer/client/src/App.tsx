import { MainLayout } from "@/components/layout/MainLayout";
import { useKeyboardShortcuts } from "@/hooks/use-keyboard-shortcuts";

export default function App() {
  useKeyboardShortcuts();

  return <MainLayout />;
}

import { FileLoader } from "@/components/sidebar/FileLoader";
import { SourceSelector } from "@/components/sidebar/SourceSelector";
import { TemplateEditor } from "@/components/sidebar/TemplateEditor";
import { ImageLoader } from "@/components/sidebar/ImageLoader";
import { TransformButton } from "@/components/sidebar/TransformButton";

export function Sidebar() {
  return (
    <div className="flex flex-col gap-3 p-3 h-full">
      <FileLoader />
      <SourceSelector />
      <TemplateEditor />
      <ImageLoader />
      <div className="mt-auto pt-3">
        <TransformButton />
      </div>
    </div>
  );
}

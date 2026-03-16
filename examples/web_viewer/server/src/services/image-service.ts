import sharp from "sharp";
import { execFile } from "child_process";
import path from "path";
import os from "os";
import fs from "fs";
import { fileURLToPath } from "url";
import { v4 as uuidv4 } from "uuid";
import type { ImageUploadResponse, TemplateParams } from "../types/api.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

interface ImageSession {
  filePath: string;
  originalName: string;
  width: number;
  height: number;
  mimeType: string;
  createdAt: number;
}

const imageStore = new Map<string, ImageSession>();
const uploadDir = path.join(os.tmpdir(), "fdl-viewer-images");

// Ensure upload directory exists
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

// Cleanup expired images every 10 minutes
setInterval(() => {
  const now = Date.now();
  const TTL = 60 * 60 * 1000; // 1 hour
  for (const [id, session] of imageStore) {
    if (now - session.createdAt > TTL) {
      try {
        fs.unlinkSync(session.filePath);
      } catch {
        // ignore
      }
      imageStore.delete(id);
    }
  }
}, 10 * 60 * 1000);

// Resolve Python path: PYTHON_PATH env → workspace .venv → python3 fallback
function resolvePythonPath(): string {
  if (process.env.PYTHON_PATH) return process.env.PYTHON_PATH;
  // Walk up from __dirname (server/src/services/) to repo root
  const repoRoot = path.resolve(__dirname, "..", "..", "..", "..", "..", "..");
  const venvPython = path.join(repoRoot, ".venv", "bin", "python");
  if (fs.existsSync(venvPython)) return venvPython;
  return "python3";
}

const PYTHON_PATH = resolvePythonPath();
const BRIDGE_SCRIPT = path.resolve(
  __dirname,
  "..",
  "..",
  "scripts",
  "transform_image.py",
);

// Check if Python bridge is available at startup
let pythonAvailable = false;
try {
  const testProc = execFile(
    PYTHON_PATH,
    ["-c", "import fdl_imaging; import OpenImageIO"],
    { timeout: 10000 },
    (err) => {
      pythonAvailable = !err;
      if (pythonAvailable) {
        console.log(`Image transform: Python bridge available (${PYTHON_PATH})`);
      } else {
        console.warn(
          "Image transform: fdl_imaging/OpenImageIO not available — image transforms will fail.",
          err?.message,
        );
      }
    },
  );
} catch {
  console.warn("Image transform: Python not found — image transforms will fail.");
}

export async function storeImage(
  filePath: string,
  originalName: string,
): Promise<ImageUploadResponse> {
  const metadata = await sharp(filePath).metadata();
  if (!metadata.width || !metadata.height) {
    throw new Error("Could not read image dimensions");
  }

  // Convert to PNG for consistent browser serving
  const id = uuidv4();
  const pngPath = path.join(uploadDir, `${id}.png`);
  await sharp(filePath).png().toFile(pngPath);

  // Remove the original upload
  try {
    fs.unlinkSync(filePath);
  } catch {
    // ignore
  }

  imageStore.set(id, {
    filePath: pngPath,
    originalName,
    width: metadata.width,
    height: metadata.height,
    mimeType: "image/png",
    createdAt: Date.now(),
  });

  return {
    id,
    url: `/api/image/${id}`,
    width: metadata.width,
    height: metadata.height,
  };
}

export function getImage(id: string): string | null {
  const session = imageStore.get(id);
  return session ? session.filePath : null;
}

export function getImageMetadata(id: string): ImageSession | null {
  return imageStore.get(id) ?? null;
}

export async function transformImage(
  imageId: string,
  sourceFdlJson: string,
  contextLabel: string,
  canvasId: string,
  framingId: string,
  template: TemplateParams,
): Promise<ImageUploadResponse> {
  if (!pythonAvailable) {
    throw new Error(
      "Image transform requires Python with fdl_imaging and OpenImageIO. " +
        "Run 'python examples/web_viewer/run.py --setup-only' to install dependencies.",
    );
  }

  const source = imageStore.get(imageId);
  if (!source) {
    throw new Error(`Image not found: ${imageId}`);
  }

  const outputId = uuidv4();
  const outputPath = path.join(uploadDir, `${outputId}.png`);

  const bridgeInput = JSON.stringify({
    sourceFdlJson,
    contextLabel,
    canvasId,
    framingId,
    template,
    inputImagePath: source.filePath,
    outputImagePath: outputPath,
  });

  const result = await new Promise<{ width: number; height: number }>(
    (resolve, reject) => {
      const proc = execFile(
        PYTHON_PATH,
        [BRIDGE_SCRIPT],
        { timeout: 60000, maxBuffer: 10 * 1024 * 1024 },
        (err, stdout, stderr) => {
          if (err) {
            // Try to parse error from stdout first
            try {
              const parsed = JSON.parse(stdout);
              if (parsed.error) {
                reject(new Error(`Image transform failed: ${parsed.error}`));
                return;
              }
            } catch {
              // ignore parse error
            }
            reject(
              new Error(
                `Image transform failed: ${stderr || err.message}`,
              ),
            );
            return;
          }
          try {
            const parsed = JSON.parse(stdout);
            if (parsed.error) {
              reject(new Error(`Image transform failed: ${parsed.error}`));
            } else {
              resolve({ width: parsed.width, height: parsed.height });
            }
          } catch {
            reject(new Error(`Failed to parse transform output: ${stdout}`));
          }
        },
      );
      proc.stdin?.write(bridgeInput);
      proc.stdin?.end();
    },
  );

  imageStore.set(outputId, {
    filePath: outputPath,
    originalName: `transformed_${source.originalName}`,
    width: result.width,
    height: result.height,
    mimeType: "image/png",
    createdAt: Date.now(),
  });

  return {
    id: outputId,
    url: `/api/image/${outputId}`,
    width: result.width,
    height: result.height,
  };
}

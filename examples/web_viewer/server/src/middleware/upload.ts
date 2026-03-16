import multer from "multer";
import path from "path";
import os from "os";

const uploadDir = path.join(os.tmpdir(), "fdl-viewer-uploads");

export const fdlUpload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB
  fileFilter: (_req, file, cb) => {
    const ext = path.extname(file.originalname).toLowerCase();
    if (ext === ".fdl" || ext === ".json") {
      cb(null, true);
    } else {
      cb(new Error("Only .fdl and .json files are accepted"));
    }
  },
});

export const imageUpload = multer({
  dest: uploadDir,
  limits: { fileSize: 100 * 1024 * 1024 }, // 100MB for images
  fileFilter: (_req, file, cb) => {
    const allowed = [
      "image/png",
      "image/jpeg",
      "image/webp",
      "image/tiff",
    ];
    if (allowed.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error("Only PNG, JPEG, WebP, and TIFF images are accepted"));
    }
  },
});

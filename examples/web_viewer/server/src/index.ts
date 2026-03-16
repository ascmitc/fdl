import express from "express";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";
import fdlRoutes from "./routes/fdl.js";
import presetsRoutes from "./routes/presets.js";
import imageRoutes from "./routes/image.js";
import { errorHandler } from "./middleware/error-handler.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json({ limit: "10mb" }));
app.use(express.text({ limit: "10mb" }));

// API routes
app.use("/api/fdl", fdlRoutes);
app.use("/api/presets", presetsRoutes);
app.use("/api/image", imageRoutes);

// Serve static client build in production
const clientDist = path.resolve(__dirname, "../../client/dist");
app.use(express.static(clientDist));
app.get("*", (_req, res) => {
  res.sendFile(path.join(clientDist, "index.html"));
});

// Error handler
app.use(errorHandler);

app.listen(PORT, () => {
  console.log(`FDL Web Viewer server running on http://localhost:${PORT}`);
});

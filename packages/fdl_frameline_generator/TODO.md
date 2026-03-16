# Frameline Generator TODO

## Styling Improvements Needed

- [ ] Revisit the rendering approach for the framing dimension area
  - Currently the innermost (framing) layer is left transparent/black because the generator was designed for overlay compositing
  - For standalone test images, we may want to fill the framing area with its color (green) instead of leaving it transparent
  - Consider adding a CLI flag like `--fill-framing` or `--standalone-mode` to control this behavior

Created: 2026-02-02

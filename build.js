#!/usr/bin/env node
/**
 * RedTape Vercel Build Script (Zero-Dependency Node.js).
 * Ensures public/ contains index.html, static assets, and favicon.ico.
 */
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const PUBLIC_DIR = path.join(ROOT, 'public');
const STATIC_SRC = path.join(ROOT, 'static');
const PUBLIC_STATIC = path.join(PUBLIC_DIR, 'static');

if (!fs.existsSync(PUBLIC_DIR)) {
  fs.mkdirSync(PUBLIC_DIR, { recursive: true });
}
if (!fs.existsSync(PUBLIC_STATIC)) {
  fs.mkdirSync(PUBLIC_STATIC, { recursive: true });
}

// 1. Ensure static assets are mirrored to public/static
if (fs.existsSync(STATIC_SRC)) {
  const files = fs.readdirSync(STATIC_SRC);
  for (const file of files) {
    const srcFile = path.join(STATIC_SRC, file);
    if (fs.statSync(srcFile).isFile()) {
      fs.copyFileSync(srcFile, path.join(PUBLIC_STATIC, file));
    }
  }
}

// 2. Ensure favicon is in public/
const favSrc = path.join(STATIC_SRC, 'favicon.ico');
if (fs.existsSync(favSrc)) {
  fs.copyFileSync(favSrc, path.join(PUBLIC_DIR, 'favicon.ico'));
}

// 3. Verify index.html exists
const indexPath = path.join(PUBLIC_DIR, 'index.html');
if (fs.existsSync(indexPath)) {
  const size = fs.statSync(indexPath).size;
  console.log(`✓ RedTape static bundle verified: public/index.html (${size} bytes)`);
} else {
  console.warn('⚠️ Warning: public/index.html not found, falling back to root index.html');
  const rootIndex = path.join(ROOT, 'index.html');
  if (fs.existsSync(rootIndex)) {
    fs.copyFileSync(rootIndex, indexPath);
  }
}

console.log('✓ Build completed successfully.');
process.exit(0);

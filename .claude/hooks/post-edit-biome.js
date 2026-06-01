#!/usr/bin/env node
/**
 * Post-Edit Biome Hook - Automatically formats files after Edit/Write operations
 *
 * Fires: PostToolUse for Edit, Write, MultiEdit tools
 * Purpose: Run Biome on edited/written files to maintain consistent formatting
 *
 * Features:
 *   - Supports common web development file types
 *   - Skips generated/dependency directories
 *   - Auto-discovers Biome binary by walking up directory tree
 *   - Non-blocking: failures are silently ignored (10s timeout)
 *
 * Exit Codes:
 *   0 - Success (non-blocking, allows continuation)
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

// ═══════════════════════════════════════════════════════════════════════════
// CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════

const SUPPORTED_EXTENSIONS = new Set([
  '.ts',
  '.tsx',
  '.js',
  '.jsx',
  '.mjs',
  '.cjs',
  '.json',
  '.jsonc',
  '.css',
]);

const SKIP_PATTERNS = [
  /node_modules/,
  /\.git\//,
  /dist\//,
  /build\//,
  /\.next\//,
  /coverage\//,
  /\.cache\//,
  /\.vercel\//,
  /\.claude\//,
  /public\//,
];

const TIMEOUT_MS = 10000;

// ═══════════════════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════

function isSupportedExtension(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  return SUPPORTED_EXTENSIONS.has(ext);
}

function shouldSkipPath(filePath) {
  const normalizedPath = filePath.replace(/\\/g, '/');
  return SKIP_PATTERNS.some((pattern) => pattern.test(normalizedPath));
}

/**
 * Find Biome binary (local node_modules)
 */
function findBiomeBinary(fileDir) {
  let currentDir = fileDir;
  const root = path.parse(currentDir).root;

  while (currentDir !== root) {
    const biomeBin = path.join(currentDir, 'node_modules', '.bin', 'biome');

    if (fs.existsSync(biomeBin)) {
      return biomeBin;
    }

    currentDir = path.dirname(currentDir);
  }

  return null;
}

/**
 * Run Biome check --write on a file with timeout
 */
function runBiome(filePath, biomeBin) {
  return new Promise((resolve) => {
    if (!biomeBin) {
      resolve(false);
      return;
    }

    const args = ['check', '--write', '--unsafe', filePath];

    const child = spawn(biomeBin, args, {
      stdio: ['ignore', 'ignore', 'ignore'],
      timeout: TIMEOUT_MS,
      windowsHide: true,
    });

    const timeout = setTimeout(() => {
      child.kill('SIGTERM');
      resolve(false);
    }, TIMEOUT_MS);

    child.on('close', (code) => {
      clearTimeout(timeout);
      resolve(code === 0);
    });

    child.on('error', () => {
      clearTimeout(timeout);
      resolve(false);
    });
  });
}

/**
 * Extract file path from tool input
 */
function extractFilePath(payload) {
  const toolInput = payload.tool_input;
  if (!toolInput) return null;

  let input = toolInput;
  if (typeof toolInput === 'string') {
    try {
      input = JSON.parse(toolInput);
    } catch {
      return null;
    }
  }

  return input.file_path || input.path || null;
}

// ═══════════════════════════════════════════════════════════════════════════
// MAIN
// ═══════════════════════════════════════════════════════════════════════════

async function main() {
  try {
    const stdin = fs.readFileSync(0, 'utf-8').trim();
    if (!stdin) process.exit(0);

    const payload = JSON.parse(stdin);

    // Only process Edit, Write, MultiEdit tools
    if (!['Edit', 'Write', 'MultiEdit'].includes(payload.tool_name)) {
      process.exit(0);
    }

    // Only process successful tool calls
    if (payload.tool_error) {
      process.exit(0);
    }

    // Extract file path
    const filePath = extractFilePath(payload);
    if (!filePath) {
      process.exit(0);
    }

    // Resolve to absolute path
    const absolutePath = path.isAbsolute(filePath)
      ? filePath
      : path.resolve(process.cwd(), filePath);

    // Check if file exists
    if (!fs.existsSync(absolutePath)) {
      process.exit(0);
    }

    // Check if extension is supported
    if (!isSupportedExtension(absolutePath)) {
      process.exit(0);
    }

    // Check if path should be skipped
    if (shouldSkipPath(absolutePath)) {
      process.exit(0);
    }

    // Find Biome binary
    const fileDir = path.dirname(absolutePath);
    const biomeBin = findBiomeBinary(fileDir);

    // Run Biome (non-blocking, ignore result)
    await runBiome(absolutePath, biomeBin);

    process.exit(0);
  } catch {
    // Fail silently - formatting is non-critical
    process.exit(0);
  }
}

main();

#!/usr/bin/env node
/**
 * hook-utils.js — Shared utilities for Claude Code hooks.
 *
 * Provides:
 *  - parsePayload()   — read JSON from stdin (Claude Code hook protocol)
 *  - jsonOutput(obj)  — write JSON to stdout (hook response protocol)
 *  - colors           — ANSI color helpers for stderr logging
 *  - findProjectRoot  — walk up to find the project root (has package.json)
 */

const path = require('path');
const fs = require('fs');

/**
 * Parse the JSON payload that Claude Code sends to hooks on stdin.
 * Returns the parsed object, or an empty object on failure.
 */
async function parsePayload() {
  return new Promise((resolve) => {
    let data = '';
    process.stdin.setEncoding('utf-8');
    process.stdin.on('data', (chunk) => {
      data += chunk;
    });
    process.stdin.on('end', () => {
      try {
        resolve(JSON.parse(data));
      } catch {
        resolve({});
      }
    });
    // If stdin is already closed or not a TTY, resolve immediately
    if (process.stdin.readableEnded) {
      try {
        resolve(JSON.parse(data || '{}'));
      } catch {
        resolve({});
      }
    }
  });
}

/**
 * Write a JSON response to stdout (Claude Code hook response protocol).
 */
function jsonOutput(obj) {
  process.stdout.write(JSON.stringify(obj));
}

/**
 * ANSI color helpers for stderr logging.
 */
const colors = {
  red: (s) => `\x1b[31m${s}\x1b[0m`,
  green: (s) => `\x1b[32m${s}\x1b[0m`,
  yellow: (s) => `\x1b[33m${s}\x1b[0m`,
  blue: (s) => `\x1b[34m${s}\x1b[0m`,
  gray: (s) => `\x1b[90m${s}\x1b[0m`,
  bold: (s) => `\x1b[1m${s}\x1b[0m`,
  reset: '\x1b[0m',
};

/**
 * Walk up from `startDir` to find the project root (directory containing
 * package.json).  Falls back to `startDir` if nothing is found.
 */
async function findProjectRoot(startDir) {
  let dir = path.resolve(startDir);
  const root = path.parse(dir).root;

  while (dir !== root) {
    if (fs.existsSync(path.join(dir, 'package.json'))) {
      return dir;
    }
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }

  return startDir;
}

module.exports = {
  parsePayload,
  jsonOutput,
  colors,
  findProjectRoot,
};

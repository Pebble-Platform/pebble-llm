#!/usr/bin/env node
/**
 * Plan Before Code Hook — Require a plan/spec .md before code writes
 *
 * Fires: PreToolUse for Edit, Write, MultiEdit
 * Purpose: Block code edits unless a related plan/spec .md was read or
 *          written in the recent transcript. Forces a written plan first.
 *
 * Logic:
 *   1. Only triggers on code files (.ts, .tsx, .js, .jsx)
 *   2. Skips trivial edits (< 20 lines of new content)
 *   3. Scans recent transcript for Read/Write/Edit of .md files under
 *      specs/, docs/, plans/, or .claude/
 *   4. No plan .md found → deny with instructions
 *   5. Override: user says "skip plan", "no plan", or "just do it"
 *
 * Exit Codes:
 *   0 - Always (decision communicated via JSON output)
 */

const fs = require('fs');
const path = require('path');
const { parsePayload, jsonOutput } = require('./hook-utils.js');

const CODE_EXTENSIONS = new Set(['.ts', '.tsx', '.js', '.jsx']);

const SKIP_PATTERNS = [
  /node_modules/,
  /\.git\//,
  /dist\//,
  /\.next\//,
  /\.claude\//,
  /plans\//,
  /docs\//,
  /__tests__\//,
  /\.test\./,
  /\.spec\./,
];

const PLAN_DIR_PATTERN = /["']([^"']*(?:specs|docs|plans|\.claude)[\/\\][^"']*\.md)["']/i;

const TRIVIAL_LINE_THRESHOLD = 20;
const SEARCH_WINDOW_LINES = 200;
const SKIP_WINDOW_LINES = 30;
const MAX_TRANSCRIPT_BYTES = 512 * 1024;

function isCodeFile(filePath) {
  if (!filePath) return false;
  return CODE_EXTENSIONS.has(path.extname(filePath).toLowerCase());
}

function shouldSkipPath(filePath) {
  const normalized = filePath.replace(/\\/g, '/');
  return SKIP_PATTERNS.some((pattern) => pattern.test(normalized));
}

function isTrivialContent(content) {
  if (!content) return true;
  return content.split('\n').length < TRIVIAL_LINE_THRESHOLD;
}

function readTranscriptTail(transcriptPath) {
  if (!transcriptPath || !fs.existsSync(transcriptPath)) return '';
  try {
    const stat = fs.statSync(transcriptPath);
    if (stat.size <= MAX_TRANSCRIPT_BYTES) {
      return fs.readFileSync(transcriptPath, 'utf-8');
    }
    const fd = fs.openSync(transcriptPath, 'r');
    const buffer = Buffer.alloc(MAX_TRANSCRIPT_BYTES);
    const bytesRead = fs.readSync(
      fd,
      buffer,
      0,
      buffer.length,
      stat.size - buffer.length,
    );
    fs.closeSync(fd);
    return buffer.toString('utf-8', 0, bytesRead);
  } catch {
    return '';
  }
}

function hasRecentPlanMd(transcript) {
  if (!transcript) return false;
  const recent = transcript.split('\n').slice(-SEARCH_WINDOW_LINES).join('\n');
  return PLAN_DIR_PATTERN.test(recent);
}

function hasSkipOverride(transcript) {
  if (!transcript) return false;
  const recent = transcript.split('\n').slice(-SKIP_WINDOW_LINES).join('\n');
  return /skip\s+plan|no\s+plan|just\s+do\s+it/i.test(recent);
}

function allow() {
  jsonOutput({
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision: 'allow',
    },
  });
  process.exit(0);
}

function deny(reason) {
  jsonOutput({
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision: 'deny',
      permissionDecisionReason: reason,
    },
  });
  process.exit(0);
}

async function main() {
  try {
    const payload = await parsePayload();

    if (!['Edit', 'Write', 'MultiEdit'].includes(payload.tool_name)) {
      allow();
      return;
    }

    const filePath =
      payload.tool_input?.file_path ||
      payload.tool_input?.edits?.[0]?.file_path ||
      '';

    if (!isCodeFile(filePath) || shouldSkipPath(filePath)) {
      allow();
      return;
    }

    const newContent =
      payload.tool_input?.new_string ||
      payload.tool_input?.content ||
      payload.tool_input?.edits?.[0]?.new_string ||
      '';

    if (isTrivialContent(newContent)) {
      allow();
      return;
    }

    const transcript = readTranscriptTail(payload.transcript_path || '');

    if (hasSkipOverride(transcript)) {
      allow();
      return;
    }

    if (hasRecentPlanMd(transcript)) {
      allow();
      return;
    }

    deny(
      'Plan required before coding. Read or write a plan/spec .md under ' +
        'specs/, docs/, plans/, or .claude/ that describes the change, ' +
        'then retry. Override: say "skip plan" if this is intentional.',
    );
  } catch {
    allow();
  }
}

main();

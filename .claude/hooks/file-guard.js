#!/usr/bin/env node
/**
 * file-guard.js - Block AI access to sensitive files
 * PreToolUse hook for: Read, Edit, MultiEdit, Write, Bash
 */

const path = require('path');
const fs = require('fs');
const {
  parsePayload,
  colors,
  jsonOutput,
  findProjectRoot,
} = require('./hook-utils.js');

// Default sensitive file patterns
const DEFAULT_PATTERNS = [
  // Environment
  '.env',
  '.env.*',
  '!.env.example',
  '!.env.template',
  '!.env.sample',
  // Certificates
  '*.pem',
  '*.key',
  '*.crt',
  '*.cer',
  '*.p12',
  '*.pfx',
  // SSH
  '.ssh/**',
  '**/id_rsa*',
  '**/id_dsa*',
  '**/id_ecdsa*',
  '**/id_ed25519*',
  '*.ppk',
  // Cloud
  '.aws/**',
  'aws_credentials',
  '.azure/**',
  'azure.json',
  '.gcloud/**',
  'gcp-key.json',
  '.kube/**',
  '.docker/config.json',
  '.dockercfg',
  '.terraform/**',
  'terraform.tfvars',
  '.pulumi/**',
  // Package managers
  '.npmrc',
  '.pypirc',
  '.cargo/credentials',
  '.gem/credentials',
  '.bundle/config',
  '.m2/settings.xml',
  // Auth
  '.netrc',
  '.authinfo',
  '.authinfo.gpg',
  '.gitconfig',
  '.git-credentials',
  // Crypto
  '.gnupg/**',
  '*.gpg',
  '*.asc',
  '*.sig',
  'keystore',
  'truststore',
  // Database
  '.pgpass',
  '.my.cnf',
  '.mysql_history',
  '.psql_history',
  '.redis_history',
  '.mongoshrc.js',
  // Tokens
  '*.token',
  'token.*',
  'secrets.*',
  '*_token.txt',
  '*_token.json',
  '*_secret.txt',
  '*_secret.json',
  '.secrets',
  'api-keys.*',
  'credentials.*',
  // Wallets
  'wallet.dat',
  'wallet.json',
  '*.wallet',
  '*.keystore',
  'seed.txt',
  // Production
  'production.db',
  'prod.db',
  '**/prod*.db',
  '*.sqlite3',
  'dump.sql',
  '*.dump',
];

// Allowed .env file patterns (not sensitive)
const ALLOWED_ENV_PATTERNS = [
  '.env.example',
  '.env.template',
  '.env.sample',
  '.env.test',
  '.env.development.example',
  '.env.production.example',
  '.env.local.example',
];

/**
 * Check if a filename is an allowed .env file
 */
function isAllowedEnvFile(filePath) {
  const fileName = path.basename(filePath);
  return ALLOWED_ENV_PATTERNS.some(
    (pattern) => fileName === pattern || fileName.endsWith(pattern),
  );
}

// Dangerous bash command patterns
const DANGEROUS_BASH_PATTERNS = [
  /cat\s+.*\.env(?!\.example|\.template|\.sample|\.test)/i,
  /cat\s+.*credentials/i,
  /cat\s+.*secret/i,
  /cat\s+.*\/\.ssh\//i,
  /cat\s+.*\.pem/i,
  /cat\s+.*\.key/i,
  /head\s+.*\.env(?!\.example|\.template|\.sample|\.test)/i,
  /tail\s+.*\.env(?!\.example|\.template|\.sample|\.test)/i,
  /less\s+.*\.env(?!\.example|\.template|\.sample|\.test)/i,
  /more\s+.*\.env(?!\.example|\.template|\.sample|\.test)/i,
  /xargs\s+.*cat/i,
  /find\s+.*-exec\s+.*cat/i,
  /find\s+.*-name\s+['"]?\.env['"]?\s*.*\|\s*.*xargs\s+.*cat/i,
];

/**
 * Load ignore patterns from various ignore files
 */
function loadIgnorePatterns(projectRoot) {
  const patterns = [...DEFAULT_PATTERNS];
  const ignoreFiles = [
    '.agentignore',
    '.aiignore',
    '.cursorignore',
    '.codeiumignore',
  ];

  for (const ignoreFile of ignoreFiles) {
    const filePath = path.join(projectRoot, ignoreFile);
    if (fs.existsSync(filePath)) {
      try {
        const content = fs.readFileSync(filePath, 'utf-8');
        const lines = content
          .split('\n')
          .map((line) => line.trim())
          .filter((line) => line && !line.startsWith('#'));
        patterns.push(...lines);
      } catch {}
    }
  }

  return patterns;
}

/**
 * Convert glob pattern to regex
 */
function patternToRegex(pattern) {
  // Handle negation patterns
  const isNegation = pattern.startsWith('!');
  const cleanPattern = isNegation ? pattern.slice(1) : pattern;

  // Convert glob to regex
  const regex = cleanPattern
    .replace(/\./g, '\\.')
    .replace(/\*\*/g, '___GLOBSTAR___')
    .replace(/\*/g, '[^/]*')
    .replace(/___GLOBSTAR___/g, '.*')
    .replace(/\?/g, '.');

  return { regex: new RegExp(`(^|/)${regex}$`), isNegation };
}

/**
 * Check if a file matches sensitive patterns
 */
function isFileProtected(filePath, patterns) {
  const normalizedPath = filePath.replace(/\\/g, '/');
  const fileName = path.basename(normalizedPath);

  // Explicitly allow .env.example and similar files
  if (isAllowedEnvFile(normalizedPath)) {
    return false;
  }

  let isProtected = false;

  for (const pattern of patterns) {
    const { regex, isNegation } = patternToRegex(pattern);

    if (regex.test(normalizedPath) || regex.test(fileName)) {
      if (isNegation) {
        isProtected = false; // Negation pattern allows the file
      } else {
        isProtected = true;
      }
    }
  }

  return isProtected;
}

/**
 * Check bash command for dangerous patterns
 */
function isDangerousBashCommand(command) {
  return DANGEROUS_BASH_PATTERNS.some((pattern) => pattern.test(command));
}

/**
 * Clean a path by removing surrounding quotes and trailing punctuation
 */
function cleanPath(filePath) {
  if (!filePath) return '';
  // Remove surrounding quotes (single or double)
  let cleaned = filePath.replace(/^["']+|["']+$/g, '');
  // Remove trailing punctuation that might be from command parsing
  cleaned = cleaned.replace(/['"]+$/, '');
  return cleaned;
}

/**
 * Extract file paths from bash command
 */
function extractPathsFromCommand(command) {
  const paths = [];

  // Extract quoted paths
  const quotedPaths = command.match(/["']([^"']+)["']/g) || [];
  for (const match of quotedPaths) {
    const extracted = match.slice(1, -1);
    const cleaned = cleanPath(extracted);
    if (cleaned && !cleaned.includes(' ')) {
      paths.push(cleaned);
    }
  }

  // Extract unquoted paths (words containing / or .)
  const words = command.split(/\s+/);
  for (const word of words) {
    const cleaned = cleanPath(word);
    if (
      (cleaned.includes('/') || cleaned.includes('.')) &&
      !cleaned.startsWith('-') &&
      !cleaned.includes('=') &&
      !['&&', '||', '|', ';', '>', '<', '>>', '2>', '2>&1'].includes(cleaned)
    ) {
      paths.push(cleaned);
    }
  }

  return [...new Set(paths)];
}

/**
 * Allow the operation
 */
function allow() {
  jsonOutput({
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision: 'allow',
    },
  });
  process.exit(0);
}

/**
 * Deny the operation
 */
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
    const toolName = payload.tool_name;
    const toolInput = payload.tool_input || {};

    // Only process relevant tools
    const supportedTools = ['Read', 'Edit', 'MultiEdit', 'Write', 'Bash'];
    if (!toolName || !supportedTools.includes(toolName)) {
      allow();
      return;
    }

    const projectRoot = await findProjectRoot(process.cwd());
    const patterns = loadIgnorePatterns(projectRoot);

    // Handle Bash commands
    if (toolName === 'Bash') {
      const command = toolInput.command || '';

      if (!command.trim()) {
        allow();
        return;
      }

      // Check for dangerous command patterns
      if (isDangerousBashCommand(command)) {
        deny(
          'Access denied: Command appears to access sensitive files. Commands that read .env, credentials, or key files are blocked.',
        );
      }

      // Extract and check paths from command
      const paths = extractPathsFromCommand(command);
      for (const filePath of paths) {
        if (isFileProtected(filePath, patterns)) {
          deny(
            `Access denied: '${path.basename(filePath)}' is protected. This path in the Bash command matches patterns that prevent AI assistant access.`,
          );
        }
      }

      allow();
      return;
    }

    // Handle file-based tools
    const filePath = toolInput.file_path;
    if (!filePath || !filePath.trim()) {
      allow();
      return;
    }

    // Check if file is protected
    if (isFileProtected(filePath, patterns)) {
      deny(
        `Access denied: '${path.basename(filePath)}' is protected. This file matches patterns that prevent AI assistant access.`,
      );
    }

    allow();
  } catch (error) {
    // On error, allow the operation to prevent blocking workflow
    console.error(`file-guard error: ${error.message}`);
    allow();
  }
}

main();

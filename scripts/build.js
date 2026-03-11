#!/usr/bin/env node
/**
 * Perfect Text Overlay - Build Script
 */

const fs = require('fs');
const path = require('path');

console.log('Building perfect-text-overlay...\n');

// Ensure all required directories exist
const dirs = ['lib', 'bin', 'scripts', 'assets', 'assets/fonts'];

for (const dir of dirs) {
  const fullPath = path.join(__dirname, '..', dir);
  if (!fs.existsSync(fullPath)) {
    fs.mkdirSync(fullPath, { recursive: true });
    console.log(`Created directory: ${dir}`);
  }
}

// Make CLI executable (on Unix)
if (process.platform !== 'win32') {
  const cliPath = path.join(__dirname, '..', 'bin', 'cli.js');
  if (fs.existsSync(cliPath)) {
    fs.chmodSync(cliPath, '755');
    console.log('Made CLI executable');
  }
}

console.log('\nBuild complete!');

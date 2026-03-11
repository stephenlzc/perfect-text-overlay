#!/usr/bin/env node
/**
 * Perfect Text Overlay - Installation Script
 * 
 * Checks Python installation and installs required dependencies.
 */

const { spawn, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const PACKAGE_ROOT = path.resolve(__dirname, '..');

// Colors for terminal output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function logInfo(message) {
  log(`ℹ ${message}`, 'blue');
}

function logSuccess(message) {
  log(`✓ ${message}`, 'green');
}

function logError(message) {
  log(`✗ ${message}`, 'red');
}

function logWarning(message) {
  log(`⚠ ${message}`, 'yellow');
}

/**
 * Check if a command exists
 */
function commandExists(command) {
  try {
    const cmd = process.platform === 'win32' ? 'where' : 'which';
    execSync(`${cmd} ${command}`, { stdio: 'pipe' });
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * Check Python version
 */
function checkPythonVersion() {
  return new Promise((resolve) => {
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    
    if (!commandExists(pythonCmd)) {
      resolve({ exists: false, version: null });
      return;
    }

    const child = spawn(pythonCmd, ['--version'], { stdio: ['pipe', 'pipe', 'pipe'] });
    
    let output = '';
    child.stdout.on('data', (data) => {
      output += data.toString();
    });
    child.stderr.on('data', (data) => {
      output += data.toString();
    });

    child.on('close', (code) => {
      if (code !== 0) {
        resolve({ exists: false, version: null });
        return;
      }

      const versionMatch = output.match(/Python (\d+)\.(\d+)\.(\d+)/);
      if (versionMatch) {
        const major = parseInt(versionMatch[1]);
        const minor = parseInt(versionMatch[2]);
        resolve({ 
          exists: true, 
          version: versionMatch[0],
          major,
          minor,
          ok: major > 3 || (major === 3 && minor >= 7)
        });
      } else {
        resolve({ exists: true, version: output.trim(), ok: true });
      }
    });

    child.on('error', () => {
      resolve({ exists: false, version: null });
    });
  });
}

/**
 * Check if Python packages are installed
 */
function checkPythonPackages() {
  return new Promise((resolve) => {
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    
    const child = spawn(pythonCmd, ['-c', `
import sys
result = {"pillow": False, "numpy": False}
try:
    from PIL import Image
    result["pillow"] = True
except:
    pass
try:
    import numpy
    result["numpy"] = True
except:
    pass
print(result)
`], { stdio: ['pipe', 'pipe', 'pipe'] });

    let output = '';
    child.stdout.on('data', (data) => {
      output += data.toString();
    });

    child.on('close', () => {
      try {
        // Parse the Python dict string
        const pillow = output.includes("'pillow': True") || output.includes('"pillow": True');
        const numpy = output.includes("'numpy': True") || output.includes('"numpy": True');
        resolve({ pillow, numpy });
      } catch (e) {
        resolve({ pillow: false, numpy: false });
      }
    });

    child.on('error', () => {
      resolve({ pillow: false, numpy: false });
    });
  });
}

/**
 * Install Python packages
 */
function installPythonPackages(packages) {
  return new Promise((resolve, reject) => {
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    const pipCmd = process.platform === 'win32' ? 'pip' : 'pip3';
    
    // Try pip first, fallback to python -m pip
    const args = ['-m', 'pip', 'install', '--user', ...packages];
    
    logInfo(`Installing packages: ${packages.join(', ')}...`);
    
    const child = spawn(pythonCmd, args, { 
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: PACKAGE_ROOT
    });

    let stdout = '';
    let stderr = '';

    child.stdout.on('data', (data) => {
      stdout += data.toString();
      process.stdout.write(data);
    });

    child.stderr.on('data', (data) => {
      stderr += data.toString();
      process.stderr.write(data);
    });

    child.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`pip install failed with code ${code}`));
        return;
      }
      resolve();
    });

    child.on('error', (error) => {
      reject(error);
    });
  });
}

/**
 * Copy font files to assets directory
 */
async function setupFonts() {
  const assetsDir = path.join(PACKAGE_ROOT, 'assets');
  const fontsDir = path.join(assetsDir, 'fonts');
  
  // Create directories if they don't exist
  if (!fs.existsSync(assetsDir)) {
    fs.mkdirSync(assetsDir, { recursive: true });
  }
  if (!fs.existsSync(fontsDir)) {
    fs.mkdirSync(fontsDir, { recursive: true });
  }

  logInfo('Font directory ready: ' + fontsDir);
}

/**
 * Main installation function
 */
async function install() {
  log('\n' + '='.repeat(60), 'cyan');
  log('  Perfect Text Overlay - Installation', 'cyan');
  log('='.repeat(60) + '\n', 'cyan');

  // Check Python
  logInfo('Checking Python installation...');
  const pythonStatus = await checkPythonVersion();
  
  if (!pythonStatus.exists) {
    logError('Python is not installed or not in PATH');
    log('\nPlease install Python 3.7 or higher:');
    log('  Windows: https://www.python.org/downloads/');
    log('  macOS: brew install python3');
    log('  Linux: sudo apt-get install python3 python3-pip');
    process.exit(1);
  }

  if (!pythonStatus.ok) {
    logWarning(`Python ${pythonStatus.version} found, but 3.7+ is recommended`);
  } else {
    logSuccess(`Python ${pythonStatus.version} is ready`);
  }

  // Check existing packages
  logInfo('Checking Python packages...');
  const packages = await checkPythonPackages();
  
  const toInstall = [];
  if (!packages.pillow) {
    toInstall.push('Pillow');
    logWarning('Pillow is not installed');
  } else {
    logSuccess('Pillow is installed');
  }
  
  if (!packages.numpy) {
    toInstall.push('numpy');
    logWarning('NumPy is not installed');
  } else {
    logSuccess('NumPy is installed');
  }

  // Install missing packages
  if (toInstall.length > 0) {
    log('\n' + '-'.repeat(60), 'cyan');
    logInfo('Installing missing packages...');
    
    try {
      await installPythonPackages(toInstall);
      logSuccess('Packages installed successfully');
    } catch (error) {
      logError(`Failed to install packages: ${error.message}`);
      log('\nPlease install manually:');
      log(`  pip install ${toInstall.join(' ')}`, 'yellow');
    }
  } else {
    logSuccess('All Python packages are ready');
  }

  // Setup fonts
  log('\n' + '-'.repeat(60), 'cyan');
  await setupFonts();

  // Final status
  log('\n' + '='.repeat(60), 'cyan');
  logSuccess('Installation complete!');
  log('='.repeat(60) + '\n', 'cyan');
  
  log('You can now use the CLI:');
  log('  pto --help', 'yellow');
  log('  pto check', 'yellow');
  log('');
}

// Run installation
install().catch((error) => {
  logError(`Installation failed: ${error.message}`);
  process.exit(1);
});

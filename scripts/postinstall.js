#!/usr/bin/env node
/**
 * Post-install script
 * Checks environment and optionally downloads fonts
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const isCI = process.env.CI || process.env.CONTINUOUS_INTEGRATION;
const skipFonts = process.env.PTO_SKIP_FONTS === 'true';

function checkPython() {
  try {
    execSync('python3 --version', { stdio: 'ignore' });
    return 'python3';
  } catch {
    try {
      execSync('python --version', { stdio: 'ignore' });
      return 'python';
    } catch {
      return null;
    }
  }
}

function checkPythonPackages(pythonCmd) {
  const packages = ['PIL', 'numpy'];
  const missing = [];
  
  for (const pkg of packages) {
    try {
      execSync(`${pythonCmd} -c "import ${pkg}"`, { stdio: 'ignore' });
    } catch {
      missing.push(pkg === 'PIL' ? 'Pillow' : pkg);
    }
  }
  
  return missing;
}

async function main() {
  console.log('\n🔧 Perfect Text Overlay - Setup\n');
  
  // Check Python
  const pythonCmd = checkPython();
  if (!pythonCmd) {
    console.log('⚠️  Python not found!');
    console.log('   Please install Python 3.8+ to use this package.');
    console.log('   Visit: https://www.python.org/downloads/\n');
  } else {
    const version = execSync(`${pythonCmd} --version`, { encoding: 'utf8' }).trim();
    console.log(`✓ ${version}`);
    
    // Check Python packages
    const missing = checkPythonPackages(pythonCmd);
    if (missing.length > 0) {
      console.log(`⚠️  Missing Python packages: ${missing.join(', ')}`);
      console.log('   Run: pip install ' + missing.join(' '));
    } else {
      console.log('✓ Python dependencies ready');
    }
  }
  
  // Download fonts (unless skipped)
  if (!isCI && !skipFonts) {
    console.log('\n📦 Fonts:');
    const fontsDir = path.join(__dirname, '..', 'assets', 'fonts');
    
    // Check if any fonts exist
    const hasFonts = fs.existsSync(fontsDir) && 
                     fs.readdirSync(fontsDir).some(f => f.endsWith('.otf') || f.endsWith('.ttf'));
    
    if (hasFonts) {
      console.log('   Fonts already installed');
    } else {
      console.log('   Fonts not installed (optional)');
      console.log('   Run: npm run download-fonts');
      console.log('   Or: pto download-fonts');
    }
  }
  
  console.log('\n✨ Setup complete!\n');
  console.log('Quick start:');
  console.log('  pto --help           Show help');
  console.log('  pto check            Check environment\n');
}

main().catch(console.error);

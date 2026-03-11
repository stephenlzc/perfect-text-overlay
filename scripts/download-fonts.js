#!/usr/bin/env node
/**
 * Font download script
 * Downloads required fonts from Google Fonts or CDN
 * This keeps the npm package size small
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

const FONTS_DIR = path.join(__dirname, '..', 'assets', 'fonts');

// Font definitions with download URLs
const FONTS = {
  'NotoSansCJKsc-Bold.otf': {
    url: 'https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Bold.otf',
    description: 'Noto Sans CJK SC Bold - Simplified Chinese'
  },
  'NotoSerifCJKsc-Bold.otf': {
    url: 'https://github.com/notofonts/noto-cjk/raw/main/Serif/OTF/SimplifiedChinese/NotoSerifCJKsc-Bold.otf',
    description: 'Noto Serif CJK SC Bold - Traditional style'
  },
  'NotoSansCJKtc-Bold.otf': {
    url: 'https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/TraditionalChinese/NotoSansCJKtc-Bold.otf',
    description: 'Noto Sans CJK TC Bold - Traditional Chinese'
  },
  'NotoSansCJKkr-Bold.otf': {
    url: 'https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/Korean/NotoSansCJKkr-Bold.otf',
    description: 'Noto Sans CJK KR Bold - Korean'
  },
  'Roboto-Bold.ttf': {
    url: 'https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf',
    description: 'Roboto Bold - English/Latin'
  },
  'OpenSans-Bold.ttf': {
    url: 'https://github.com/googlefonts/opensans/raw/main/fonts/ttf/OpenSans-Bold.ttf',
    description: 'Open Sans Bold - English/Latin'
  }
};

function downloadFile(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    https.get(url, { timeout: 30000 }, (response) => {
      if (response.statusCode === 302 || response.statusCode === 301) {
        // Follow redirect
        file.close();
        fs.unlinkSync(dest);
        downloadFile(response.headers.location, dest).then(resolve).catch(reject);
        return;
      }
      
      if (response.statusCode !== 200) {
        file.close();
        fs.unlinkSync(dest);
        reject(new Error(`Failed to download: ${response.statusCode}`));
        return;
      }

      response.pipe(file);
      file.on('finish', () => {
        file.close();
        resolve();
      });
    }).on('error', (err) => {
      fs.unlinkSync(dest);
      reject(err);
    });
  });
}

async function downloadFonts(fontNames = null) {
  // Ensure fonts directory exists
  if (!fs.existsSync(FONTS_DIR)) {
    fs.mkdirSync(FONTS_DIR, { recursive: true });
  }

  const fontsToDownload = fontNames || Object.keys(FONTS);
  const results = { success: [], failed: [] };

  console.log('📥 Downloading fonts...\n');

  for (const fontName of fontsToDownload) {
    const fontInfo = FONTS[fontName];
    if (!fontInfo) {
      console.log(`  ⚠️  Unknown font: ${fontName}`);
      results.failed.push(fontName);
      continue;
    }

    const destPath = path.join(FONTS_DIR, fontName);
    
    // Skip if already exists
    if (fs.existsSync(destPath)) {
      console.log(`  ✓ ${fontName} (already exists)`);
      results.success.push(fontName);
      continue;
    }

    process.stdout.write(`  ⏳ ${fontName}... `);
    
    try {
      await downloadFile(fontInfo.url, destPath);
      console.log('✓');
      results.success.push(fontName);
    } catch (err) {
      console.log(`✗ (${err.message})`);
      results.failed.push(fontName);
    }
  }

  console.log('\n' + '='.repeat(50));
  console.log(`Downloaded: ${results.success.length}/${fontsToDownload.length}`);
  
  if (results.failed.length > 0) {
    console.log(`Failed: ${results.failed.length}`);
    console.log('  Note: Fonts are optional. System fonts will be used as fallback.');
  }
  
  return results;
}

// CLI usage
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.includes('--list')) {
    console.log('Available fonts:\n');
    for (const [name, info] of Object.entries(FONTS)) {
      const exists = fs.existsSync(path.join(FONTS_DIR, name)) ? '✓' : ' ';
      console.log(`  [${exists}] ${name}`);
      console.log(`      ${info.description}`);
      console.log('');
    }
    process.exit(0);
  }
  
  if (args.includes('--all')) {
    downloadFonts().then(() => process.exit(0));
  } else if (args.length > 0) {
    downloadFonts(args).then(() => process.exit(0));
  } else {
    // Download minimal set by default
    downloadFonts(['NotoSansCJKsc-Bold.otf', 'Roboto-Bold.ttf']).then(() => process.exit(0));
  }
}

module.exports = { downloadFonts, FONTS };

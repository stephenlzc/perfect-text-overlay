#!/usr/bin/env node
/**
 * Perfect Text Overlay
 * Main module for separating image generation and text overlay
 */

const { execSync, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Get script directory
const SCRIPTS_DIR = path.join(__dirname, '..', 'scripts');

/**
 * Check if Python and required packages are available
 * @returns {boolean}
 */
function checkPythonEnvironment() {
  try {
    execSync('python3 --version', { stdio: 'ignore' });
    return true;
  } catch {
    try {
      execSync('python --version', { stdio: 'ignore' });
      return true;
    } catch {
      return false;
    }
  }
}

/**
 * Run a Python script and return the output
 * @param {string} scriptName - Name of the Python script
 * @param {string[]} args - Arguments to pass to the script
 * @returns {Promise<Object>} - Parsed JSON output
 */
function runPythonScript(scriptName, args = []) {
  return new Promise((resolve, reject) => {
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    const scriptPath = path.join(SCRIPTS_DIR, scriptName);
    
    if (!fs.existsSync(scriptPath)) {
      reject(new Error(`Script not found: ${scriptPath}`));
      return;
    }

    const child = spawn(pythonCmd, [scriptPath, ...args], {
      encoding: 'utf8',
      stdio: ['pipe', 'pipe', 'pipe']
    });

    let stdout = '';
    let stderr = '';

    child.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    child.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    child.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python script failed with code ${code}: ${stderr}`));
        return;
      }

      try {
        // Try to parse JSON output
        const lines = stdout.trim().split('\n');
        const jsonLine = lines.find(line => {
          try {
            JSON.parse(line);
            return true;
          } catch {
            return false;
          }
        });
        
        if (jsonLine) {
          resolve(JSON.parse(jsonLine));
        } else {
          resolve({ output: stdout.trim() });
        }
      } catch {
        resolve({ output: stdout.trim() });
      }
    });

    child.on('error', (err) => {
      reject(new Error(`Failed to run Python script: ${err.message}`));
    });
  });
}

/**
 * Separate user prompt into image-only prompt and text requirements
 * @param {string} prompt - User's original prompt
 * @returns {Promise<Object>} - Separated prompt and text requirements
 */
async function separatePrompt(prompt) {
  if (!prompt || typeof prompt !== 'string') {
    throw new Error('Prompt must be a non-empty string');
  }

  try {
    // Use Python script for prompt separation
    const result = await runPythonScript('prompt_separator.py', []);
    
    // Since the Python script doesn't accept command line args for prompt,
    // we need to modify it or use a different approach
    // For now, we'll import the function directly
    return separatePromptSync(prompt);
  } catch (error) {
    throw new Error(`Failed to separate prompt: ${error.message}`);
  }
}

/**
 * Synchronous version of separatePrompt using inline Python execution
 * @param {string} prompt - User's original prompt
 * @returns {Object} - Separated prompt and text requirements
 */
function separatePromptSync(prompt) {
  if (!prompt || typeof prompt !== 'string') {
    throw new Error('Prompt must be a non-empty string');
  }

  // Simple implementation based on prompt_separator.py logic
  const textItems = extractTextMentions(prompt);
  
  if (textItems.length === 0) {
    return {
      has_text: false,
      image_prompt: prompt,
      text_requirements: null
    };
  }

  const imagePrompt = createImagePrompt(prompt, textItems);
  const textRequirements = createTextRequirements(textItems, prompt);

  return {
    has_text: true,
    image_prompt: imagePrompt,
    text_requirements: textRequirements,
    original_text_items: textItems
  };
}

/**
 * Extract text mentions from the prompt
 * @param {string} prompt - User's original prompt
 * @returns {Array} - Array of text items
 */
function extractTextMentions(prompt) {
  const textItems = [];
  const QUOTES = '"\u201c\u201d\u2018\u2019\'';
  const seenContents = new Set();

  // Chinese patterns
  const patternsCn = [
    new RegExp(`(?:标题|主题)[是为写][:：]?\\s*[${QUOTES}]([^${QUOTES}]+)[${QUOTES}]`, 'gi'),
    new RegExp(`写[着为][:：]?\\s*[${QUOTES}]([^${QUOTES}]+)[${QUOTES}]`, 'gi'),
    new RegExp(`加[上入][:：]?\\s*[${QUOTES}]([^${QUOTES}]+)[${QUOTES}]?[文]?字?`, 'gi'),
    new RegExp(`文[字内容][:：]?\\s*[${QUOTES}]([^${QUOTES}]+)[${QUOTES}]`, 'gi'),
  ];

  // English patterns
  const patternsEn = [
    new RegExp(`\\btext[:\\s]+[${QUOTES}]([^${QUOTES}]+)[${QUOTES}]`, 'gi'),
    new RegExp(`\\btitle[:\\s]+[${QUOTES}]([^${QUOTES}]+)[${QUOTES}]`, 'gi'),
    new RegExp(`\\bcaption[:\\s]+[${QUOTES}]([^${QUOTES}]+)[${QUOTES}]`, 'gi'),
  ];

  const allPatterns = [...patternsCn, ...patternsEn];

  for (const pattern of allPatterns) {
    const matches = prompt.matchAll(pattern);
    for (const match of matches) {
      const content = match[1].trim();
      if (content && content.length > 1 && !seenContents.has(content)) {
        seenContents.add(content);
        textItems.push({
          content,
          position: 'auto',
          start_idx: match.index,
          end_idx: match.index + match[0].length
        });
      }
    }
  }

  // Flowchart pattern
  const listPattern = /(?:包含|步骤|流程|如[下下]|步骤[:：])?\s*[:：]?\s*(?:\n)?\s*(\d+[.、]\s*[^\d\n]+(?:\n?\s*\d+[.、]\s*[^\d\n]+)*)/gi;
  const listMatches = prompt.matchAll(listPattern);
  for (const match of listMatches) {
    const listText = match[1];
    const steps = [...listText.matchAll(/\d+[.、]\s*([^\d\n]+)/g)];
    steps.forEach((step, i) => {
      const stepContent = step[1].trim();
      if (stepContent) {
        textItems.push({
          content: stepContent,
          position: `step_${i + 1}`,
          semantic_type: 'flowchart_node',
          start_idx: match.index,
          end_idx: match.index + match[0].length
        });
      }
    });
  }

  return textItems;
}

/**
 * Create image-only prompt by removing text descriptions
 * @param {string} originalPrompt - Original user prompt
 * @param {Array} textItems - Extracted text items
 * @returns {string} - Image-only prompt
 */
function createImagePrompt(originalPrompt, textItems) {
  let imagePrompt = originalPrompt;
  
  // Sort by index in reverse order to replace from end to start
  const sortedItems = [...textItems].sort((a, b) => b.start_idx - a.start_idx);
  
  for (const item of sortedItems) {
    const replacement = getVisualReplacement(item);
    imagePrompt = imagePrompt.slice(0, item.start_idx) + replacement + imagePrompt.slice(item.end_idx);
  }

  // Clean up
  imagePrompt = imagePrompt
    .replace(/\s+/g, ' ')
    .replace(/,\s*,/g, ',')
    .replace(/\s+,/g, ',')
    .trim(' ,.:;');

  // Enhance
  const enhancements = ['high quality', 'professional', 'clean composition', 'suitable for text overlay'];
  const hasQuality = /high quality|4k|8k|professional|hd/i.test(imagePrompt);
  
  if (!hasQuality) {
    imagePrompt += ', ' + enhancements.join(', ');
  }

  return imagePrompt;
}

/**
 * Get visual replacement for text mention
 * @param {Object} item - Text item
 * @returns {string} - Visual replacement text
 */
function getVisualReplacement(item) {
  if (item.semantic_type === 'flowchart_node') {
    return 'a blank node box';
  }

  const replacements = {
    top: 'blank header area at top',
    bottom: 'blank footer area at bottom',
    center: 'blank central focal area',
    left: 'blank area on the left side',
    right: 'blank area on the right side',
    auto: 'blank area suitable for text overlay'
  };

  return replacements[item.position] || 'blank area for text';
}

/**
 * Create structured text requirements
 * @param {Array} textItems - Extracted text items
 * @param {string} originalPrompt - Original user prompt
 * @returns {Object} - Text requirements
 */
function createTextRequirements(textItems, originalPrompt) {
  const isFlowchart = textItems.some(item => item.semantic_type === 'flowchart_node');

  const requirements = {
    type: isFlowchart ? 'flowchart' : 'single_or_few',
    text_groups: [],
    style_hints: extractStyleHints(originalPrompt)
  };

  textItems.forEach((item, i) => {
    requirements.text_groups.push({
      id: `text_${i + 1}`,
      content: item.content,
      semantic_position: item.position,
      node_type: item.semantic_type || 'text_block'
    });
  });

  return requirements;
}

/**
 * Extract style hints from prompt
 * @param {string} prompt - User's original prompt
 * @returns {Object} - Style hints
 */
function extractStyleHints(prompt) {
  const hints = {
    color: null,
    font_style: null,
    size: null
  };

  const promptLower = prompt.toLowerCase();

  // Color hints
  const colorKeywords = {
    red: ['红色', 'red', '红'],
    blue: ['蓝色', 'blue', '蓝'],
    green: ['绿色', 'green', '绿'],
    gold: ['金色', 'gold', '金'],
    white: ['白色', 'white', '白'],
    black: ['黑色', 'black', '黑']
  };

  for (const [color, keywords] of Object.entries(colorKeywords)) {
    if (keywords.some(kw => promptLower.includes(kw))) {
      hints.color = color;
      break;
    }
  }

  // Font style hints
  const fontKeywords = {
    calligraphy: ['书法', '手写', 'calligraphy', 'handwritten'],
    modern: ['现代', '简约', 'modern', 'minimalist'],
    cartoon: ['卡通', '可爱', 'cartoon', 'cute'],
    traditional: ['传统', '古典', 'traditional', 'classic']
  };

  for (const [style, keywords] of Object.entries(fontKeywords)) {
    if (keywords.some(kw => promptLower.includes(kw))) {
      hints.font_style = style;
      break;
    }
  }

  return hints;
}

/**
 * Analyze image for text placement
 * @param {string} imagePath - Path to the image file
 * @param {Object} textRequirements - Text requirements from separatePrompt
 * @returns {Promise<Object>} - Analysis results
 */
async function analyzeImage(imagePath, textRequirements) {
  if (!fs.existsSync(imagePath)) {
    throw new Error(`Image not found: ${imagePath}`);
  }

  // For now, return a simplified analysis
  // In production, this would call the Python image_analyzer.py script
  return {
    image_size: [800, 600],
    color_scheme: {
      dominant_rgb: [128, 128, 128],
      brightness: 128,
      color_family: 'neutral',
      suggested_text_color: [30, 30, 30],
      suggested_bg: 'light'
    },
    safe_zones: [
      {
        bbox: [50, 50, 750, 150],
        position_name: 'top_center',
        complexity: 15.5,
        area: 70000,
        avg_color: [200, 200, 200]
      },
      {
        bbox: [50, 450, 750, 550],
        position_name: 'bottom_center',
        complexity: 12.3,
        area: 70000,
        avg_color: [180, 180, 180]
      }
    ],
    complexity_map: 'generated'
  };
}

/**
 * Render text on image
 * @param {string} imagePath - Path to input image
 * @param {string} outputPath - Path for output image
 * @param {Array} placements - Text placement information
 * @param {Object} userChoices - User customization choices
 * @returns {Promise<string>} - Path to output image
 */
async function renderTextOnImage(imagePath, outputPath, placements, userChoices = {}) {
  if (!fs.existsSync(imagePath)) {
    throw new Error(`Input image not found: ${imagePath}`);
  }

  // Ensure output directory exists
  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // For now, just copy the image (actual rendering requires Python PIL)
  // In production, this would call scripts/text_renderer.py
  fs.copyFileSync(imagePath, outputPath);

  return outputPath;
}

/**
 * Get text placement suggestions based on analysis
 * @param {Object} analysis - Analysis results from analyzeImage
 * @param {Object} textRequirements - Text requirements
 * @returns {Array} - Placement suggestions
 */
function getTextPlacementSuggestions(analysis, textRequirements) {
  const suggestions = [];
  const textGroups = textRequirements?.text_groups || [];
  const safeZones = analysis?.safe_zones || [];

  if (textRequirements?.type === 'flowchart') {
    // For flowcharts, create node positions
    const nodes = analysis?.detected_nodes || [];
    textGroups.forEach((group, i) => {
      if (i < nodes.length) {
        suggestions.push({
          text_id: group.id,
          content: group.content,
          placement: {
            bbox: nodes[i].bbox,
            center: nodes[i].center,
            type: 'centered_in_box'
          },
          style_suggestions: {
            color: analysis?.color_scheme?.suggested_text_color || [30, 30, 30],
            max_width: nodes[i].bbox[2] - nodes[i].bbox[0] - 20
          }
        });
      }
    });
  } else {
    // For single/few text, use safe zones
    const positionPriority = {
      top: safeZones.filter(z => z.position_name.includes('top')),
      bottom: safeZones.filter(z => z.position_name.includes('bottom')),
      center: safeZones.filter(z => z.position_name === 'center'),
      left: safeZones.filter(z => z.position_name.includes('left')),
      right: safeZones.filter(z => z.position_name.includes('right')),
      auto: safeZones
    };

    textGroups.forEach((group) => {
      const semanticPos = group.semantic_position || 'auto';
      const candidates = positionPriority[semanticPos] || safeZones;

      if (candidates.length > 0) {
        const zone = candidates[0];
        suggestions.push({
          text_id: group.id,
          content: group.content,
          placement: {
            bbox: zone.bbox,
            position_name: zone.position_name,
            type: 'overlay'
          },
          style_suggestions: {
            color: analysis?.color_scheme?.suggested_text_color || [30, 30, 30],
            contrast_bg: zone.avg_color,
            max_width: zone.bbox[2] - zone.bbox[0] - 40
          }
        });
      }
    });
  }

  return suggestions;
}

module.exports = {
  separatePrompt,
  separatePromptSync,
  analyzeImage,
  renderTextOnImage,
  getTextPlacementSuggestions,
  checkPythonEnvironment,
  extractTextMentions,
  createImagePrompt,
  createTextRequirements,
  extractStyleHints
};

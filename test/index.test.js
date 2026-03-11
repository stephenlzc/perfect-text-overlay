#!/usr/bin/env node
/**
 * Test suite for perfect-text-overlay
 * Uses Node.js built-in test runner
 */

const { describe, it, before } = require('node:test');
const assert = require('node:assert');
const fs = require('fs');
const path = require('path');

const {
  separatePromptSync,
  analyzeImage,
  renderTextOnImage,
  getTextPlacementSuggestions,
  checkPythonEnvironment,
  extractTextMentions,
  createImagePrompt,
  createTextRequirements,
  extractStyleHints
} = require('../lib/index');

// Test fixtures path
const FIXTURES_DIR = path.join(__dirname, 'fixtures');
const OUTPUTS_DIR = path.join(__dirname, '..', 'outputs');

// Ensure outputs directory exists
if (!fs.existsSync(OUTPUTS_DIR)) {
  fs.mkdirSync(OUTPUTS_DIR, { recursive: true });
}

describe('Environment', () => {
  it('should check Python environment', () => {
    const result = checkPythonEnvironment();
    // Result depends on environment, just ensure it doesn't throw
    assert.strictEqual(typeof result, 'boolean');
  });

  it('should have test fixtures directory', () => {
    assert.strictEqual(fs.existsSync(FIXTURES_DIR), true);
  });

  it('should have sample.png in fixtures', () => {
    const samplePath = path.join(FIXTURES_DIR, 'sample.png');
    assert.strictEqual(fs.existsSync(samplePath), true);
  });
});

describe('extractTextMentions', () => {
  it('should extract text from Chinese prompt with quotes', () => {
    const prompt = '生成一张海报，标题写"新春大促"，红色风格';
    const result = extractTextMentions(prompt);
    
    assert.strictEqual(result.length, 1);
    assert.strictEqual(result[0].content, '新春大促');
    assert.strictEqual(result[0].position, 'auto');
  });

  it('should extract text from English prompt', () => {
    const prompt = 'Create a poster with text "Summer Sale" in the center';
    const result = extractTextMentions(prompt);
    
    assert.strictEqual(result.length, 1);
    assert.strictEqual(result[0].content, 'Summer Sale');
  });

  it('should handle multiple text mentions', () => {
    const prompt = '海报标题写"主标题"，副标题写"副标题内容"';
    const result = extractTextMentions(prompt);
    
    // Both should be extracted
    assert.strictEqual(result.length >= 1, true);
  });

  it('should return empty array for prompt without text', () => {
    const prompt = '生成一张风景图片，有山有水';
    const result = extractTextMentions(prompt);
    
    assert.strictEqual(result.length, 0);
  });

  it('should extract flowchart steps', () => {
    const prompt = '创建流程图：1.填写信息 2.验证邮箱 3.完成注册';
    const result = extractTextMentions(prompt);
    
    assert.strictEqual(result.length >= 3, true);
    assert.strictEqual(result[0].semantic_type, 'flowchart_node');
  });

  it('should handle different quote styles', () => {
    const prompt = '标题写"双引号"';
    const result = extractTextMentions(prompt);
    
    // Should extract at least the double-quoted text
    assert.strictEqual(result.length >= 1, true);
  });
});

describe('createImagePrompt', () => {
  it('should create image-only prompt', () => {
    const originalPrompt = '生成海报，标题"测试标题"，红色风格';
    const textItems = [
      { content: '测试标题', position: 'auto', start_idx: 7, end_idx: 17, semantic_type: 'text_block' }
    ];
    
    const result = createImagePrompt(originalPrompt, textItems);
    
    assert.strictEqual(typeof result, 'string');
    assert.strictEqual(result.includes('测试标题'), false);
    assert.strictEqual(result.includes('high quality'), true);
  });

  it('should add quality enhancements', () => {
    const originalPrompt = 'Simple image';
    const textItems = [];
    
    const result = createImagePrompt(originalPrompt, textItems);
    
    assert.strictEqual(result.includes('high quality'), true);
    assert.strictEqual(result.includes('professional'), true);
  });

  it('should not duplicate quality terms', () => {
    const originalPrompt = 'High quality professional image';
    const textItems = [];
    
    const result = createImagePrompt(originalPrompt, textItems);
    
    // Should not add duplicate quality terms
    const qualityCount = (result.match(/high quality/gi) || []).length;
    assert.strictEqual(qualityCount, 1);
  });
});

describe('createTextRequirements', () => {
  it('should create text requirements structure', () => {
    const textItems = [
      { content: '测试文字', position: 'top', semantic_type: 'text_block' }
    ];
    const originalPrompt = '测试提示';
    
    const result = createTextRequirements(textItems, originalPrompt);
    
    assert.strictEqual(result.type, 'single_or_few');
    assert.strictEqual(Array.isArray(result.text_groups), true);
    assert.strictEqual(result.text_groups.length, 1);
    assert.strictEqual(result.text_groups[0].content, '测试文字');
    assert.strictEqual(typeof result.style_hints, 'object');
  });

  it('should detect flowchart type', () => {
    const textItems = [
      { content: '步骤1', position: 'step_1', semantic_type: 'flowchart_node' },
      { content: '步骤2', position: 'step_2', semantic_type: 'flowchart_node' }
    ];
    const originalPrompt = '流程图测试';
    
    const result = createTextRequirements(textItems, originalPrompt);
    
    assert.strictEqual(result.type, 'flowchart');
    assert.strictEqual(result.text_groups.length, 2);
  });
});

describe('extractStyleHints', () => {
  it('should extract color hints', () => {
    const prompt = '红色背景的海报';
    const result = extractStyleHints(prompt);
    
    assert.strictEqual(result.color, 'red');
  });

  it('should extract font style hints', () => {
    const prompt = '使用书法字体';
    const result = extractStyleHints(prompt);
    
    assert.strictEqual(result.font_style, 'calligraphy');
  });

  it('should handle multiple style hints', () => {
    const prompt = '蓝色现代风格';
    const result = extractStyleHints(prompt);
    
    assert.strictEqual(result.color, 'blue');
    assert.strictEqual(result.font_style, 'modern');
  });

  it('should return null for unknown styles', () => {
    const prompt = '普通图片';
    const result = extractStyleHints(prompt);
    
    assert.strictEqual(result.color, null);
    assert.strictEqual(result.font_style, null);
  });
});

describe('separatePromptSync', () => {
  it('should separate prompt with text', () => {
    const prompt = '生成海报，标题写"测试"';
    const result = separatePromptSync(prompt);
    
    assert.strictEqual(result.has_text, true);
    assert.strictEqual(typeof result.image_prompt, 'string');
    assert.strictEqual(typeof result.text_requirements, 'object');
    assert.strictEqual(result.text_requirements.text_groups[0].content, '测试');
  });

  it('should handle prompt without text', () => {
    const prompt = '生成风景图片';
    const result = separatePromptSync(prompt);
    
    assert.strictEqual(result.has_text, false);
    assert.strictEqual(result.image_prompt, prompt);
    assert.strictEqual(result.text_requirements, null);
  });

  it('should throw error for empty prompt', () => {
    assert.throws(() => {
      separatePromptSync('');
    }, /non-empty string/);
  });

  it('should throw error for non-string prompt', () => {
    assert.throws(() => {
      separatePromptSync(null);
    }, /non-empty string/);
  });
});

describe('analyzeImage', () => {
  it('should analyze image and return structure', async () => {
    const imagePath = path.join(FIXTURES_DIR, 'sample.png');
    const textRequirements = {
      type: 'single_or_few',
      text_groups: [{ id: 't1', content: 'Test', semantic_position: 'center' }]
    };
    
    const result = await analyzeImage(imagePath, textRequirements);
    
    assert.strictEqual(typeof result, 'object');
    assert.ok(Array.isArray(result.image_size));
    assert.strictEqual(result.image_size.length, 2);
    assert.strictEqual(typeof result.color_scheme, 'object');
    assert.ok(Array.isArray(result.safe_zones));
    assert.strictEqual(result.safe_zones.length > 0, true);
  });

  it('should throw error for non-existent image', async () => {
    await assert.rejects(async () => {
      await analyzeImage('/nonexistent/path.png', {});
    }, /Image not found/);
  });
});

describe('getTextPlacementSuggestions', () => {
  it('should generate suggestions for single text', () => {
    const analysis = {
      safe_zones: [
        { bbox: [0, 0, 100, 50], position_name: 'top_center', complexity: 10, area: 5000, avg_color: [200, 200, 200] }
      ],
      color_scheme: { suggested_text_color: [30, 30, 30] }
    };
    const textRequirements = {
      type: 'single_or_few',
      text_groups: [{ id: 't1', content: 'Test Text', semantic_position: 'auto' }]
    };
    
    const result = getTextPlacementSuggestions(analysis, textRequirements);
    
    assert.ok(Array.isArray(result));
    assert.strictEqual(result.length, 1);
    assert.strictEqual(result[0].content, 'Test Text');
    assert.ok(Array.isArray(result[0].placement.bbox));
  });

  it('should generate suggestions for flowchart', () => {
    const analysis = {
      detected_nodes: [
        { id: 'node_1', bbox: [0, 0, 100, 50], center: [50, 25] },
        { id: 'node_2', bbox: [100, 0, 200, 50], center: [150, 25] }
      ],
      color_scheme: { suggested_text_color: [30, 30, 30] }
    };
    const textRequirements = {
      type: 'flowchart',
      text_groups: [
        { id: 't1', content: 'Step 1' },
        { id: 't2', content: 'Step 2' }
      ]
    };
    
    const result = getTextPlacementSuggestions(analysis, textRequirements);
    
    assert.ok(Array.isArray(result));
    assert.strictEqual(result.length, 2);
  });

  it('should handle empty requirements', () => {
    const analysis = { safe_zones: [] };
    const textRequirements = { type: 'single_or_few', text_groups: [] };
    
    const result = getTextPlacementSuggestions(analysis, textRequirements);
    
    assert.ok(Array.isArray(result));
    assert.strictEqual(result.length, 0);
  });
});

describe('renderTextOnImage', () => {
  it('should render text and create output file', async () => {
    const imagePath = path.join(FIXTURES_DIR, 'sample.png');
    const outputPath = path.join(OUTPUTS_DIR, 'test-output.png');
    const placements = [
      {
        text_id: 't1',
        content: 'Test',
        placement: { bbox: [50, 50, 200, 100], position_name: 'center', type: 'overlay' },
        style_suggestions: { color: [255, 255, 255], max_width: 150 }
      }
    ];
    
    // Clean up if exists
    if (fs.existsSync(outputPath)) {
      fs.unlinkSync(outputPath);
    }
    
    const result = await renderTextOnImage(imagePath, outputPath, placements, {});
    
    assert.strictEqual(typeof result, 'string');
    assert.strictEqual(fs.existsSync(result), true);
    
    // Clean up
    if (fs.existsSync(outputPath)) {
      fs.unlinkSync(outputPath);
    }
  });

  it('should throw error for non-existent input', async () => {
    await assert.rejects(async () => {
      await renderTextOnImage('/nonexistent.png', 'output.png', [], {});
    }, /Input image not found/);
  });

  it('should create output directory if not exists', async () => {
    const imagePath = path.join(FIXTURES_DIR, 'sample.png');
    const nestedDir = path.join(OUTPUTS_DIR, 'nested', 'dir');
    const outputPath = path.join(nestedDir, 'test.png');
    
    // Clean up
    if (fs.existsSync(nestedDir)) {
      fs.rmSync(nestedDir, { recursive: true });
    }
    
    await renderTextOnImage(imagePath, outputPath, [], {});
    
    assert.strictEqual(fs.existsSync(outputPath), true);
    
    // Clean up
    if (fs.existsSync(nestedDir)) {
      fs.rmSync(nestedDir, { recursive: true });
    }
  });
});

describe('Integration', () => {
  it('should complete full workflow', async () => {
    const prompt = '生成一张促销海报，标题写"夏日大促"，蓝色海洋风格';
    const imagePath = path.join(FIXTURES_DIR, 'sample.png');
    const outputPath = path.join(OUTPUTS_DIR, 'integration-test.png');
    
    // Step 1: Separate prompt
    const separation = separatePromptSync(prompt);
    assert.strictEqual(separation.has_text, true);
    assert.strictEqual(separation.text_requirements.text_groups[0].content, '夏日大促');
    
    // Step 2: Analyze image
    const analysis = await analyzeImage(imagePath, separation.text_requirements);
    assert.ok(analysis.safe_zones.length > 0);
    
    // Step 3: Get placement suggestions
    const suggestions = getTextPlacementSuggestions(analysis, separation.text_requirements);
    assert.ok(suggestions.length > 0);
    
    // Step 4: Render
    if (fs.existsSync(outputPath)) {
      fs.unlinkSync(outputPath);
    }
    
    const result = await renderTextOnImage(imagePath, outputPath, suggestions, {
      font_style: 'modern',
      effects: ['shadow']
    });
    
    assert.strictEqual(fs.existsSync(result), true);
    
    // Clean up
    if (fs.existsSync(outputPath)) {
      fs.unlinkSync(outputPath);
    }
  });
});

// Run tests if this file is executed directly
if (require.main === module) {
  console.log('Running tests...\n');
}

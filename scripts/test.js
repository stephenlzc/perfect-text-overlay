#!/usr/bin/env node
/**
 * Perfect Text Overlay - Test Script
 */

const { separatePrompt, checkDependencies } = require('../lib/index');

async function runTests() {
  console.log('Running tests...\n');

  // Test 1: Check dependencies
  console.log('Test 1: Checking dependencies...');
  const deps = await checkDependencies();
  if (deps.python) {
    console.log('  ✓ Python is available');
  } else {
    console.log('  ✗ Python not found');
  }

  // Test 2: Separate prompt
  console.log('\nTest 2: Testing prompt separation...');
  try {
    const result = await separatePrompt('创建一个标题为"Hello World"的海报');
    if (result.has_text && result.text_requirements) {
      console.log('  ✓ Prompt separation works');
      console.log(`  Found ${result.text_requirements.text_groups?.length || 0} text group(s)`);
    } else {
      console.log('  ⚠ No text detected (might be expected)');
    }
  } catch (error) {
    console.log(`  ✗ Error: ${error.message}`);
  }

  console.log('\nTests complete!');
}

runTests().catch(console.error);

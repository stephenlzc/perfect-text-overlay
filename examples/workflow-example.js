/**
 * Perfect Text Overlay - Complete Workflow Example
 * =================================================
 * 
 * This example demonstrates the complete workflow from user prompt to final image.
 * It shows how to integrate all three main APIs in a real-world scenario.
 * 
 * Workflow:
 * 1. Separate user prompt into image prompt and text requirements
 * 2. Generate base image (external tool)
 * 3. Analyze image for optimal text placement
 * 4. Collect user customization choices
 * 5. Render final image with text overlay
 */

const fs = require('fs');
const path = require('path');
const { 
  separatePrompt,
  analyzeImage,
  getTextPlacementSuggestions,
  renderTextOnImage
} = require('perfect-text-overlay');

// Configuration
const CONFIG = {
  outputDir: './outputs',
  tempDir: './temp',
  defaultFontStyle: 'modern',
  defaultEffects: ['shadow', 'outline']
};

/**
 * Ensure output directories exist
 */
function ensureDirectories() {
  [CONFIG.outputDir, CONFIG.tempDir].forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });
}

/**
 * Step 1: Separate Prompt
 * Extract text requirements from user input
 * 
 * @param {string} userInput - Raw user prompt
 * @returns {Object} Separated prompt data
 */
function step1_separatePrompt(userInput) {
  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('STEP 1: Separate Prompt');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  
  console.log('\n📝 User Input:');
  console.log(`   "${userInput}"`);
  
  const result = separatePrompt(userInput);
  
  console.log('\n✅ Separation Result:');
  console.log(`   Has Text: ${result.has_text}`);
  console.log(`   Image Prompt: "${result.image_prompt.substring(0, 80)}..."`);
  console.log(`   Text Groups: ${result.text_requirements.text_groups.length}`);
  
  result.text_requirements.text_groups.forEach((group, i) => {
    console.log(`   [${i + 1}] "${group.content}" (${group.semantic_position})`);
  });
  
  // Save intermediate result
  const tempFile = path.join(CONFIG.tempDir, 'step1_result.json');
  fs.writeFileSync(tempFile, JSON.stringify(result, null, 2));
  console.log(`\n💾 Saved to: ${tempFile}`);
  
  return result;
}

/**
 * Step 2: Generate Base Image
 * This is an external step - user generates image using their preferred tool
 * 
 * @param {string} imagePrompt - Clean image prompt without text
 * @returns {string} Path to generated base image
 */
async function step2_generateBaseImage(imagePrompt) {
  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('STEP 2: Generate Base Image (External)');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  
  console.log('\n🎨 Image Prompt for Generation:');
  console.log(`   "${imagePrompt}"`);
  
  console.log('\n⚠️  NOTE: This step requires an external image generator.');
  console.log('   Examples: DALL-E, Midjourney, Stable Diffusion, etc.');
  console.log('\n   In a real application, you would:');
  console.log('   1. Call your image generation API');
  console.log('   2. Wait for the image to be generated');
  console.log('   3. Save the image to a known location');
  
  // For this example, we assume the image already exists
  // In production, integrate with your image generation service
  const baseImagePath = path.join(CONFIG.outputDir, 'base_image.png');
  
  // Simulating external generation
  console.log(`\n⏳ Simulating image generation...`);
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  console.log(`\n✅ Base image would be saved to: ${baseImagePath}`);
  
  return baseImagePath;
}

/**
 * Step 3: Analyze Image
 * Find safe zones for text placement
 * 
 * @param {string} imagePath - Path to base image
 * @param {Object} textRequirements - Text requirements from step 1
 * @returns {Array} Text placement suggestions
 */
function step3_analyzeImage(imagePath, textRequirements) {
  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('STEP 3: Analyze Image');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  
  console.log(`\n🔍 Analyzing image: ${imagePath}`);
  
  // Analyze image for safe zones
  const analysis = analyzeImage(imagePath, textRequirements);
  
  console.log('\n📊 Analysis Results:');
  console.log(`   Safe Zones: ${analysis.safe_zones.length}`);
  console.log(`   Color Palette: ${analysis.color_palette.length} dominant colors`);
  
  // Get placement suggestions
  const placements = getTextPlacementSuggestions(analysis, textRequirements);
  
  console.log('\n📍 Suggested Placements:');
  placements.forEach((placement, i) => {
    console.log(`   [${i + 1}] "${placement.text}"`);
    console.log(`       Position: (${placement.x}, ${placement.y})`);
    console.log(`       Size: ${placement.width}x${placement.height}`);
    console.log(`       Suggested Color: RGB(${placement.suggested_color.join(', ')})`);
  });
  
  // Save intermediate result
  const tempFile = path.join(CONFIG.tempDir, 'step3_placements.json');
  fs.writeFileSync(tempFile, JSON.stringify(placements, null, 2));
  console.log(`\n💾 Saved to: ${tempFile}`);
  
  return placements;
}

/**
 * Step 4: Collect User Choices
 * In a real app, this would be a UI. For this example, we use predefined choices.
 * 
 * @param {Array} placements - Text placements
 * @returns {Object} User customization choices
 */
function step4_collectUserChoices(placements) {
  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('STEP 4: User Customization');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  
  console.log('\n🎛️  Collecting user preferences...');
  
  // In a real application, these would come from user input via UI
  const userChoices = {
    // Question 1: Scene Type
    scene_type: 'poster',  // 'poster', 'flowchart', 'infographic', 'diagram'
    
    // Question 2: Text Content (already confirmed via placements)
    text_confirmed: true,
    
    // Question 3: Font Style
    font_style: 'modern',  // 'modern', 'traditional', 'traditional_tw', 'korean', 'english', 'cartoon', 'calligraphy'
    
    // Question 4: Text Position
    text_position: 'auto',  // 'top', 'bottom', 'center', 'auto', or custom
    
    // Question 5: Effects
    effects: ['shadow', 'outline'],  // Array of effects
    
    // Additional options
    text_color: null,  // null = auto-detect, or [R, G, B] array
    text_size: 'auto',  // 'auto' or number in pixels
    show_connections: false,  // For flowcharts
    background_opacity: 180  // 0-255
  };
  
  console.log('\n✅ User Choices:');
  console.log(`   Scene Type: ${userChoices.scene_type}`);
  console.log(`   Font Style: ${userChoices.font_style}`);
  console.log(`   Effects: ${userChoices.effects.join(', ')}`);
  console.log(`   Position: ${userChoices.text_position}`);
  
  return userChoices;
}

/**
 * Step 5: Render Final Image
 * Apply text overlay to base image
 * 
 * @param {string} baseImagePath - Path to base image
 * @param {Array} placements - Text placements
 * @param {Object} userChoices - User customization choices
 * @returns {string} Path to final image
 */
function step5_renderFinalImage(baseImagePath, placements, userChoices) {
  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('STEP 5: Render Final Image');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  
  console.log('\n🖌️  Rendering text overlay...');
  
  const outputPath = path.join(CONFIG.outputDir, 'final_image.png');
  
  const result = renderTextOnImage({
    image_path: baseImagePath,
    output_path: outputPath,
    placements: placements,
    user_choices: userChoices
  });
  
  console.log('\n✅ Render Complete!');
  console.log(`   Output: ${result}`);
  console.log(`   Text Elements: ${placements.length}`);
  console.log(`   Font: ${userChoices.font_style}`);
  console.log(`   Effects: ${userChoices.effects.join(', ')}`);
  
  return result;
}

/**
 * Main Workflow Function
 * Orchestrates all steps from prompt to final image
 * 
 * @param {string} userInput - User's original prompt
 */
async function processWorkflow(userInput) {
  console.log('\n');
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║     PERFECT TEXT OVERLAY - COMPLETE WORKFLOW              ║');
  console.log('╚════════════════════════════════════════════════════════════╝');
  
  const startTime = Date.now();
  
  try {
    // Ensure directories exist
    ensureDirectories();
    
    // Step 1: Separate prompt
    const separated = step1_separatePrompt(userInput);
    
    if (!separated.has_text) {
      console.log('\n⚠️  No text detected in prompt. Skipping text overlay.');
      return;
    }
    
    // Step 2: Generate base image (external)
    const baseImagePath = await step2_generateBaseImage(separated.image_prompt);
    
    // Check if base image exists
    if (!fs.existsSync(baseImagePath)) {
      console.log('\n⚠️  Base image not found. Please generate it first.');
      console.log('   In production, this would be generated by your image API.');
      return;
    }
    
    // Step 3: Analyze image
    const placements = step3_analyzeImage(baseImagePath, separated.text_requirements);
    
    // Step 4: Collect user choices
    const userChoices = step4_collectUserChoices(placements);
    
    // Step 5: Render final image
    const finalPath = step5_renderFinalImage(baseImagePath, placements, userChoices);
    
    // Summary
    const duration = Date.now() - startTime;
    console.log('\n');
    console.log('╔════════════════════════════════════════════════════════════╗');
    console.log('║                    WORKFLOW COMPLETE                       ║');
    console.log('╠════════════════════════════════════════════════════════════╣');
    console.log(`║  Input:  "${userInput.substring(0, 40)}${userInput.length > 40 ? '...' : ''}"`);
    console.log(`║  Output: ${finalPath}`);
    console.log(`║  Time:   ${duration}ms`);
    console.log('╚════════════════════════════════════════════════════════════╝');
    
    return {
      input: userInput,
      output: finalPath,
      duration: duration,
      textElements: placements.length
    };
    
  } catch (error) {
    console.error('\n❌ Workflow Error:', error.message);
    console.error(error.stack);
    throw error;
  }
}

/**
 * Example: Chinese Poster
 */
async function exampleChinesePoster() {
  console.log('\n\n═══════════════════════════════════════════════════════════════');
  console.log('EXAMPLE 1: Chinese New Year Poster');
  console.log('═══════════════════════════════════════════════════════════════');
  
  const userInput = "生成一张春节促销海报，标题写'新春大促，全场5折起'，要有红色的喜庆氛围";
  
  await processWorkflow(userInput);
}

/**
 * Example: English Movie Poster
 */
async function exampleMoviePoster() {
  console.log('\n\n═══════════════════════════════════════════════════════════════');
  console.log('EXAMPLE 2: Movie Poster');
  console.log('═══════════════════════════════════════════════════════════════');
  
  const userInput = "Create a sci-fi movie poster with title 'Interstellar', space theme";
  
  await processWorkflow(userInput);
}

/**
 * Example: Flowchart
 */
async function exampleFlowchart() {
  console.log('\n\n═══════════════════════════════════════════════════════════════');
  console.log('EXAMPLE 3: User Registration Flowchart');
  console.log('═══════════════════════════════════════════════════════════════');
  
  const userInput = "Create a user registration flowchart: 1. Fill info 2. Verify email 3. Complete";
  
  // Override step 4 for flowchart-specific options
  const originalStep4 = step4_collectUserChoices;
  step4_collectUserChoices = function(placements) {
    const choices = originalStep4(placements);
    choices.scene_type = 'flowchart';
    choices.effects = ['border', 'arrows'];
    choices.show_connections = true;
    return choices;
  };
  
  await processWorkflow(userInput);
}

/**
 * Run all examples
 */
async function runAllExamples() {
  await exampleChinesePoster();
  await exampleMoviePoster();
  await exampleFlowchart();
  
  console.log('\n\n');
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║                  ALL EXAMPLES COMPLETE                     ║');
  console.log('╚════════════════════════════════════════════════════════════╝');
}

// Run if called directly
if (require.main === module) {
  // Run with a single example by default
  const exampleInput = process.argv[2] || "Create a poster with title 'Hello World'";
  
  processWorkflow(exampleInput).catch(console.error);
  
  // Uncomment to run all examples:
  // runAllExamples().catch(console.error);
}

// Export for use in other files
module.exports = {
  processWorkflow,
  exampleChinesePoster,
  exampleMoviePoster,
  exampleFlowchart,
  runAllExamples
};

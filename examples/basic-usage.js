/**
 * Perfect Text Overlay - Basic Usage Example
 * ===========================================
 * 
 * This example demonstrates the core API usage:
 * - separatePrompt: Extract text requirements from user prompts
 * - analyzeImage: Analyze image for safe text placement zones
 * - renderTextOnImage: Render text with professional typography
 */

const { 
  separatePrompt, 
  analyzeImage, 
  getTextPlacementSuggestions,
  renderTextOnImage 
} = require('perfect-text-overlay');

// ============================================================
// Example 1: Separate Prompt - Extract text from user input
// ============================================================

async function example1_separatePrompt() {
  console.log('\n=== Example 1: Separate Prompt ===\n');
  
  // User input with text requirements
  const userInput = "生成一张春节促销海报，标题写'新春大促，全场5折起'，要有红色的喜庆氛围";
  
  // Extract text requirements
  const result = separatePrompt(userInput);
  
  console.log('Original input:', userInput);
  console.log('\n--- Result ---');
  console.log('Has text:', result.has_text);
  console.log('Image prompt:', result.image_prompt);
  console.log('Text requirements:', JSON.stringify(result.text_requirements, null, 2));
  
  // Expected output:
  // {
  //   has_text: true,
  //   image_prompt: "A festive Chinese New Year promotional poster, vibrant red and gold color scheme...",
  //   text_requirements: {
  //     type: "single_or_few",
  //     text_groups: [{
  //       id: "text_1",
  //       content: "新春大促，全场5折起",
  //       semantic_position: "auto"
  //     }]
  //   }
  // }
  
  return result;
}

// ============================================================
// Example 2: Analyze Image - Find safe text placement zones
// ============================================================

async function example2_analyzeImage() {
  console.log('\n=== Example 2: Analyze Image ===\n');
  
  // Text requirements from step 1
  const textRequirements = {
    type: "single_or_few",
    text_groups: [{
      id: "text_1",
      content: "新春大促，全场5折起",
      semantic_position: "auto"
    }]
  };
  
  // Analyze the generated image
  // Note: This assumes you have already generated a base image
  const analysis = analyzeImage("./outputs/base_image.png", textRequirements);
  
  console.log('Image analysis complete!');
  console.log('Safe zones found:', analysis.safe_zones.length);
  console.log('Color palette:', analysis.color_palette);
  
  // Get text placement suggestions
  const placements = getTextPlacementSuggestions(analysis, textRequirements);
  
  console.log('\n--- Placement Suggestions ---');
  placements.forEach((placement, index) => {
    console.log(`Text ${index + 1}:`, {
      content: placement.text,
      position: `(${placement.x}, ${placement.y})`,
      size: `${placement.width}x${placement.height}`,
      suggested_color: placement.suggested_color
    });
  });
  
  return placements;
}

// ============================================================
// Example 3: Render Text - Add text to image
// ============================================================

async function example3_renderText() {
  console.log('\n=== Example 3: Render Text on Image ===\n');
  
  // Placement data from step 2
  const placements = [
    {
      id: "text_1",
      text: "新春大促，全场5折起",
      x: 400,
      y: 800,
      width: 800,
      height: 100,
      suggested_color: [255, 215, 0],  // Gold color
      font_size: 72
    }
  ];
  
  // User customization choices
  const userChoices = {
    // Font style options:
    // - 'modern': Clean sans-serif (Noto Sans CJK SC)
    // - 'traditional': Serif style (Noto Serif CJK SC)
    // - 'traditional_tw': Traditional Chinese (Noto Sans CJK TC)
    // - 'korean': Korean font (Noto Sans CJK KR)
    // - 'english': Latin font (Roboto)
    // - 'cartoon': Playful style
    // - 'calligraphy': Handwritten style
    font_style: "modern",
    
    // Text size: 'auto' or specific size in pixels
    text_size: "auto",
    
    // Text color: RGB array or null for auto-detection
    text_color: [255, 215, 0],  // Gold
    
    // Effects array: 'shadow', 'outline', 'background_box', 'border', 'arrows'
    effects: ["shadow", "outline"],
    
    // For flowcharts: show connection arrows between nodes
    show_connections: false,
    
    // Background box opacity (0-255)
    background_opacity: 180
  };
  
  // Render text on image
  const outputPath = renderTextOnImage({
    image_path: "./outputs/base_image.png",
    output_path: "./outputs/final_image.png",
    placements: placements,
    user_choices: userChoices
  });
  
  console.log('Text rendered successfully!');
  console.log('Output saved to:', outputPath);
  
  return outputPath;
}

// ============================================================
// Example 4: Complete Single Text Overlay
// ============================================================

async function example4_completeSingle() {
  console.log('\n=== Example 4: Complete Single Text Overlay ===\n');
  
  const userInput = "Create a sci-fi movie poster with title 'Interstellar'";
  
  // Step 1: Separate prompt
  const separated = separatePrompt(userInput);
  console.log('Step 1 - Image prompt:', separated.image_prompt);
  
  // Step 2: [External] Generate base image using separated.image_prompt
  // const baseImage = await generateImage(separated.image_prompt);
  console.log('Step 2 - Generate base image (external)');
  
  // Step 3: Analyze image
  const analysis = analyzeImage("./outputs/base_image.png", separated.text_requirements);
  const placements = getTextPlacementSuggestions(analysis, separated.text_requirements);
  
  // Step 4: Render
  const outputPath = renderTextOnImage({
    image_path: "./outputs/base_image.png",
    output_path: "./outputs/interstellar_poster.png",
    placements: placements,
    user_choices: {
      font_style: "english",
      effects: ["shadow", "outline"],
      text_color: [255, 255, 255]
    }
  });
  
  console.log('Complete! Output:', outputPath);
}

// ============================================================
// Example 5: Flowchart with Multiple Text Elements
// ============================================================

async function example5_flowchart() {
  console.log('\n=== Example 5: Flowchart Example ===\n');
  
  const userInput = "Create a user registration flowchart: 1. Fill info 2. Verify email 3. Complete";
  
  // Step 1: Separate prompt
  const separated = separatePrompt(userInput);
  console.log('Detected flowchart nodes:', 
    separated.text_requirements.text_groups.length);
  
  // Step 2 & 3: Analyze image
  const analysis = analyzeImage("./outputs/flowchart_base.png", separated.text_requirements);
  const placements = getTextPlacementSuggestions(analysis, separated.text_requirements);
  
  // Step 4: Render with flowchart-specific options
  const outputPath = renderTextOnImage({
    image_path: "./outputs/flowchart_base.png",
    output_path: "./outputs/flowchart_final.png",
    placements: placements,
    user_choices: {
      font_style: "modern",
      effects: ["border", "background_box"],
      show_connections: true,  // Add arrows between nodes
      text_color: [50, 50, 50]
    }
  });
  
  console.log('Flowchart created! Output:', outputPath);
}

// ============================================================
// Run all examples
// ============================================================

async function runAll() {
  try {
    await example1_separatePrompt();
    await example2_analyzeImage();
    await example3_renderText();
    await example4_completeSingle();
    await example5_flowchart();
    
    console.log('\n✅ All examples completed!\n');
  } catch (error) {
    console.error('\n❌ Error:', error.message);
    console.error('Note: Some examples require existing image files.');
  }
}

// Run if called directly
if (require.main === module) {
  runAll();
}

// Export for use in other files
module.exports = {
  example1_separatePrompt,
  example2_analyzeImage,
  example3_renderText,
  example4_completeSingle,
  example5_flowchart
};

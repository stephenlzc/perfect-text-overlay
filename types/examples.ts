/**
 * Perfect Text Overlay - TypeScript Usage Examples
 * 
 * This file demonstrates how to use the TypeScript types in your project.
 */

import {
  // Core functions
  separatePrompt,
  analyzeImage,
  renderTextOnImage,
  createWorkflow,
  
  // Types
  PromptSeparationResult,
  TextRequirements,
  ImageAnalysis,
  Placement,
  UserChoices,
  WorkflowOptions,
  Workflow,
  
  // Enums/Literals
  FontStyle,
  TextEffect,
  SceneType,
} from './index';

// =============================================================================
// Example 1: Basic Workflow
// =============================================================================

async function basicExample() {
  // Step 1: Separate the prompt
  const userPrompt = "生成一张春节促销海报，标题写'新春大促，全场5折起'，要有红色的喜庆氛围";
  
  const separation: PromptSeparationResult = separatePrompt(userPrompt);
  
  if (!separation.has_text) {
    console.log('No text detected, generate image normally');
    return;
  }
  
  console.log('Image Prompt:', separation.image_prompt);
  console.log('Text Requirements:', separation.text_requirements);
  
  // Step 2: Analyze the generated image
  const imagePath = '/path/to/generated_image.png';
  const analysis: ImageAnalysis = analyzeImage(
    imagePath,
    separation.text_requirements!
  );
  
  console.log('Image Size:', analysis.image_size);
  console.log('Color Scheme:', analysis.color_scheme);
  console.log('Safe Zones:', analysis.safe_zones);
  
  // Step 3: Prepare placements (from analysis)
  const placements: Placement[] = [
    {
      text_id: 'text_1',
      content: '新春大促，全场5折起',
      placement: {
        bbox: [100, 50, 700, 150],
        position_name: 'top_center',
        type: 'overlay',
      },
      style_suggestions: {
        color: [255, 215, 0], // Gold color
        max_width: 600,
      },
      is_title: true,
    },
  ];
  
  // Step 4: User choices
  const userChoices: UserChoices = {
    font_style: 'traditional',    // 思源宋体
    text_size: 'large',
    effects: ['shadow', 'outline'],
    text_color: '#FFD700',        // Gold
    shadow_offset: [3, 3],
    stroke_width: 2,
  };
  
  // Step 5: Render
  const outputPath = renderTextOnImage(
    imagePath,
    '/path/to/output.png',
    placements,
    userChoices
  );
  
  console.log('Output saved to:', outputPath);
}

// =============================================================================
// Example 2: Flowchart Workflow
// =============================================================================

async function flowchartExample() {
  const userPrompt = "创建一个用户注册流程图，包含：1.填写信息 2.验证邮箱 3.完成注册";
  
  const separation = separatePrompt(userPrompt);
  
  if (separation.text_requirements?.type === 'flowchart') {
    const analysis = analyzeImage('/path/to/flowchart_base.png', separation.text_requirements);
    
    // Flowcharts have detected nodes
    console.log('Detected Nodes:', analysis.detected_nodes);
    console.log('Suggested Connections:', analysis.suggested_connections);
    
    const placements: Placement[] = analysis.detected_nodes?.map((node, i) => ({
      text_id: `text_${i + 1}`,
      content: separation.text_requirements!.text_groups[i]?.content || '',
      placement: {
        bbox: node.bbox,
        center: node.center,
        type: 'centered_in_box',
      },
      style_suggestions: {
        color: analysis.color_scheme.suggested_text_color,
        max_width: node.bbox[2] - node.bbox[0] - 20,
      },
    })) || [];
    
    const userChoices: UserChoices = {
      font_style: 'modern',
      text_size: 'auto',
      effects: ['box'],
      show_connections: true,
      connections: analysis.suggested_connections,
      line_color: [100, 100, 100],
      line_width: 3,
    };
    
    renderTextOnImage(
      '/path/to/flowchart_base.png',
      '/path/to/flowchart_final.png',
      placements,
      userChoices
    );
  }
}

// =============================================================================
// Example 3: Using the Workflow API
// =============================================================================

async function workflowExample() {
  const options: WorkflowOptions = {
    imagePath: '/path/to/base_image.png',
    outputPath: '/path/to/final.png',
    prompt: "生成一张科技海报，标题'AI的未来'",
    sceneType: 'poster',
    defaultChoices: {
      font_style: 'modern',
      text_size: 'large',
      effects: ['shadow'],
    },
    onStepComplete: (step, result) => {
      console.log(`Step completed: ${step}`, result);
    },
    onError: (error, step) => {
      console.error(`Error in ${step}:`, error);
    },
  };
  
  const workflow: Workflow = createWorkflow(options);
  
  // Execute full workflow
  try {
    const result = await workflow.execute();
    console.log('Workflow completed:', result);
  } catch (error) {
    console.error('Workflow failed:', error);
  }
}

// =============================================================================
// Example 4: Type-Safe User Choices
// =============================================================================

function createPosterChoices(): UserChoices {
  const fontStyle: FontStyle = 'modern'; // Type-safe selection
  const effects: TextEffect[] = ['shadow', 'outline'];
  
  return {
    font_style: fontStyle,
    text_size: 'large',
    effects,
    text_color: [255, 255, 255], // RGB tuple
    shadow_offset: [2, 2],
    stroke_width: 3,
  };
}

// =============================================================================
// Example 5: Scene Type Selection
// =============================================================================

function getSceneTypeDescription(sceneType: SceneType): string {
  const descriptions: Record<SceneType, string> = {
    poster: '海报/封面（单组/少量文字，强调视觉）',
    flowchart: '流程图/步骤图（多组文字，强调逻辑顺序）',
    infographic: '信息图/数据图（多组文字，强调信息呈现）',
    diagram: '示意图/标注图（多组文字，强调说明）',
    other: '其他自定义类型',
  };
  
  return descriptions[sceneType];
}

// =============================================================================
// Export examples for testing
// =============================================================================

export {
  basicExample,
  flowchartExample,
  workflowExample,
  createPosterChoices,
  getSceneTypeDescription,
};

/**
 * Perfect Text Overlay - TypeScript Type Definitions
 * 
 * A TypeScript library for fixing imperfect AI-generated text in images
 * by separating image generation and text overlay into two distinct steps.
 */

// ============================================================================
// Enums and Literal Types
// ============================================================================

/** Type of text content in the image */
export type TextRequirementsType = 'single_or_few' | 'flowchart';

/** Semantic position hints for text placement */
export type SemanticPosition = 
  | 'auto' 
  | 'top' 
  | 'bottom' 
  | 'center' 
  | 'left' 
  | 'right'
  | 'top_left'
  | 'top_right'
  | 'bottom_left'
  | 'bottom_right';

/** Font style options */
export type FontStyle = 
  | 'modern'           // 思源黑体 - for tech/business
  | 'traditional'      // 思源宋体 - for Chinese culture
  | 'traditional_tw'   // 思源黑体繁体 - for Traditional Chinese (Taiwan)
  | 'calligraphy'      // 书法/手写风格
  | 'cartoon'          // 卡通/可爱风格
  | 'english'          // Roboto/Open Sans - for English/Latin
  | 'korean'           // Noto Sans CJK KR - for Korean
  | 'default'          // Auto fallback
  | string;            // Custom font path

/** Text size preferences */
export type TextSize = 'auto' | 'large' | 'small';

/** Text effect options */
export type TextEffect = 
  | 'shadow'           // Add shadow for 3D effect
  | 'outline'          // Add stroke for readability
  | 'stroke'           // Alias for outline
  | 'box'              // Background box
  | 'arrow'            // Connection arrows for flowcharts
  | 'none';            // No special effects

/** Color family classification */
export type ColorFamily = 'warm' | 'cool' | 'neutral';

/** Background brightness classification */
export type BackgroundType = 'light' | 'dark';

/** Flowchart node types */
export type NodeType = 'box' | 'diamond' | 'circle';

/** Connection/arrow types */
export type ConnectionType = 'arrow' | 'line' | 'dashed';

/** Placement type for text positioning */
export type PlacementType = 
  | 'overlay'          // Direct overlay on image
  | 'centered_in_box'  // Center within a bounding box
  | 'top'              // Aligned to top
  | 'bottom'           // Aligned to bottom
  | 'left'             // Aligned to left
  | 'right';           // Aligned to right

/** Scene type for workflow */
export type SceneType = 
  | 'poster'           // 海报/封面
  | 'flowchart'        // 流程图/步骤图
  | 'infographic'      // 信息图/数据图
  | 'diagram'          // 示意图/标注图
  | 'other';           // 其他

// ============================================================================
// Core Data Types
// ============================================================================

/** RGB Color tuple */
export type RGBColor = [number, number, number];

/** RGBA Color tuple */
export type RGBAColor = [number, number, number, number];

/** Image size as [width, height] */
export type ImageSize = [number, number];

/** Bounding box as [x1, y1, x2, y2] */
export type BoundingBox = [number, number, number, number];

/** Point coordinates as [x, y] */
export type Point = [number, number];

// ============================================================================
// Text Requirements Types
// ============================================================================

/** Represents a single extracted text item from the prompt */
export interface TextItem {
  /** The text content */
  content: string;
  /** Semantic position hint */
  position: SemanticPosition;
  /** Start index in original prompt */
  start_idx: number;
  /** End index in original prompt */
  end_idx: number;
  /** Optional semantic type classification */
  semantic_type?: 'text_block' | 'flowchart_node' | string;
}

/** Style hints extracted from the prompt */
export interface StyleHints {
  /** Suggested text color */
  color: string | null;
  /** Suggested font style */
  font_style: FontStyle | null;
  /** Suggested text size */
  size: TextSize | null;
}

/** A group of related text for placement */
export interface TextGroup {
  /** Unique identifier for the text group */
  id: string;
  /** The text content to display */
  content: string;
  /** Semantic position hint */
  semantic_position: SemanticPosition;
  /** Type of node (for flowcharts) */
  node_type?: 'text_block' | 'flowchart_node' | string;
}

/** Structured text requirements extracted from user prompt */
export interface TextRequirements {
  /** Type of text content */
  type: TextRequirementsType;
  /** Array of text groups to place */
  text_groups: TextGroup[];
  /** Style hints from prompt analysis */
  style_hints: StyleHints;
}

// ============================================================================
// Image Analysis Types
// ============================================================================

/** Color scheme analysis result */
export interface ColorScheme {
  /** Dominant RGB color */
  dominant_rgb: RGBColor;
  /** Average brightness (0-255) */
  brightness: number;
  /** Color family classification */
  color_family: ColorFamily;
  /** Suggested text color for contrast */
  suggested_text_color: RGBColor;
  /** Background brightness type */
  suggested_bg: BackgroundType;
}

/** Safe zone for text placement */
export interface SafeZone {
  /** Bounding box [x1, y1, x2, y2] */
  bbox: BoundingBox;
  /** Position name (e.g., 'top_center', 'bottom_left') */
  position_name: string;
  /** Visual complexity score (lower is better for text) */
  complexity: number;
  /** Area in pixels */
  area: number;
  /** Average color in the zone */
  avg_color: RGBColor;
}

/** Flowchart node detection result */
export interface Node {
  /** Unique node identifier */
  id: string;
  /** Bounding box [x1, y1, x2, y2] */
  bbox: BoundingBox;
  /** Center point [x, y] */
  center: Point;
  /** Node shape type */
  type: NodeType;
}

/** Connection between flowchart nodes */
export interface Connection {
  /** Source node ID */
  from: string;
  /** Target node ID */
  to: string;
  /** Start point coordinates */
  start_point: Point;
  /** End point coordinates */
  end_point: Point;
  /** Connection type */
  type: ConnectionType;
}

/** Complete image analysis result */
export interface ImageAnalysis {
  /** Image dimensions [width, height] */
  image_size: ImageSize;
  /** Color scheme analysis */
  color_scheme: ColorScheme;
  /** Safe zones for text placement */
  safe_zones: SafeZone[];
  /** Complexity heatmap (numpy array) */
  complexity_map: any;
  /** Detected flowchart nodes (if applicable) */
  detected_nodes?: Node[];
  /** Suggested connections between nodes (if applicable) */
  suggested_connections?: Connection[];
}

// ============================================================================
// Text Placement Types
// ============================================================================

/** Placement configuration for a single text element */
export interface PlacementConfig {
  /** Bounding box for text placement */
  bbox: BoundingBox;
  /** Center point for alignment */
  center?: Point;
  /** Position name */
  position_name?: string;
  /** Placement type */
  type: PlacementType;
}

/** Style suggestions from image analysis */
export interface StyleSuggestions {
  /** Suggested text color */
  color: RGBColor;
  /** Background color for contrast reference */
  contrast_bg?: RGBColor;
  /** Maximum width for text wrapping */
  max_width?: number;
}

/** Complete placement suggestion for a text group */
export interface Placement {
  /** Reference to text group ID */
  text_id: string;
  /** Text content to render */
  content: string;
  /** Placement configuration */
  placement: PlacementConfig;
  /** Style suggestions */
  style_suggestions: StyleSuggestions;
  /** Whether this is a title (affects size) */
  is_title?: boolean;
}

// ============================================================================
// User Choices Types
// ============================================================================

/** User customization choices */
export interface UserChoices {
  /** Font style selection */
  font_style?: FontStyle;
  /** Text size preference */
  text_size?: TextSize;
  /** Text effects to apply */
  effects?: TextEffect[];
  /** Specific text color (overrides suggestions) */
  text_color?: RGBColor | string;
  /** Whether to show connections (for flowcharts) */
  show_connections?: boolean;
  /** Connection definitions (if show_connections is true) */
  connections?: Connection[];
  /** Shadow offset [x, y] */
  shadow_offset?: Point;
  /** Stroke/outline width */
  stroke_width?: number;
  /** Whether to add background boxes */
  add_boxes?: boolean;
  /** Box color (with optional alpha) */
  box_color?: RGBAColor | string;
  /** Line color for connections */
  line_color?: RGBColor | string;
  /** Line width for connections */
  line_width?: number;
  /** Custom font path */
  font_path?: string;
}

// ============================================================================
// Prompt Separation Types
// ============================================================================

/** Result of prompt separation */
export interface PromptSeparationResult {
  /** Whether any text was detected in the prompt */
  has_text: boolean;
  /** Clean image-only prompt (no text descriptions) */
  image_prompt: string;
  /** Structured text requirements (null if no text) */
  text_requirements: TextRequirements | null;
  /** Original extracted text items */
  original_text_items?: TextItem[];
}

// ============================================================================
// Workflow Types
// ============================================================================

/** Options for creating a workflow */
export interface WorkflowOptions {
  /** Input image path */
  imagePath: string;
  /** Output image path */
  outputPath: string;
  /** Original user prompt */
  prompt: string;
  /** Scene type */
  sceneType?: SceneType;
  /** Custom scene description */
  sceneDescription?: string;
  /** Whether to auto-confirm text content */
  autoConfirmText?: boolean;
  /** Default user choices */
  defaultChoices?: Partial<UserChoices>;
  /** Callback for step completion */
  onStepComplete?: (step: string, result: any) => void;
  /** Callback for errors */
  onError?: (error: Error, step: string) => void;
}

/** Workflow state */
export interface WorkflowState {
  /** Current step in the workflow */
  currentStep: 'idle' | 'separating' | 'analyzing' | 'confirming' | 'rendering' | 'complete' | 'error';
  /** Original prompt */
  prompt: string;
  /** Separated image prompt */
  imagePrompt?: string;
  /** Text requirements */
  textRequirements?: TextRequirements;
  /** Image analysis result */
  analysis?: ImageAnalysis;
  /** Text placements */
  placements?: Placement[];
  /** User choices */
  userChoices?: UserChoices;
  /** Final output path */
  outputPath?: string;
  /** Error message if failed */
  error?: string;
}

/** Workflow interface */
export interface Workflow {
  /** Workflow options */
  options: WorkflowOptions;
  /** Current workflow state */
  state: WorkflowState;
  /** Execute the complete workflow */
  execute: () => Promise<string>;
  /** Execute a single step */
  executeStep: (step: string) => Promise<any>;
  /** Update user choices */
  setUserChoices: (choices: UserChoices) => void;
  /** Get current placements */
  getPlacements: () => Placement[] | undefined;
  /** Cancel the workflow */
  cancel: () => void;
}

// ============================================================================
// Configuration Types
// ============================================================================

/** Library configuration options */
export interface Config {
  /** Default font style */
  defaultFontStyle?: FontStyle;
  /** Default text size */
  defaultTextSize?: TextSize;
  /** Default effects */
  defaultEffects?: TextEffect[];
  /** Assets directory path */
  assetsDir?: string;
  /** Font directory path */
  fontsDir?: string;
  /** Output directory */
  outputDir?: string;
  /** Quality setting (1-100) */
  quality?: number;
  /** Enable debug logging */
  debug?: boolean;
}

// ============================================================================
// Function Declarations
// ============================================================================

/**
 * Separate user prompt into image-only prompt and text requirements.
 * 
 * @param prompt - The user's original prompt string
 * @returns Object containing image prompt and text requirements
 */
export function separatePrompt(prompt: string): PromptSeparationResult;

/**
 * Analyze image to find suitable text placement zones.
 * 
 * @param imagePath - Path to the input image file
 * @param textRequirements - Structured text requirements
 * @returns Image analysis results including safe zones and color scheme
 */
export function analyzeImage(
  imagePath: string, 
  textRequirements: TextRequirements
): ImageAnalysis;

/**
 * Get text placement suggestions based on image analysis.
 * 
 * @param analysis - Image analysis result
 * @param textRequirements - Text requirements
 * @returns Array of placement suggestions
 */
export function getTextPlacementSuggestions(
  analysis: ImageAnalysis,
  textRequirements: TextRequirements
): Placement[];

/**
 * Render text onto image according to placements and user choices.
 * 
 * @param imagePath - Path to the input image
 * @param outputPath - Path for the output image
 * @param placements - Text placement configurations
 * @param userChoices - User customization choices
 * @returns Path to the rendered output image
 */
export function renderTextOnImage(
  imagePath: string,
  outputPath: string,
  placements: Placement[],
  userChoices: UserChoices
): string;

/**
 * Create a new workflow instance.
 * 
 * @param options - Workflow configuration options
 * @returns Workflow instance
 */
export function createWorkflow(options: WorkflowOptions): Workflow;

/**
 * Configure the library with default options.
 * 
 * @param config - Configuration object
 */
export function configure(config: Config): void;

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Parse color string to RGB tuple.
 * 
 * @param colorStr - Color string (hex, name, etc.)
 * @param alpha - Optional alpha value
 * @returns RGB or RGBA color tuple
 */
export function parseColor(colorStr: string, alpha?: number): RGBColor | RGBAColor;

/**
 * Calculate optimal font size for a bounding box.
 * 
 * @param bbox - Bounding box dimensions
 * @param text - Text content
 * @param userChoices - User choices
 * @returns Optimal font size in pixels
 */
export function calculateFontSize(
  bbox: BoundingBox,
  text: string,
  userChoices: UserChoices
): number;

/**
 * Validate user choices.
 * 
 * @param choices - User choices to validate
 * @returns Validation result
 */
export function validateUserChoices(choices: UserChoices): {
  valid: boolean;
  errors: string[];
};

// ============================================================================
// Error Types
// ============================================================================

/** Base error class */
export class PerfectTextOverlayError extends Error {
  /** Error code */
  code: string;
  /** Step where error occurred */
  step?: string;
}

/** Error for invalid prompts */
export class PromptError extends PerfectTextOverlayError {
  code: 'PROMPT_INVALID' | 'PROMPT_NO_TEXT' | 'PROMPT_TOO_LONG';
}

/** Error for image processing */
export class ImageError extends PerfectTextOverlayError {
  code: 'IMAGE_NOT_FOUND' | 'IMAGE_INVALID' | 'IMAGE_TOO_SMALL' | 'ANALYSIS_FAILED';
}

/** Error for text rendering */
export class RenderError extends PerfectTextOverlayError {
  code: 'FONT_NOT_FOUND' | 'RENDER_FAILED' | 'TEXT_TOO_LONG';
}

// ============================================================================
// Default Export
// ============================================================================

declare const perfectTextOverlay: {
  separatePrompt: typeof separatePrompt;
  analyzeImage: typeof analyzeImage;
  getTextPlacementSuggestions: typeof getTextPlacementSuggestions;
  renderTextOnImage: typeof renderTextOnImage;
  createWorkflow: typeof createWorkflow;
  configure: typeof configure;
  parseColor: typeof parseColor;
  calculateFontSize: typeof calculateFontSize;
  validateUserChoices: typeof validateUserChoices;
  PerfectTextOverlayError: typeof PerfectTextOverlayError;
  PromptError: typeof PromptError;
  ImageError: typeof ImageError;
  RenderError: typeof RenderError;
};

export default perfectTextOverlay;

/**
 * Perfect Text Overlay - React Component Example
 * ================================================
 * 
 * This example shows how to integrate perfect-text-overlay in a React application.
 * 
 * IMPORTANT NOTE: The actual image processing (analysis and text rendering) 
 * happens on the server side. The React component handles the UI and 
 * communicates with the backend API.
 * 
 * Prerequisites:
 * - React 18+
 * - Axios or fetch for API calls
 * 
 * Backend API should implement endpoints:
 * - POST /api/separate-prompt
 * - POST /api/analyze-image
 * - POST /api/render-text
 * - POST /api/process-complete
 */

import React, { useState, useCallback } from 'react';
import axios from 'axios';

// ============================================
// Configuration
// ============================================
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';

const FONT_STYLES = [
  { value: 'modern', label: '现代简约', description: 'Clean sans-serif (推荐: 科技/商务)' },
  { value: 'traditional', label: '传统书法', description: 'Serif style (推荐: 中式/文化)' },
  { value: 'traditional_tw', label: '台湾繁体', description: 'Traditional Chinese (台湾)' },
  { value: 'korean', label: '韩文字体', description: 'Korean font' },
  { value: 'english', label: '英文', description: 'Roboto font (英文/拉丁)' },
  { value: 'cartoon', label: '可爱卡通', description: 'Playful style (推荐: 儿童/趣味)' },
  { value: 'calligraphy', label: '艺术手写', description: 'Handwritten style (推荐: 个人/温馨)' }
];

const SCENE_TYPES = [
  { value: 'poster', label: '海报/封面', description: '单组/少量文字，强调视觉' },
  { value: 'flowchart', label: '流程图/步骤图', description: '多组文字，强调逻辑顺序' },
  { value: 'infographic', label: '信息图/数据图', description: '多组文字，强调信息呈现' },
  { value: 'diagram', label: '示意图/标注图', description: '多组文字，强调说明' }
];

const EFFECT_OPTIONS = [
  { value: 'shadow', label: '添加阴影', description: '增加立体感' },
  { value: 'outline', label: '添加描边', description: '增强可读性' },
  { value: 'background_box', label: '半透明背景框', description: '确保清晰' },
  { value: 'border', label: '添加框线', description: '流程图节点' },
  { value: 'arrows', label: '添加连接箭头', description: '流程图' }
];

// ============================================
// Main Component
// ============================================

export default function PerfectTextOverlay() {
  // Form state
  const [prompt, setPrompt] = useState('');
  const [sceneType, setSceneType] = useState('poster');
  const [fontStyle, setFontStyle] = useState('modern');
  const [selectedEffects, setSelectedEffects] = useState(['shadow', 'outline']);
  const [textPosition, setTextPosition] = useState('auto');
  const [textColor, setTextColor] = useState('');
  
  // Processing state
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Results
  const [separatedPrompt, setSeparatedPrompt] = useState(null);
  const [placements, setPlacements] = useState(null);
  const [baseImage, setBaseImage] = useState(null);
  const [finalImage, setFinalImage] = useState(null);

  // ============================================
  // Handlers
  // ============================================

  const handleEffectToggle = (effect) => {
    setSelectedEffects(prev => 
      prev.includes(effect)
        ? prev.filter(e => e !== effect)
        : [...prev, effect]
    );
  };

  const handleSeparatePrompt = useCallback(async () => {
    if (!prompt.trim()) return;
    
    setLoading(true);
    setError(null);
    setStep(1);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/separate-prompt`, {
        prompt: prompt
      });
      
      setSeparatedPrompt(response.data);
    } catch (err) {
      setError('Failed to separate prompt: ' + err.message);
    } finally {
      setLoading(false);
    }
  }, [prompt]);

  const handleGenerateImage = useCallback(async () => {
    if (!separatedPrompt) return;
    
    setLoading(true);
    setError(null);
    setStep(2);
    
    try {
      // In production, this would call your image generation service
      // For this example, we assume the user uploads or generates the image externally
      
      // Simulating image generation/upload
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // User would upload the generated image here
      // For demo purposes, we'll use a placeholder
      setBaseImage('/api/placeholder/800/600');
    } catch (err) {
      setError('Failed to generate image: ' + err.message);
    } finally {
      setLoading(false);
    }
  }, [separatedPrompt]);

  const handleAnalyzeImage = useCallback(async (imageFile) => {
    if (!separatedPrompt || !imageFile) return;
    
    setLoading(true);
    setError(null);
    setStep(3);
    
    try {
      const formData = new FormData();
      formData.append('image', imageFile);
      formData.append('text_requirements', JSON.stringify(separatedPrompt.text_requirements));
      
      const response = await axios.post(`${API_BASE_URL}/analyze-image`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setPlacements(response.data.placements);
    } catch (err) {
      setError('Failed to analyze image: ' + err.message);
    } finally {
      setLoading(false);
    }
  }, [separatedPrompt]);

  const handleRender = useCallback(async () => {
    if (!baseImage || !placements) return;
    
    setLoading(true);
    setError(null);
    setStep(5);
    
    try {
      const userChoices = {
        font_style: fontStyle,
        effects: selectedEffects,
        text_position: textPosition,
        text_color: textColor ? hexToRgb(textColor) : null,
        scene_type: sceneType
      };
      
      const response = await axios.post(`${API_BASE_URL}/render-text`, {
        base_image: baseImage,
        placements: placements,
        user_choices: userChoices
      });
      
      setFinalImage(response.data.output_url);
    } catch (err) {
      setError('Failed to render text: ' + err.message);
    } finally {
      setLoading(false);
    }
  }, [baseImage, placements, fontStyle, selectedEffects, textPosition, textColor, sceneType]);

  const handleProcessComplete = useCallback(async () => {
    if (!prompt.trim()) return;
    
    setLoading(true);
    setError(null);
    setStep(1);
    
    try {
      const userChoices = {
        font_style: fontStyle,
        effects: selectedEffects,
        text_position: textPosition,
        text_color: textColor ? hexToRgb(textColor) : null,
        scene_type: sceneType
      };
      
      const response = await axios.post(`${API_BASE_URL}/process-complete`, {
        prompt: prompt,
        user_choices: userChoices
      });
      
      setSeparatedPrompt(response.data.separated);
      setPlacements(response.data.placements);
      setFinalImage(response.data.output_url);
      setStep(5);
    } catch (err) {
      setError('Failed to process: ' + err.message);
    } finally {
      setLoading(false);
    }
  }, [prompt, fontStyle, selectedEffects, textPosition, textColor, sceneType]);

  // ============================================
  // Helpers
  // ============================================

  const hexToRgb = (hex) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? [
      parseInt(result[1], 16),
      parseInt(result[2], 16),
      parseInt(result[3], 16)
    ] : null;
  };

  // ============================================
  // Render
  // ============================================

  return (
    <div className="perfect-text-overlay">
      <header className="pto-header">
        <h1>🎨 Perfect Text Overlay</h1>
        <p>Create images with perfect text rendering</p>
      </header>

      {/* Error Display */}
      {error && (
        <div className="pto-error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Step 0: Input Prompt */}
      <section className="pto-section">
        <h2>Step 1: Enter Your Prompt</h2>
        <textarea
          className="pto-textarea"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="e.g., 生成一张春节促销海报，标题写'新春大促，全场5折起'"
          rows={4}
        />
        <button 
          className="pto-button pto-button-primary"
          onClick={handleSeparatePrompt}
          disabled={loading || !prompt.trim()}
        >
          {loading ? 'Processing...' : 'Separate Prompt'}
        </button>
      </section>

      {/* Step 1: Show Separated Result */}
      {separatedPrompt && (
        <section className="pto-section">
          <h2>Step 2: Separated Result</h2>
          <div className="pto-result-box">
            <h4>Image Prompt:</h4>
            <p className="pto-prompt-text">{separatedPrompt.image_prompt}</p>
            
            <h4>Text Requirements:</h4>
            <ul>
              {separatedPrompt.text_requirements.text_groups.map((group, i) => (
                <li key={group.id}>
                  <strong>Text {i + 1}:</strong> "{group.content}"
                </li>
              ))}
            </ul>
          </div>
        </section>
      )}

      {/* Step 2: Customization Options */}
      {separatedPrompt && (
        <section className="pto-section">
          <h2>Step 3: Customize Your Image</h2>
          
          {/* Scene Type */}
          <div className="pto-form-group">
            <label>Scene Type:</label>
            <select value={sceneType} onChange={(e) => setSceneType(e.target.value)}>
              {SCENE_TYPES.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label} - {type.description}
                </option>
              ))}
            </select>
          </div>

          {/* Font Style */}
          <div className="pto-form-group">
            <label>Font Style:</label>
            <select value={fontStyle} onChange={(e) => setFontStyle(e.target.value)}>
              {FONT_STYLES.map(font => (
                <option key={font.value} value={font.value}>
                  {font.label} - {font.description}
                </option>
              ))}
            </select>
          </div>

          {/* Text Position */}
          <div className="pto-form-group">
            <label>Text Position:</label>
            <select value={textPosition} onChange={(e) => setTextPosition(e.target.value)}>
              <option value="auto">自动检测最佳位置</option>
              <option value="top">顶部居中（标题风格）</option>
              <option value="bottom">底部居中（电影海报风格）</option>
              <option value="center">中心位置（强调重点）</option>
            </select>
          </div>

          {/* Text Color */}
          <div className="pto-form-group">
            <label>Text Color (optional):</label>
            <input
              type="color"
              value={textColor}
              onChange={(e) => setTextColor(e.target.value)}
              placeholder="Auto-detect"
            />
            <small>Leave empty for auto-detection</small>
          </div>

          {/* Effects */}
          <div className="pto-form-group">
            <label>Effects:</label>
            <div className="pto-effects-grid">
              {EFFECT_OPTIONS.map(effect => (
                <label key={effect.value} className="pto-checkbox">
                  <input
                    type="checkbox"
                    checked={selectedEffects.includes(effect.value)}
                    onChange={() => handleEffectToggle(effect.value)}
                  />
                  <span>{effect.label}</span>
                  <small>{effect.description}</small>
                </label>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Step 3: Image Upload */}
      {separatedPrompt && (
        <section className="pto-section">
          <h2>Step 4: Upload Base Image</h2>
          <p className="pto-hint">
            Generate a base image using the image prompt above, then upload it here.
            <br />
            Use DALL-E, Midjourney, Stable Diffusion, or any image generator.
          </p>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => {
              if (e.target.files[0]) {
                handleAnalyzeImage(e.target.files[0]);
              }
            }}
          />
        </section>
      )}

      {/* Step 4: Placements Preview */}
      {placements && (
        <section className="pto-section">
          <h2>Step 5: Text Placement Preview</h2>
          <div className="pto-placements">
            {placements.map((placement, i) => (
              <div key={placement.id} className="pto-placement-card">
                <h4>Text {i + 1}</h4>
                <p><strong>Content:</strong> "{placement.text}"</p>
                <p><strong>Position:</strong> ({placement.x}, {placement.y})</p>
                <p><strong>Size:</strong> {placement.width}x{placement.height}</p>
              </div>
            ))}
          </div>
          <button 
            className="pto-button pto-button-primary"
            onClick={handleRender}
            disabled={loading}
          >
            {loading ? 'Rendering...' : 'Render Final Image'}
          </button>
        </section>
      )}

      {/* Step 5: Final Result */}
      {finalImage && (
        <section className="pto-section">
          <h2>✅ Final Result</h2>
          <div className="pto-image-container">
            <img src={finalImage} alt="Final result" className="pto-final-image" />
          </div>
          <div className="pto-actions">
            <a href={finalImage} download className="pto-button">
              Download Image
            </a>
            <button 
              className="pto-button pto-button-secondary"
              onClick={() => {
                setStep(0);
                setPrompt('');
                setSeparatedPrompt(null);
                setPlacements(null);
                setBaseImage(null);
                setFinalImage(null);
              }}
            >
              Start Over
            </button>
          </div>
        </section>
      )}

      {/* Progress Indicator */}
      {loading && (
        <div className="pto-loading-overlay">
          <div className="pto-spinner"></div>
          <p>Processing... (Step {step}/5)</p>
        </div>
      )}
    </div>
  );
}

// ============================================
// CSS Styles (can be moved to separate file)
// ============================================

const styles = `
.perfect-text-overlay {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.pto-header {
  text-align: center;
  margin-bottom: 40px;
}

.pto-header h1 {
  font-size: 2.5em;
  margin-bottom: 10px;
}

.pto-section {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}

.pto-section h2 {
  margin-top: 0;
  color: #333;
}

.pto-textarea {
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  resize: vertical;
  margin-bottom: 16px;
}

.pto-button {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
  margin-right: 12px;
}

.pto-button-primary {
  background: #007bff;
  color: white;
}

.pto-button-primary:hover {
  background: #0056b3;
}

.pto-button-secondary {
  background: #6c757d;
  color: white;
}

.pto-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.pto-form-group {
  margin-bottom: 20px;
}

.pto-form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
}

.pto-form-group select,
.pto-form-group input[type="color"] {
  padding: 10px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  width: 100%;
}

.pto-effects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.pto-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  cursor: pointer;
}

.pto-checkbox input {
  width: 20px;
  height: 20px;
}

.pto-checkbox small {
  color: #666;
  margin-left: auto;
}

.pto-result-box {
  background: white;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #007bff;
}

.pto-prompt-text {
  color: #555;
  font-style: italic;
}

.pto-placements {
  display: grid;
  gap: 12px;
  margin-bottom: 20px;
}

.pto-placement-card {
  background: white;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.pto-image-container {
  text-align: center;
  margin: 20px 0;
}

.pto-final-image {
  max-width: 100%;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.pto-error {
  background: #f8d7da;
  color: #721c24;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.pto-hint {
  color: #666;
  font-size: 14px;
  margin-bottom: 16px;
}

.pto-loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255,255,255,0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.pto-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
`;

// Inject styles
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.innerText = styles;
  document.head.appendChild(styleSheet);
}

// ============================================
// Hook for using the component logic
// ============================================

export function usePerfectTextOverlay() {
  const [state, setState] = useState({
    loading: false,
    error: null,
    result: null
  });

  const processPrompt = useCallback(async (prompt, userChoices) => {
    setState({ loading: true, error: null, result: null });
    
    try {
      const response = await axios.post(`${API_BASE_URL}/process-complete`, {
        prompt,
        user_choices: userChoices
      });
      
      setState({
        loading: false,
        error: null,
        result: response.data
      });
      
      return response.data;
    } catch (err) {
      setState({
        loading: false,
        error: err.message,
        result: null
      });
      throw err;
    }
  }, []);

  return {
    ...state,
    processPrompt
  };
}

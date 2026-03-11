# Flowchart Symbols Guide

Standard flowchart symbols and their usage.

## Basic Symbols

### 1. Terminal (Start/End)
**Shape:** Rounded rectangle or oval
**Usage:** Beginning or end of a process
**Text examples:** "开始", "结束", "Start", "End", "完成"

```
┌─────────────┐
│   开始     │
└─────────────┘
```

### 2. Process
**Shape:** Rectangle
**Usage:** General processing step, action
**Text examples:** "验证邮箱", "处理数据", "Verify Email"

```
┌─────────────┐
│  验证邮箱   │
└─────────────┘
```

### 3. Decision
**Shape:** Diamond
**Usage:** Decision point with yes/no or multiple branches
**Text examples:** "是否有效？", "通过？", "Is Valid?"

```
      /\
     /  \
    / 是 \
   / 否？ \
  /________\
```

### 4. Input/Output
**Shape:** Parallelogram
**Usage:** Data input or output operations
**Text examples:** "输入用户名", "显示结果", "Input Data"

```
    /─────────/
   / 输入数据  /
  /─────────/
```

### 5. Connector
**Shape:** Small circle
**Usage:** Connects flowchart across pages or distant areas

### 6. Arrow/Flow Line
**Shape:** Line with arrowhead
**Usage:** Shows direction of flow between symbols

## Node Type Recommendations by Content

| Content Type | Recommended Shape | Color Suggestion |
|-------------|--------------------|------------------|
| Start/End | Rounded rectangle | Green (start), Gray (end) |
| Process | Rectangle | Blue |
| Decision | Diamond | Yellow or Orange |
| Input/Output | Parallelogram | Purple |
| Error/Exception | Rectangle with red border | Red |

## Layout Patterns

### Horizontal Linear Flow
```
[开始] → [步骤1] → [步骤2] → [结束]
```
Best for: Simple sequential processes

### Vertical Linear Flow
```
   [开始]
      ↓
   [步骤1]
      ↓
   [步骤2]
      ↓
   [结束]
```
Best for: Step-by-step instructions

### Decision Branch
```
        [开始]
           ↓
       [验证？]
        ↙    ↘
   [通过]    [失败]
      ↓        ↓
  [继续]    [重试]
```
Best for: Conditional logic

### Parallel Process
```
         [开始]
            ↓
     ┌──────┴──────┐
     ↓             ↓
 [任务A]       [任务B]
     ↓             ↓
     └──────┬──────┘
            ↓
         [合并]
```
Best for: Parallel workflows

## Text Styling for Flowcharts

### Font
- **Type:** Sans-serif (clean and readable)
- **Weight:** Medium or Bold
- **Size:** Large enough to read at thumbnail size

### Alignment
- **Inside nodes:** Centered both horizontally and vertically
- **Multiple lines:** Center-aligned

### Color
- **Light nodes:** Dark text (black or dark gray)
- **Dark nodes:** Light text (white)
- **Decision diamonds:** Often use black text regardless

## Spacing Guidelines

- **Node padding:** Text should have 20-30% padding inside the shape
- **Node spacing:** Minimum 1.5x node width between adjacent nodes
- **Arrow length:** Should be clear but not excessively long
- **Label spacing:** Decision labels (yes/no) should be close to arrows

## Multi-line Text in Nodes

When text is too long for a single line:

```
┌─────────────────┐
│    填写用户      │
│    基本信息      │
└─────────────────┘
```

Guidelines:
- Break at natural pauses
- Keep 2-3 lines maximum
- Adjust font size if needed
- Consider shorter wording

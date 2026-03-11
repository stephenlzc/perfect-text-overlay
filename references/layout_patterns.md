# Layout Patterns for Text Overlay

This document describes common layout patterns and best practices for placing text on images.

## Single Text Layouts

### 1. Top Center (Header Style)
**Best for:** Titles, headlines, announcements
- **Position:** Top 15-25% of image
- **Alignment:** Center
- **Max width:** 80% of image width
- **Font size:** Large (title size)
- **Background:** Optional subtle bar or shadow

### 2. Bottom Center (Movie Poster Style)
**Best for:** Captions, credits, taglines
- **Position:** Bottom 15-25% of image
- **Alignment:** Center
- **Max width:** 80% of image width
- **Font size:** Medium to large
- **Background:** Often has gradient fade from bottom

### 3. Center Focus
**Best for:** Emphasis, quotes, key messages
- **Position:** Center of image
- **Alignment:** Center
- **Max width:** 60-70% of image width
- **Font size:** Large
- **Background:** Often needs semi-transparent box

### 4. Side Placement
**Best for:** Vertical text, Asian-style layouts
- **Position:** Left or right 15-20% of image
- **Alignment:** Vertical or horizontal
- **Max width:** 20-30% of image width
- **Font size:** Medium
- **Background:** Usually transparent or minimal

## Flowchart/Diagram Layouts

### 1. Horizontal Flow (Left to Right)
```
[Node 1] → [Node 2] → [Node 3]
```
**Best for:** Linear processes, timelines
- **Node distribution:** Evenly spaced horizontally
- **Vertical position:** Middle or slightly above center
- **Spacing:** Equal gaps between nodes
- **Arrows:** Horizontal, pointing right

### 2. Vertical Flow (Top to Bottom)
```
  [Node 1]
     ↓
  [Node 2]
     ↓
  [Node 3]
```
**Best for:** Step-by-step instructions, decision trees
- **Node distribution:** Evenly spaced vertically
- **Horizontal position:** Center or aligned left
- **Spacing:** Equal gaps between nodes
- **Arrows:** Vertical, pointing down

### 3. Branching Structure
```
       [Start]
          ↓
      [Decision]
       ↙      ↘
  [Branch A] [Branch B]
```
**Best for:** Decision trees, conditional flows
- **Root:** Top or left
- **Branches:** Spread outward
- **Alignment:** Hierarchical levels aligned
- **Arrows:** Show direction of flow

## Typography Best Practices

### Color Contrast
- **Light background:** Dark text (black, dark gray, dark blue)
- **Dark background:** Light text (white, light gray, cream)
- **Colorful background:** White or black with transparency/shadow
- **General rule:** Contrast ratio should be at least 4.5:1

### Font Size Hierarchy
1. **Main title:** 48-72px (or 8-12% of image height)
2. **Subtitle:** 32-48px (or 5-8% of image height)
3. **Body text:** 18-32px (or 3-5% of image height)
4. **Captions:** 14-18px (or 2-3% of image height)

### Readability Enhancements

#### Shadow Effect
- **Color:** Black with 30-50% opacity
- **Offset:** 2-4 pixels
- **Blur:** 0-2 pixels (optional)

#### Outline/Stroke
- **Color:** Opposite of text color (black text → white outline)
- **Width:** 1-3 pixels
- **Use case:** Essential for text on busy/complex backgrounds

#### Background Box
- **Style:** Rounded rectangle or pill shape
- **Color:** White or black with 70-85% opacity
- **Padding:** 10-20% of text size on all sides
- **Use case:** Ensures readability on any background

### Text Length Guidelines

| Text Type | Max Characters (EN) | Max Characters (CN) |
|-----------|--------------------|--------------------|
| Headline | 30-40 | 10-15 |
| Subtitle | 50-60 | 15-20 |
| Body | 100-150 | 40-60 |
| Caption | 80-100 | 25-40 |

## Cultural/Regional Considerations

### Chinese Text
- **Vertical layouts:** Traditional for formal occasions
- **Font choices:** Serif (Songti) for formal, Sans-serif (Heiti) for modern
- **Avoid:** Too many font variations (max 2-3)

### Western Text
- **Alignment:** Left-aligned for long text, centered for short
- **All caps:** Use sparingly, good for short labels only
- **Line spacing:** 1.2-1.5x for body text

### Mixed Language
- **Chinese + English:** Use compatible fonts, maintain similar weight
- **Size adjustment:** English may need to be slightly larger to match visual weight
- **Spacing:** Extra space between Chinese and English text

## Common Mistakes to Avoid

1. **Placing text over faces or important subjects**
2. **Insufficient contrast with background**
3. **Font too small or too decorative for readability**
4. **Too many different fonts in one image**
5. **Text too close to image edges**
6. **Ignoring safe zones (avoid very edges)**

## Safe Zone Guidelines

Safe zones are areas away from edges where text is less likely to be cropped:
- **Phone screens:** Avoid top/bottom 10% (notch/status bar area)
- **Social media:** Center 80% of image is safest
- **Print materials:** Keep 5mm from all edges

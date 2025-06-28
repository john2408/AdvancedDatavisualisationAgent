# Frontend Styles

This directory contains all the CSS styling for the Visualization Agent application.

## File Structure

```
frontend/style/
├── base.css        # Base layout and typography styles
├── sidebar.css     # Sidebar-specific styling
├── chat.css        # Chat interface styling
├── components.css  # UI components (buttons, containers, etc.)
└── main.css        # Main file that imports all others (alternative approach)
```

## Style Organization

### base.css
- Main app layout and background
- Typography and text colors
- General element styling
- Streamlit default element hiding

### sidebar.css
- Sidebar background and borders
- Sidebar text styling
- Sidebar layout adjustments

### chat.css
- Chat input box styling
- Chat message containers
- Chat-specific interactions

### components.css
- Button styles and hover effects
- Welcome message container
- Suggestion buttons
- Other UI components

## Usage

The styles are loaded in `app.py` using the utility function from `frontend/utils.py`:

```python
from frontend.utils import load_multiple_css

css_files = [
    "frontend/style/base.css",
    "frontend/style/sidebar.css", 
    "frontend/style/chat.css",
    "frontend/style/components.css"
]
load_multiple_css(css_files)
```

## Adding New Styles

1. Add styles to the appropriate category file
2. If creating a new category, create a new `.css` file
3. Add the new file to the `css_files` list in `app.py`
4. Document the new file in this README

## Color Scheme

- Primary Background: `#F0F2F6`
- Sidebar Background: `#FFFFFF`
- Text Primary: `#1F2937`
- Text Secondary: `#374151`
- Text Muted: `#6B7280`
- Borders: `#E0E0E0`, `#D1D5DB`
- Accent Colors:
  - Blue: `#4F46E5` (background: `#E0E7FF`)
  - Green: `#065F46` (background: `#D1FAE5`)
  - Orange: `#92400E` (background: `#FEF3C7`)

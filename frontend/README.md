# frontend/ - Web User Interface

## Overview

This directory contains the web chat interface for GRAYSON. It provides a clean, responsive chat UI for interacting with the AI research assistant.

## Structure

| File | Purpose |
|------|---------|
| `index.html` | Single-page chat application |

## Tech Stack

- **HTML5** - Semantic markup
- **Vanilla JavaScript** - No framework dependencies
- **Tailwind CSS** - Utility-first styling (via CDN)

## Features

- Real-time chat interface with message animations
- Typing indicator while waiting for responses
- Markdown-like formatting support
- Source citations with clickable links
- Library integration links (OMNI, JSTOR)
- Responsive design for mobile and desktop
- Error handling for API connection issues

## Running the Frontend

### Option 1: Direct File Access
Simply open `index.html` in your web browser:
```
file:///path/to/grayson/frontend/index.html
```

### Option 2: Local Server (Recommended)
```bash
# Using Python
python -m http.server 3000 --directory frontend

# Then open http://localhost:3000
```

## Configuration

The frontend connects to the backend API at `http://localhost:8000`. To change this, edit the `API_URL` constant in `index.html`:

```javascript
const API_URL = 'http://localhost:8000';
```

## API Integration

The frontend communicates with two backend endpoints:

### POST /query
Sends user questions and receives AI-generated responses with sources.

**Request:**
```json
{
  "question": "What is the theological significance of John 1:1?",
  "top_k": 5
}
```

**Response:**
```json
{
  "answer": "Based on the research...",
  "sources": [{"title": "...", "doi": "...", "year": 2020}],
  "library_links": {
    "omni": "https://omni.scholarsportal.info/...",
    "jstor": "https://www.jstor.org/..."
  }
}
```

## Customization

### Styling
The UI uses Tailwind CSS classes. Modify the classes directly in the HTML to change appearance.

### Colors
Primary color scheme uses Tailwind's blue palette. Key classes:
- `bg-blue-600` - Primary buttons
- `text-blue-600` - Accent text
- `border-blue-200` - Borders

### Animations
Custom animations defined in the `<style>` block:
- `fadeIn` - Message entry animation
- `bounce` - Typing indicator dots

## Browser Support

Tested and supported on:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

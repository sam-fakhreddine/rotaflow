# HTML Template Separation Best Practices

## Core Rules
- **NEVER embed HTML strings directly in Python code**
- **NEVER embed CSS directly in HTML files**
- **NEVER embed JavaScript directly in HTML files**

## Template Organization

### File Structure
```
app/
├── templates/
│   ├── html/              # Pure HTML template files
│   │   ├── login.html
│   │   ├── calendar.html
│   │   ├── swaps.html
│   │   └── index.html
│   ├── css/               # Centralized CSS files
│   │   ├── base.css       # Common styles
│   │   ├── forms.css      # Form-specific styles
│   │   └── components.css # Component styles
│   ├── js/                # Centralized JavaScript files
│   │   ├── base.js        # Common functionality
│   │   ├── forms.js       # Form validation
│   │   └── components.js  # Component behavior
│   └── renderers/         # Python template renderers
│       ├── login_renderer.py
│       ├── calendar_renderer.py
│       └── swap_renderer.py
```

### Template Files (.html)
- Pure HTML with placeholder syntax: `{{variable}}`, `{{#loop}}`, `{{/loop}}`
- No Python code in HTML files
- No embedded CSS - use `<link>` tags to external CSS files
- No embedded JavaScript - use `<script src="">` tags to external JS files
- Use consistent placeholder naming

### CSS Files (.css)
- Centralized in `/templates/css/` directory
- Shared styles in `base.css`
- Component-specific styles in separate files
- Follow CSS naming conventions (BEM recommended)

### JavaScript Files (.js)
- Centralized in `/templates/js/` directory
- Shared functionality in `base.js`
- Component-specific behavior in separate files
- Use modern JavaScript (ES6+)

### Renderer Classes (.py)
- Handle data injection into templates
- Contain template loading and rendering logic
- Return rendered HTML strings
- Keep rendering logic separate from business logic

## Implementation Pattern

### HTML Template File
```html
<!DOCTYPE html>
<html>
<head>
    <title>{{title}}</title>
    <style>{{css}}</style>
</head>
<body>
    <div class="container">
        <h1>{{heading}}</h1>
        {{#error_message}}
        <div class="error">{{error_message}}</div>
        {{/error_message}}
        {{content}}
    </div>
</body>
</html>
```

### Python Renderer Class
```python
class TemplateRenderer:
    def __init__(self, template_path):
        self.template_path = template_path
    
    def render(self, **context):
        with open(self.template_path) as f:
            template = f.read()
        return self._substitute_variables(template, context)
```

## Benefits
- **Separation of Concerns**: HTML designers can work independently
- **Maintainability**: Template changes don't require Python code changes
- **Reusability**: Templates can be shared across different handlers
- **Version Control**: HTML changes are clearly visible in diffs
- **IDE Support**: Proper syntax highlighting and validation

## Anti-Patterns to Avoid

### ❌ Bad: Embedded HTML Strings
```python
def render_page(self):
    html = f"""
    <html>
    <body>
        <h1>{self.title}</h1>
        <p>{self.content}</p>
    </body>
    </html>
    """
    return html
```

### ✅ Good: Separate Template Files
```python
def render_page(self):
    renderer = TemplateRenderer('templates/html/page.html')
    return renderer.render(title=self.title, content=self.content)
```
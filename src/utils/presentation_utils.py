"""
Utilities for presentation formatting and handling.
"""
import os
import json
import re
from typing import Dict, List, Optional, Union, Any

class PresentationFormat:
    """
    Formats for presentation output.
    """
    MARKDOWN = "markdown"
    HTML = "html"
    # Could add more formats like PPTX in the future

class PresentationUtils:
    """
    Utilities for handling presentation formatting and output.
    """
    
    @staticmethod
    def format_slide_markdown(title: str, content: str, slide_number: int) -> str:
        """
        Format a slide in Markdown format.
        
        Args:
            title: The slide title
            content: The slide content
            slide_number: The slide number
            
        Returns:
            Formatted slide in Markdown
        """
        return f"""
# {title}

{content}

---
"""
    
    @staticmethod
    def markdown_to_html(markdown_text: str) -> str:
        """
        Convert Markdown text to HTML.
        
        Args:
            markdown_text: The markdown text to convert
            
        Returns:
            HTML representation of the markdown
        """
        # Basic markdown conversion - headings
        html = markdown_text
        
        # Convert headers (h1-h6)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
        html = re.sub(r'^##### (.+)$', r'<h5>\1</h5>', html, flags=re.MULTILINE)
        html = re.sub(r'^###### (.+)$', r'<h6>\1</h6>', html, flags=re.MULTILINE)
        
        # Convert bold and italic
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        html = re.sub(r'\_\_(.+?)\_\_', r'<strong>\1</strong>', html)
        html = re.sub(r'\_(.+?)\_', r'<em>\1</em>', html)
        
        # Convert links
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
        
        # Convert unordered lists
        list_pattern = re.compile(r'(^|\n)(\* .+?(?:\n\* .+?)*)(?=\n|$)', re.DOTALL)
        
        def replace_list(match):
            items = match.group(2).split('\n* ')
            items = [item for item in items if item]
            if not items:
                return match.group(0)
            list_html = '<ul>\n'
            for item in items:
                list_html += f'  <li>{item}</li>\n'
            list_html += '</ul>'
            return match.group(1) + list_html
        
        html = list_pattern.sub(replace_list, html)
        
        # Convert ordered lists
        ordered_list_pattern = re.compile(r'(^|\n)((?:\d+\. .+\n?)+)(?=\n|$)', re.MULTILINE)
        
        def replace_ordered_list(match):
            items = re.split(r'\d+\.\s+', match.group(2))
            items = [item for item in items if item.strip()]
            if not items:
                return match.group(0)
            list_html = '<ol>\n'
            for item in items:
                list_html += f'  <li>{item.strip()}</li>\n'
            list_html += '</ol>'
            return match.group(1) + list_html
        
        html = ordered_list_pattern.sub(replace_ordered_list, html)
        
        # Convert code blocks
        html = re.sub(r'```(.+?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
        
        # Convert paragraph breaks
        paragraphs = html.split('\n\n')
        for i, p in enumerate(paragraphs):
            if not p.strip():
                continue
            # Skip if paragraph already contains HTML tags
            if re.search(r'<(h[1-6]|ul|ol|pre|blockquote)', p):
                continue
            paragraphs[i] = f'<p>{p}</p>'
        
        html = '\n'.join(paragraphs)
        
        # Clean up any extra newlines
        html = re.sub(r'\n{3,}', '\n\n', html)
        
        return html
    
    @staticmethod
    def format_slide_html(title: str, content: str, slide_number: int) -> str:
        """
        Format a slide in HTML format.
        
        Args:
            title: The slide title
            content: The slide content (in Markdown format)
            slide_number: The slide number
            
        Returns:
            Formatted slide in HTML
        """
        # Convert content from markdown to HTML
        html_content = PresentationUtils.markdown_to_html(content)
        
        return f"""
<div class="slide" id="slide-{slide_number}" data-slide-number="{slide_number}">
    <div class="slide-header">
        <span class="slide-number">{slide_number}</span>
    </div>
    <h1 class="slide-title">{title}</h1>
    <div class="content">
        {html_content}
    </div>
    <div class="slide-footer">
        <div class="progress-indicator">
            <div class="progress-bar" style="width: {(slide_number / 100) * 100}%"></div>
        </div>
    </div>
</div>
"""
    
    @staticmethod
    def create_presentation_markdown(slides: List[Dict[str, str]], title: str) -> str:
        """
        Create a complete presentation in Markdown format.
        
        Args:
            slides: List of slide dictionaries with 'title' and 'content'
            title: The presentation title
            
        Returns:
            Complete presentation in Markdown
        """
        presentation = f"# {title}\n\n---\n\n"
        
        for i, slide in enumerate(slides):
            presentation += PresentationUtils.format_slide_markdown(
                slide['title'], slide['content'], i+1
            )
        
        return presentation
    
    @staticmethod
    def create_presentation_html(slides: List[Dict[str, str]], title: str, theme: str = "default") -> str:
        """
        Create a complete presentation in HTML format.
        
        Args:
            slides: List of slide dictionaries with 'title' and 'content' (in Markdown format)
            title: The presentation title
            theme: The presentation theme (default, dark, light, gradient)
            
        Returns:
            Complete presentation in HTML
        """
        # Define color schemes for different themes
        themes = {
            "default": {
                "background": "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
                "text": "#333333",
                "accent": "#3498db",
                "secondary": "#2c3e50"
            },
            "dark": {
                "background": "linear-gradient(135deg, #2c3e50 0%, #1a1a2e 100%)",
                "text": "#ffffff",
                "accent": "#e74c3c",
                "secondary": "#ecf0f1"
            },
            "light": {
                "background": "linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%)",
                "text": "#2c3e50",
                "accent": "#27ae60",
                "secondary": "#7f8c8d"
            },
            "gradient": {
                "background": "linear-gradient(135deg, #6a11cb 0%, #2575fc 100%)",
                "text": "#ffffff",
                "accent": "#ffd166",
                "secondary": "#f8f9fa"
            }
        }
        
        # Use the default theme if the specified theme doesn't exist
        theme_colors = themes.get(theme, themes["default"])
        
        html_head = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/atom-one-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&display=swap');
        
        :root {{
            --background: {theme_colors["background"]};
            --text-color: {theme_colors["text"]};
            --accent-color: {theme_colors["accent"]};
            --secondary-color: {theme_colors["secondary"]};
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Poppins', sans-serif;
            background: var(--background);
            color: var(--text-color);
            overflow: hidden;
            transition: background 0.5s ease;
        }}
        
        .presentation-container {{
            position: relative;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
        }}
        
        .slide {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            padding: 4rem 6rem;
            opacity: 0;
            transform: translateY(50px);
            transition: all 0.8s cubic-bezier(0.77, 0, 0.175, 1);
            display: flex;
            flex-direction: column;
            justify-content: center;
            overflow-y: auto;
        }}
        
        .slide.active {{
            opacity: 1;
            transform: translateY(0);
        }}
        
        .slide-header {{
            position: absolute;
            top: 2rem;
            right: 2rem;
        }}
        
        .slide-number {{
            font-size: 1rem;
            opacity: 0.5;
            font-weight: 300;
        }}
        
        .slide-title {{
            font-family: 'Playfair Display', serif;
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            color: var(--accent-color);
            position: relative;
            display: inline-block;
        }}
        
        .slide-title::after {{
            content: '';
            position: absolute;
            bottom: -10px;
            left: 0;
            width: 80px;
            height: 4px;
            background: var(--accent-color);
        }}
        
        .content {{
            font-size: 1.25rem;
            line-height: 1.6;
            max-width: 900px;
        }}
        
        /* Markdown-rendered HTML elements styling */
        .content h1, .content h2, .content h3, .content h4, .content h5, .content h6 {{
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            color: var(--secondary-color);
            font-family: 'Playfair Display', serif;
        }}
        
        .content h1 {{ font-size: 2.5rem; }}
        .content h2 {{ font-size: 2rem; }}
        .content h3 {{ font-size: 1.75rem; }}
        .content h4 {{ font-size: 1.5rem; }}
        .content h5 {{ font-size: 1.25rem; }}
        .content h6 {{ font-size: 1rem; }}
        
        .content p {{
            margin-bottom: 1rem;
        }}
        
        .content a {{
            color: var(--accent-color);
            text-decoration: none;
            border-bottom: 1px dotted var(--accent-color);
            transition: border-bottom 0.3s ease;
        }}
        
        .content a:hover {{
            border-bottom: 1px solid var(--accent-color);
        }}
        
        .content strong {{
            font-weight: 600;
            color: var(--accent-color);
        }}
        
        .content em {{
            font-style: italic;
        }}
        
        .content ul, .content ol {{
            margin-left: 2rem;
            margin-bottom: 1.5rem;
        }}
        
        .content li {{
            margin-bottom: 0.5rem;
        }}
        
        .content img {{
            max-width: 100%;
            border-radius: 8px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
            margin: 1.5rem 0;
        }}
        
        .content blockquote {{
            padding: 1rem 1.5rem;
            border-left: 4px solid var(--accent-color);
            background: rgba(255, 255, 255, 0.1);
            margin: 1.5rem 0;
            border-radius: 0 8px 8px 0;
            font-style: italic;
        }}
        
        .content pre {{
            background: rgba(0, 0, 0, 0.1);
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1.5rem 0;
        }}
        
        .content code {{
            font-family: 'Courier New', Courier, monospace;
            font-size: 0.9em;
            background: rgba(0, 0, 0, 0.1);
            padding: 0.2em 0.4em;
            border-radius: 3px;
        }}
        
        .content pre code {{
            background: transparent;
            padding: 0;
            font-size: 0.85em;
            line-height: 1.5;
        }}
        
        .content table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
        }}
        
        .content table th, .content table td {{
            padding: 0.75rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
            text-align: left;
        }}
        
        .content table th {{
            background: rgba(255, 255, 255, 0.1);
            font-weight: 600;
        }}
        
        .slide-footer {{
            position: absolute;
            bottom: 2rem;
            left: 0;
            width: 100%;
            padding: 0 6rem;
        }}
        
        .progress-indicator {{
            width: 100%;
            height: 4px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 2px;
            overflow: hidden;
        }}
        
        .progress-bar {{
            height: 100%;
            background: var(--accent-color);
            transition: width 0.3s ease;
        }}
        
        .controls {{
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            z-index: 100;
            display: flex;
            gap: 0.5rem;
        }}
        
        .control-button {{
            background: rgba(255, 255, 255, 0.2);
            color: var(--text-color);
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }}
        
        .control-button:hover {{
            background: var(--accent-color);
            transform: scale(1.1);
        }}
        
        .theme-switcher {{
            position: fixed;
            top: 2rem;
            left: 2rem;
            z-index: 100;
        }}
        
        .theme-button {{
            background: rgba(255, 255, 255, 0.2);
            color: var(--text-color);
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            font-size: 0.8rem;
        }}
        
        .theme-button:hover {{
            background: var(--accent-color);
        }}
        
        /* Animations for content */
        .fade-in {{
            animation: fadeIn 1s ease forwards;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        /* Responsive adjustments */
        @media (max-width: 768px) {{
            .slide {{
                padding: 2rem;
            }}
            
            .slide-title {{
                font-size: 2.5rem;
            }}
            
            .content {{
                font-size: 1rem;
            }}
            
            .slide-footer {{
                padding: 0 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="presentation-container">
"""
        
        html_slides = ""
        for i, slide in enumerate(slides):
            html_slides += PresentationUtils.format_slide_html(
                slide['title'], slide['content'], i+1
            )
        
        total_slides = len(slides)
        
        html_foot = f"""
    </div>
    
    <div class="controls">
        <button class="control-button" id="prev-button" title="Previous slide">
            <i class="fas fa-chevron-left"></i>
        </button>
        <button class="control-button" id="next-button" title="Next slide">
            <i class="fas fa-chevron-right"></i>
        </button>
        <button class="control-button" id="fullscreen-button" title="Toggle fullscreen">
            <i class="fas fa-expand"></i>
        </button>
    </div>
    
    <div class="theme-switcher">
        <button class="theme-button" id="theme-toggle">Change Theme</button>
    </div>
    
    <script>
        // Slide navigation functionality
        const slides = document.querySelectorAll('.slide');
        const totalSlides = {total_slides};
        let currentSlide = 0;
        
        // Progress bar update
        function updateProgress() {{
            const progressBars = document.querySelectorAll('.progress-bar');
            progressBars.forEach(bar => {{
                bar.style.width = `${{((currentSlide + 1) / totalSlides) * 100}}%`;
            }});
        }}
        
        // Show the current slide
        function showSlide(index) {{
            // Hide all slides
            slides.forEach(slide => {{
                slide.classList.remove('active');
            }});
            
            // Show the current slide
            slides[index].classList.add('active');
            
            // Update progress
            updateProgress();
        }}
        
        function nextSlide() {{
            if (currentSlide < totalSlides - 1) {{
                currentSlide++;
                showSlide(currentSlide);
            }}
        }}
        
        function prevSlide() {{
            if (currentSlide > 0) {{
                currentSlide--;
                showSlide(currentSlide);
            }}
        }}
        
        // Theme switching functionality
        const themes = ['default', 'dark', 'light', 'gradient'];
        let currentTheme = 0;
        
        function switchTheme() {{
            currentTheme = (currentTheme + 1) % themes.length;
            document.body.setAttribute('data-theme', themes[currentTheme]);
            
            // Update CSS variables based on theme
            const themeColors = {{
                "default": {{
                    "background": "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
                    "text": "#333333",
                    "accent": "#3498db",
                    "secondary": "#2c3e50"
                }},
                "dark": {{
                    "background": "linear-gradient(135deg, #2c3e50 0%, #1a1a2e 100%)",
                    "text": "#ffffff",
                    "accent": "#e74c3c",
                    "secondary": "#ecf0f1"
                }},
                "light": {{
                    "background": "linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%)",
                    "text": "#2c3e50",
                    "accent": "#27ae60", 
                    "secondary": "#7f8c8d"
                }},
                "gradient": {{
                    "background": "linear-gradient(135deg, #6a11cb 0%, #2575fc 100%)",
                    "text": "#ffffff",
                    "accent": "#ffd166",
                    "secondary": "#f8f9fa"
                }}
            }};
            
            const selectedTheme = themeColors[themes[currentTheme]];
            document.documentElement.style.setProperty('--background', selectedTheme.background);
            document.documentElement.style.setProperty('--text-color', selectedTheme.text);
            document.documentElement.style.setProperty('--accent-color', selectedTheme.accent);
            document.documentElement.style.setProperty('--secondary-color', selectedTheme.secondary);
            
            document.getElementById('theme-toggle').textContent = `Theme: ${{themes[currentTheme].charAt(0).toUpperCase() + themes[currentTheme].slice(1)}}`;
        }}
        
        // Fullscreen functionality
        function toggleFullscreen() {{
            if (!document.fullscreenElement) {{
                document.documentElement.requestFullscreen().catch(err => {{
                    console.log(`Error attempting to enable fullscreen: ${{err.message}}`);
                }});
            }} else {{
                if (document.exitFullscreen) {{
                    document.exitFullscreen();
                }}
            }}
        }}
        
        // Initialize presentation
        function initPresentation() {{
            // Show first slide
            showSlide(currentSlide);
            
            // Add event listeners
            document.getElementById('next-button').addEventListener('click', nextSlide);
            document.getElementById('prev-button').addEventListener('click', prevSlide);
            document.getElementById('fullscreen-button').addEventListener('click', toggleFullscreen);
            document.getElementById('theme-toggle').addEventListener('click', switchTheme);
            
            // Add keyboard navigation
            document.addEventListener('keydown', function(e) {{
                if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'n') {{
                    nextSlide();
                }} else if (e.key === 'ArrowLeft' || e.key === 'p') {{
                    prevSlide();
                }} else if (e.key === 'f') {{
                    toggleFullscreen();
                }} else if (e.key === 't') {{
                    switchTheme();
                }}
            }});
            
            // Animate content elements with delay
            const contentElements = document.querySelectorAll('.content > *');
            contentElements.forEach((element, index) => {{
                element.classList.add('fade-in');
                element.style.animationDelay = `${{index * 0.2}}s`;
            }});
            
            // Set initial theme
            document.getElementById('theme-toggle').textContent = `Theme: Default`;
            
            // Initialize syntax highlighting for code blocks
            document.querySelectorAll('pre code').forEach((block) => {{
                hljs.highlightElement(block);
            }});
        }}
        
        // Run initialization when DOM is loaded
        document.addEventListener('DOMContentLoaded', initPresentation);
    </script>
</body>
</html>
"""
        
        return html_head + html_slides + html_foot
    
    @staticmethod
    def save_presentation(content: str, filename: str, format_type: str = PresentationFormat.MARKDOWN):
        """
        Save the presentation to a file.
        
        Args:
            content: The presentation content
            filename: The filename to save to
            format_type: The format type (markdown or html)
        """
        extension = ".md" if format_type == PresentationFormat.MARKDOWN else ".html"
        if not filename.endswith(extension):
            filename += extension
            
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
            
        return filename
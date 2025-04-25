"""
Utilities for presentation formatting and handling.
"""
import os
import json
import re
import math
from typing import Dict, List, Optional, Union, Any, Tuple

from src.utils.markdown_converter import MarkdownConverter

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
    # Constants for content optimization
    MAX_CONTENT_LENGTH = 2000  # Maximum character length for slide content
    MAX_BULLET_POINTS = 8  # Maximum number of bullet points per slide
    MAX_PARAGRAPHS = 4  # Maximum number of paragraphs per slide
    MAX_TITLE_LENGTH = 60  # Maximum character length for slide titles

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
        Convert Markdown text to HTML with improved handling of complex elements.

        Args:
            markdown_text: The markdown text to convert

        Returns:
            HTML representation of the markdown
        """
        # Use the new MarkdownConverter for more robust conversion
        return MarkdownConverter.convert(markdown_text)

    @staticmethod
    def split_content_for_slides(content: str, title: str) -> List[Dict[str, str]]:
        """
        Split content into multiple slides if it's too long instead of trimming.

        Args:
            content: The slide content in markdown format
            title: The slide title

        Returns:
            List of slide dictionaries with 'title' and 'content'
        """
        slides = []

        # Check if content needs to be split
        if not PresentationUtils.detect_content_overflow(content):
            # Content fits on a single slide
            slides.append({
                'title': title,
                'content': content
            })
            return slides

        # Content needs to be split into multiple slides

        # First try to split by paragraphs
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 1:
            current_content = ""
            part_num = 1

            for paragraph in paragraphs:
                # Check if adding this paragraph would cause overflow
                test_content = current_content + paragraph + "\n\n"

                if PresentationUtils.detect_content_overflow(test_content) and current_content:
                    # Current content is already at capacity, create a slide
                    slide_title = f"{title} (Part {part_num})" if part_num > 1 else title
                    slides.append({
                        'title': slide_title,
                        'content': current_content.strip()
                    })
                    current_content = paragraph + "\n\n"
                    part_num += 1
                else:
                    # Add paragraph to current content
                    current_content += paragraph + "\n\n"

            # Add the last slide
            if current_content:
                slide_title = f"{title} (Part {part_num})" if part_num > 1 else title
                slides.append({
                    'title': slide_title,
                    'content': current_content.strip()
                })

            return slides

        # If we can't split by paragraphs, try to split by bullet points
        # Improved pattern to match all list markers (*, +, -)
        bullet_points_match = re.findall(r'^\s*(?:\*|\+|-)\s+(?=\S).+$', content, re.MULTILINE)
        if len(bullet_points_match) > PresentationUtils.MAX_BULLET_POINTS:
            lines = content.split('\n')
            current_content = ""
            bullet_count = 0
            part_num = 1

            for line in lines:
                if re.match(r'^\s*(?:\*|\+|-)\s+(?=\S)', line):
                    bullet_count += 1

                    if bullet_count > PresentationUtils.MAX_BULLET_POINTS and current_content:
                        # Current content has max bullets, create a slide
                        slide_title = f"{title} (Part {part_num})" if part_num > 1 else title
                        slides.append({
                            'title': slide_title,
                            'content': current_content.strip()
                        })
                        current_content = line + "\n"
                        bullet_count = 1
                        part_num += 1
                    else:
                        # Add bullet point to current content
                        current_content += line + "\n"
                else:
                    # Add non-bullet line to current content
                    current_content += line + "\n"

            # Add the last slide
            if current_content:
                slide_title = f"{title} (Part {part_num})" if part_num > 1 else title
                slides.append({
                    'title': slide_title,
                    'content': current_content.strip()
                })

            return slides

        # If we can't split by bullets either, split by content length
        if len(content) > PresentationUtils.MAX_CONTENT_LENGTH:
            remaining = content
            part_num = 1

            while remaining:
                # Find a good breaking point
                if len(remaining) <= PresentationUtils.MAX_CONTENT_LENGTH:
                    # Last piece fits entirely
                    break_point = len(remaining)
                else:
                    break_point = remaining.rfind('\n\n', 0, PresentationUtils.MAX_CONTENT_LENGTH)
                    if break_point == -1:
                        break_point = remaining.rfind('. ', 0, PresentationUtils.MAX_CONTENT_LENGTH)
                    if break_point == -1:
                        break_point = PresentationUtils.MAX_CONTENT_LENGTH

                # Create a slide with this portion
                current_content = remaining[:break_point].strip()
                slide_title = f"{title} (Part {part_num})" if part_num > 1 else title

                slides.append({
                    'title': slide_title,
                    'content': current_content
                })

                # Update remaining content and part number
                remaining = remaining[break_point:].strip()
                part_num += 1

            return slides

        # Fallback: just return the original content as a single slide
        slides.append({
            'title': title,
            'content': content
        })

        return slides

    @staticmethod
    def optimize_title(title: str) -> str:
        """
        Optimize title to fit better on slides.

        Args:
            title: The slide title

        Returns:
            Optimized title
        """
        if len(title) > PresentationUtils.MAX_TITLE_LENGTH:
            # Try to find a good breaking point
            break_point = title.rfind(' ', 0, PresentationUtils.MAX_TITLE_LENGTH - 3)
            if break_point == -1:
                break_point = PresentationUtils.MAX_TITLE_LENGTH - 3

            title = title[:break_point] + "..."

        return title

    @staticmethod
    def detect_content_overflow(content: str) -> bool:
        """
        Detect if content is likely to overflow on a slide.

        Args:
            content: The slide content in markdown format

        Returns:
            True if content is likely to overflow, False otherwise
        """
        # Check content length
        if len(content) > PresentationUtils.MAX_CONTENT_LENGTH:
            return True

        # Check number of bullet points - improved pattern to match all list markers
        bullet_points = re.findall(r'^\s*(?:\*|\+|-)\s+(?=\S)', content, re.MULTILINE)
        if len(bullet_points) > PresentationUtils.MAX_BULLET_POINTS:
            return True

        # Check number of paragraphs
        paragraphs = content.split('\n\n')
        if len(paragraphs) > PresentationUtils.MAX_PARAGRAPHS:
            return True

        return False

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
        # Optimize title if needed
        optimized_title = PresentationUtils.optimize_title(title)

        # Convert content from markdown to HTML
        html_content = PresentationUtils.markdown_to_html(content)

        # Check if this is a multi-part slide
        part_indicator = ""
        if "(Part " in title:
            part_indicator = '<div class="slide-part-indicator">Multi-part slide</div>'

        # The progress bar width will be set by JavaScript

        return f"""
<div class="slide" id="slide-{slide_number}" data-slide-number="{slide_number}">
    <div class="slide-header">
        <span class="slide-number">{slide_number}</span>
    </div>
    <h1 class="slide-title">{optimized_title}</h1>
    <div class="content">
        {html_content}
    </div>
    {part_indicator}
    <div class="slide-footer">
        <div class="progress-indicator">
            <div class="progress-bar" style="width: 0%"></div>
        </div>
    </div>
</div>
"""

    @staticmethod
    def create_presentation_markdown(slides: List[Dict[str, str]], title: str) -> str:
        """
        Create a complete presentation in Markdown format with automatic slide splitting for overflow content.

        Args:
            slides: List of slide dictionaries with 'title' and 'content'
            title: The presentation title

        Returns:
            Complete presentation in Markdown
        """
        presentation = f"# {title}\n\n---\n\n"

        # Process slides and split content if needed
        processed_slides = []
        for slide in slides:
            # Split content into multiple slides if needed
            split_slides = PresentationUtils.split_content_for_slides(slide['content'], slide['title'])
            processed_slides.extend(split_slides)

        # Format all slides
        for i, slide in enumerate(processed_slides):
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
            theme: The presentation theme (elegant-dark, elegant-light, royal-purple, ocean-blue, sunset, default)

        Returns:
            Complete presentation in HTML
        """
        # Define elegant color schemes for different themes
        themes = {
            "elegant-dark": {
                "background": "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",
                "text": "#ffffff",
                "accent": "#0f3460",
                "secondary": "#e94560",
                "subtle_accent": "rgba(15, 52, 96, 0.2)",
                "highlight": "#f1c40f",
                "muted": "rgba(255, 255, 255, 0.7)",
                "shadow": "rgba(0, 0, 0, 0.2)"
            },
            "elegant-light": {
                "background": "linear-gradient(135deg, #f9f9f9 0%, #f0f0f0 100%)",
                "text": "#333333",
                "accent": "#3498db",
                "secondary": "#2ecc71",
                "subtle_accent": "rgba(52, 152, 219, 0.1)",
                "highlight": "#e74c3c",
                "muted": "rgba(0, 0, 0, 0.6)",
                "shadow": "rgba(0, 0, 0, 0.1)"
            },
            "royal-purple": {
                "background": "linear-gradient(135deg, #2c2157 0%, #1e1646 100%)",
                "text": "#f5f5f5",
                "accent": "#8a4fff",
                "secondary": "#ff7eb6",
                "subtle_accent": "rgba(138, 79, 255, 0.2)",
                "highlight": "#ffcf5c",
                "muted": "rgba(245, 245, 245, 0.7)",
                "shadow": "rgba(0, 0, 0, 0.3)"
            },
            "ocean-blue": {
                "background": "linear-gradient(135deg, #f0f5f9 0%, #e4f0f5 100%)",
                "text": "#1e2022",
                "accent": "#1e5f74",
                "secondary": "#133b5c",
                "subtle_accent": "rgba(30, 95, 116, 0.1)",
                "highlight": "#fcdab7",
                "muted": "rgba(30, 32, 34, 0.7)",
                "shadow": "rgba(19, 59, 92, 0.1)"
            },
            "sunset": {
                "background": "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",
                "text": "#ffffff",
                "accent": "#ff9a3c",
                "secondary": "#ff6a88",
                "subtle_accent": "rgba(255, 154, 60, 0.2)",
                "highlight": "#ffde7d",
                "muted": "rgba(255, 255, 255, 0.7)",
                "shadow": "rgba(0, 0, 0, 0.25)"
            },
            "default": {
                "background": "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",
                "text": "#ffffff",
                "accent": "#0f3460",
                "secondary": "#e94560",
                "subtle_accent": "rgba(15, 52, 96, 0.2)",
                "highlight": "#f1c40f",
                "muted": "rgba(255, 255, 255, 0.7)",
                "shadow": "rgba(0, 0, 0, 0.2)"
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
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;400;500&display=swap');

        :root {{
            --background: {theme_colors["background"]};
            --text-color: {theme_colors["text"]};
            --accent-color: {theme_colors["accent"]};
            --secondary-color: {theme_colors["secondary"]};

            /* Additional elegant color variables */
            --subtle-accent: {theme_colors.get("subtle_accent", "rgba(52, 152, 219, 0.2)")};
            --highlight-color: {theme_colors.get("highlight", "#f1c40f")};
            --muted-text: {theme_colors.get("muted", "rgba(255, 255, 255, 0.7)")};
            --shadow-color: {theme_colors.get("shadow", "rgba(0, 0, 0, 0.1)")};

            /* Typography variables */
            --heading-font: 'Cormorant Garamond', 'Playfair Display', serif;
            --body-font: 'Poppins', sans-serif;
            --code-font: 'Fira Code', monospace;

            /* Spacing variables */
            --spacing-xs: 0.25rem;
            --spacing-sm: 0.5rem;
            --spacing-md: 1rem;
            --spacing-lg: 2rem;
            --spacing-xl: 4rem;

            /* Animation variables */
            --transition-fast: 0.3s ease;
            --transition-medium: 0.5s ease;
            --transition-slow: 0.8s cubic-bezier(0.77, 0, 0.175, 1);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: var(--body-font);
            background: var(--background);
            color: var(--text-color);
            overflow: hidden;
            transition: background var(--transition-medium);
            line-height: 1.6;
            font-weight: 300;
            text-rendering: optimizeLegibility;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
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
            padding: var(--spacing-xl) var(--spacing-xl);
            opacity: 0;
            transform: translateY(50px);
            transition: all var(--transition-slow);
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            overflow-y: auto;
            scrollbar-width: thin;
            scrollbar-color: var(--accent-color) transparent;
            background-size: cover;
            background-position: center;
        }}

        /* Custom scrollbar styling */
        .slide::-webkit-scrollbar {{
            width: 6px;
        }}

        .slide::-webkit-scrollbar-track {{
            background: transparent;
        }}

        .slide::-webkit-scrollbar-thumb {{
            background-color: var(--accent-color);
            border-radius: 3px;
        }}

        .slide.active {{
            opacity: 1;
            transform: translateY(0);
            animation: slideFadeIn var(--transition-slow) forwards;
        }}

        @keyframes slideFadeIn {{
            0% {{ opacity: 0; transform: translateY(30px); }}
            100% {{ opacity: 1; transform: translateY(0); }}
        }}

        .slide::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, var(--subtle-accent) 0%, transparent 50%);
            opacity: 0.5;
            z-index: -1;
        }}

        .slide-header {{
            position: absolute;
            top: var(--spacing-lg);
            right: var(--spacing-lg);
            z-index: 10;
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);
        }}

        .slide-number {{
            font-size: 1rem;
            opacity: 0.6;
            font-weight: 300;
            font-family: var(--heading-font);
            letter-spacing: 1px;
            background: var(--subtle-accent);
            padding: var(--spacing-xs) var(--spacing-sm);
            border-radius: 20px;
            min-width: 2.5rem;
            text-align: center;
        }}

        .slide-title {{
            font-family: var(--heading-font);
            font-size: 3.8rem;
            font-weight: 600;
            margin-bottom: var(--spacing-lg);
            color: var(--accent-color);
            position: relative;
            display: inline-block;
            max-width: 90%;
            word-wrap: break-word;
            line-height: 1.2;
            letter-spacing: -0.5px;
            text-shadow: 1px 1px 2px var(--shadow-color);
        }}

        .slide-title::after {{
            content: '';
            position: absolute;
            bottom: -10px;
            left: 0;
            width: 100px;
            height: 3px;
            background: linear-gradient(to right, var(--accent-color), transparent);
            transform-origin: left;
            animation: expandWidth 1.5s ease forwards;
        }}

        @keyframes expandWidth {{
            0% {{ width: 0; opacity: 0; }}
            100% {{ width: 100px; opacity: 1; }}
        }}

        .content {{
            font-size: 1.25rem;
            line-height: 1.6;
            max-width: 900px;
            width: 100%;
            overflow-wrap: break-word;
            word-wrap: break-word;
            hyphens: auto;
            margin-bottom: var(--spacing-lg);
            position: relative;
            z-index: 1;
        }}

        /* Add elegant styling to content elements */
        .elegant-paragraph {{
            margin-bottom: var(--spacing-md);
            font-weight: 300;
            color: var(--text-color);
            text-align: justify;
            text-justify: inter-word;
        }}

        .elegant-paragraph:first-letter {{
            font-size: 1.5em;
            font-weight: 500;
            color: var(--accent-color);
            font-family: var(--heading-font);
        }}

        .elegant-list {{
            margin: var(--spacing-md) 0;
            padding-left: var(--spacing-lg);
        }}

        .elegant-list li {{
            margin-bottom: var(--spacing-sm);
            position: relative;
        }}

        .elegant-list li::before {{
            content: '';
            position: absolute;
            left: -20px;
            top: 10px;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--accent-color);
        }}

        .nested-list {{
            margin-top: var(--spacing-sm);
            margin-left: var(--spacing-md);
        }}

        .elegant-quote {{
            border-left: 3px solid var(--accent-color);
            padding: var(--spacing-md) var(--spacing-lg);
            margin: var(--spacing-md) 0;
            background: var(--subtle-accent);
            border-radius: 0 8px 8px 0;
            font-style: italic;
            position: relative;
        }}

        .elegant-quote::before {{
            content: '"';
            font-family: var(--heading-font);
            font-size: 4rem;
            position: absolute;
            top: -20px;
            left: 10px;
            color: var(--accent-color);
            opacity: 0.2;
        }}

        .elegant-hr {{
            border: none;
            height: 1px;
            background: linear-gradient(to right, transparent, var(--accent-color), transparent);
            margin: var(--spacing-lg) 0;
        }}

        .elegant-hr.thick {{
            height: 3px;
        }}

        .elegant-image {{
            margin: var(--spacing-md) 0;
            position: relative;
            display: inline-block;
            max-width: 100%;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 10px 30px var(--shadow-color);
        }}

        .elegant-image img {{
            max-width: 100%;
            display: block;
            transition: transform var(--transition-medium);
        }}

        .elegant-image:hover img {{
            transform: scale(1.02);
        }}

        .elegant-image figcaption {{
            padding: var(--spacing-sm);
            text-align: center;
            font-style: italic;
            font-size: 0.9rem;
            color: var(--muted-text);
        }}

        .table-container {{
            overflow-x: auto;
            margin: var(--spacing-md) 0;
            border-radius: 8px;
            box-shadow: 0 4px 12px var(--shadow-color);
        }}

        .elegant-table {{
            width: 100%;
            border-collapse: collapse;
            overflow: hidden;
        }}

        .elegant-table th, .elegant-table td {{
            padding: var(--spacing-sm) var(--spacing-md);
            text-align: left;
            border-bottom: 1px solid var(--subtle-accent);
        }}

        .elegant-table th {{
            background: var(--subtle-accent);
            font-weight: 600;
            color: var(--accent-color);
            text-transform: uppercase;
            font-size: 0.9rem;
            letter-spacing: 1px;
        }}

        .elegant-table tr:last-child td {{
            border-bottom: none;
        }}

        .elegant-table tr:hover {{
            background: var(--subtle-accent);
        }}

        .code-block {{
            margin: var(--spacing-md) 0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 12px var(--shadow-color);
            position: relative;
        }}

        .code-block code {{
            font-family: var(--code-font);
            font-size: 0.9rem;
            line-height: 1.5;
            display: block;
            padding: var(--spacing-md);
            overflow-x: auto;
        }}

        .line-number {{
            display: inline-block;
            width: 2rem;
            text-align: right;
            color: var(--muted-text);
            margin-right: var(--spacing-sm);
            user-select: none;
        }}

        .inline-code {{
            font-family: var(--code-font);
            background: var(--subtle-accent);
            padding: 0.1em 0.4em;
            border-radius: 3px;
            font-size: 0.9em;
        }}

        .task-list {{
            list-style: none;
            padding-left: var(--spacing-md);
            margin: var(--spacing-md) 0;
        }}

        .task-item {{
            margin-bottom: var(--spacing-sm);
            display: flex;
            align-items: center;
        }}

        .checkbox {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 1.2rem;
            height: 1.2rem;
            border-radius: 50%;
            margin-right: var(--spacing-sm);
            background: var(--subtle-accent);
            color: var(--accent-color);
            font-size: 0.8rem;
        }}

        .task-item.completed {{
            text-decoration: line-through;
            opacity: 0.7;
        }}

        /* Navigation hints for multi-part slides */
        .slide-part-indicator {{
            position: absolute;
            bottom: 4rem;
            right: 2rem;
            background: linear-gradient(135deg, var(--accent-color), var(--secondary-color));
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 30px;
            font-size: 0.8rem;
            opacity: 0.8;
            transition: all var(--transition-fast);
            box-shadow: 0 4px 12px var(--shadow-color);
            transform: translateY(0);
        }}

        .slide-part-indicator:hover {{
            opacity: 1;
            transform: translateY(-3px);
            box-shadow: 0 6px 16px var(--shadow-color);
        }}

        /* Markdown-rendered HTML elements styling */
        .content h1, .content h2, .content h3, .content h4, .content h5, .content h6 {{
            margin-top: var(--spacing-lg);
            margin-bottom: var(--spacing-md);
            color: var(--secondary-color);
            font-family: var(--heading-font);
            font-weight: 600;
            line-height: 1.2;
            letter-spacing: -0.5px;
            position: relative;
            display: inline-block;
        }}

        .content h1::after, .content h2::after {{
            content: '';
            position: absolute;
            bottom: -5px;
            left: 0;
            width: 50px;
            height: 2px;
            background: linear-gradient(to right, var(--accent-color), transparent);
        }}

        .content h1 {{
            font-size: 2.5rem;
            margin-top: var(--spacing-xl);
        }}

        .content h2 {{
            font-size: 2rem;
            color: var(--accent-color);
        }}

        .content h3 {{
            font-size: 1.75rem;
            font-weight: 500;
        }}

        .content h4 {{
            font-size: 1.5rem;
            font-weight: 500;
            color: var(--accent-color);
            opacity: 0.9;
        }}

        .content h5 {{
            font-size: 1.25rem;
            font-weight: 500;
            font-style: italic;
        }}

        .content h6 {{
            font-size: 1rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .content p {{
            margin-bottom: var(--spacing-md);
            line-height: 1.7;
        }}

        .content a {{
            color: var(--accent-color);
            text-decoration: none;
            border-bottom: 1px dotted var(--accent-color);
            transition: all var(--transition-fast);
            position: relative;
            display: inline-block;
            padding: 0 2px;
        }}

        .content a:hover {{
            border-bottom: 1px solid var(--accent-color);
            background: var(--subtle-accent);
            border-radius: 3px;
        }}

        .content a::after {{
            content: '↗';
            font-size: 0.8em;
            position: relative;
            top: -0.5em;
            opacity: 0;
            margin-left: 2px;
            transition: opacity var(--transition-fast);
        }}

        .content a:hover::after {{
            opacity: 1;
        }}

        .content strong {{
            font-weight: 600;
            color: var(--accent-color);
            padding: 0 2px;
        }}

        .content em {{
            font-style: italic;
            color: var(--secondary-color);
        }}

        .content del {{
            text-decoration: line-through;
            opacity: 0.7;
        }}

        /* Lists are now styled with .elegant-list class */

        /* Images are now styled with .elegant-image class */

        /* Blockquotes are now styled with .elegant-quote class */

        /* Code blocks are now styled with .code-block class */

        /* Tables are now styled with .elegant-table class */

        /* Add animation for content elements */
        .content > * {{
            animation: fadeSlideUp 0.8s ease forwards;
            opacity: 0;
            transform: translateY(20px);
        }}

        @keyframes fadeSlideUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .slide-footer {{
            position: absolute;
            bottom: var(--spacing-lg);
            left: 0;
            width: 100%;
            padding: 0 var(--spacing-xl);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .progress-indicator {{
            width: 100%;
            height: 4px;
            background: var(--subtle-accent);
            border-radius: 4px;
            overflow: hidden;
            box-shadow: 0 2px 8px var(--shadow-color);
        }}

        .progress-bar {{
            height: 100%;
            background: linear-gradient(to right, var(--accent-color), var(--secondary-color));
            transition: width var(--transition-medium);
            border-radius: 4px;
            position: relative;
            overflow: hidden;
        }}

        .progress-bar::after {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(
                90deg,
                rgba(255,255,255,0) 0%,
                rgba(255,255,255,0.3) 50%,
                rgba(255,255,255,0) 100%
            );
            animation: shimmer 2s infinite;
            transform: translateX(-100%);
        }}

        @keyframes shimmer {{
            100% {{ transform: translateX(100%); }}
        }}

        .controls {{
            position: fixed;
            bottom: var(--spacing-lg);
            right: var(--spacing-lg);
            z-index: 100;
            display: flex;
            gap: var(--spacing-xs);
            background: rgba(0, 0, 0, 0.1);
            padding: var(--spacing-xs);
            border-radius: 50px;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 20px var(--shadow-color);
        }}

        .control-button {{
            background: var(--subtle-accent);
            color: var(--text-color);
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all var(--transition-fast);
            font-size: 0.9rem;
        }}

        .control-button:hover {{
            background: var(--accent-color);
            transform: scale(1.1);
            color: white;
            box-shadow: 0 2px 10px var(--shadow-color);
        }}

        .control-button:active {{
            transform: scale(0.95);
        }}

        .theme-switcher {{
            position: fixed;
            top: var(--spacing-lg);
            left: var(--spacing-lg);
            z-index: 100;
        }}

        .theme-button {{
            background: var(--subtle-accent);
            color: var(--text-color);
            border: none;
            padding: var(--spacing-sm) var(--spacing-md);
            border-radius: 30px;
            cursor: pointer;
            transition: all var(--transition-fast);
            backdrop-filter: blur(10px);
            font-size: 0.9rem;
            font-weight: 500;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 12px var(--shadow-color);
            display: flex;
            align-items: center;
            gap: var(--spacing-xs);
        }}

        .theme-button::before {{
            content: '🎨';
            font-size: 1rem;
        }}

        .theme-button:hover {{
            background: var(--accent-color);
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 6px 16px var(--shadow-color);
        }}

        .theme-button:active {{
            transform: translateY(0);
        }}

        /* Animations for content */
        .fade-in {{
            animation: fadeIn 1s ease forwards;
            animation-delay: calc(var(--animation-order, 0) * 0.1s);
            opacity: 0;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Elegant transitions between slides */
        .slide.prev {{
            transform: translateX(-50px);
            opacity: 0;
            transition: all var(--transition-slow);
        }}

        .slide.next {{
            transform: translateX(50px);
            opacity: 0;
            transition: all var(--transition-slow);
        }}

        /* Elegant background patterns */
        .slide::after {{
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 300px;
            height: 300px;
            background-image: radial-gradient(circle, var(--subtle-accent) 10%, transparent 10.5%);
            background-size: 20px 20px;
            background-position: 0 0;
            opacity: 0.3;
            z-index: -1;
            pointer-events: none;
        }}

        /* Responsive adjustments with CSS variables */
        @media (max-width: 1200px) {{
            :root {{
                --spacing-xl: 3rem;
                --spacing-lg: 1.5rem;
            }}

            .slide {{
                padding: var(--spacing-xl);
            }}

            .slide-title {{
                font-size: 3.2rem;
                max-width: 95%;
            }}

            .content {{
                font-size: 1.15rem;
            }}

            .elegant-paragraph:first-letter {{
                font-size: 1.3em;
            }}
        }}

        @media (max-width: 992px) {{
            :root {{
                --spacing-xl: 2.5rem;
                --spacing-lg: 1.25rem;
                --spacing-md: 0.75rem;
            }}

            .slide {{
                padding: var(--spacing-xl);
            }}

            .slide-title {{
                font-size: 2.8rem;
            }}

            .content {{
                font-size: 1.1rem;
                max-width: 100%;
            }}

            .slide-footer {{
                padding: 0 var(--spacing-xl);
            }}

            .elegant-quote::before {{
                font-size: 3rem;
            }}

            .slide::after {{
                width: 200px;
                height: 200px;
            }}
        }}

        @media (max-width: 768px) {{
            :root {{
                --spacing-xl: 2rem;
                --spacing-lg: 1rem;
                --spacing-md: 0.5rem;
            }}

            .slide {{
                padding: var(--spacing-xl);
            }}

            .slide-title {{
                font-size: 2.5rem;
                margin-bottom: var(--spacing-md);
            }}

            .content {{
                font-size: 1rem;
            }}

            .slide-footer {{
                padding: 0 var(--spacing-xl);
                bottom: var(--spacing-lg);
            }}

            .controls {{
                bottom: var(--spacing-lg);
                right: var(--spacing-lg);
            }}

            .theme-switcher {{
                top: var(--spacing-lg);
                left: var(--spacing-lg);
            }}

            .elegant-image figcaption {{
                font-size: 0.8rem;
            }}

            .slide::after {{
                width: 150px;
                height: 150px;
                background-size: 15px 15px;
            }}
        }}

        @media (max-width: 576px) {{
            :root {{
                --spacing-xl: 1.5rem;
                --spacing-lg: 0.75rem;
                --spacing-md: 0.5rem;
                --spacing-sm: 0.25rem;
            }}

            .slide {{
                padding: var(--spacing-xl);
            }}

            .slide-title {{
                font-size: 2rem;
            }}

            .content {{
                font-size: 0.9rem;
            }}

            .slide-header {{
                top: var(--spacing-md);
                right: var(--spacing-md);
            }}

            .controls {{
                bottom: var(--spacing-md);
                right: var(--spacing-md);
                gap: 2px;
                padding: 4px;
            }}

            .theme-switcher {{
                top: var(--spacing-md);
                left: var(--spacing-md);
            }}

            .control-button {{
                width: 32px;
                height: 32px;
                font-size: 0.8rem;
            }}

            .theme-button {{
                font-size: 0.8rem;
                padding: 4px 8px;
            }}

            .theme-button::before {{
                font-size: 0.9rem;
            }}

            .slide-part-indicator {{
                bottom: var(--spacing-xl);
                right: var(--spacing-md);
                font-size: 0.7rem;
                padding: 4px 8px;
            }}

            .slide::after {{
                width: 100px;
                height: 100px;
                background-size: 10px 10px;
            }}
        }}

        /* Handle very small screens and orientation */
        @media (max-height: 600px), (max-width: 400px) {{
            .slide-title {{
                font-size: 1.8rem;
                margin-bottom: var(--spacing-sm);
            }}

            .content {{
                font-size: 0.85rem;
                line-height: 1.4;
            }}

            .content h1 {{ font-size: 1.6rem; }}
            .content h2 {{ font-size: 1.4rem; }}
            .content h3 {{ font-size: 1.2rem; }}
            .content h4 {{ font-size: 1rem; }}
            .content h5 {{ font-size: 0.9rem; }}
            .content h6 {{ font-size: 0.8rem; }}

            .elegant-paragraph:first-letter {{
                font-size: 1.1em;
            }}

            .elegant-quote {{
                padding: var(--spacing-sm);
            }}

            .elegant-quote::before {{
                font-size: 2rem;
                top: -10px;
            }}

            .slide::after {{
                display: none;
            }}
        }}

        /* Print styles for PDF export */
        @media print {{
            .slide {{
                page-break-after: always;
                opacity: 1 !important;
                transform: none !important;
                position: relative;
                height: auto;
                min-height: 100vh;
            }}

            .controls, .theme-switcher, .slide-part-indicator {{
                display: none !important;
            }}

            body {{
                background: white !important;
                color: black !important;
            }}

            .slide-footer {{
                position: relative;
                margin-top: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="presentation-container">
"""

        # Process slides and split content if needed
        processed_slides = []
        for slide in slides:
            # Split content into multiple slides if needed
            split_slides = PresentationUtils.split_content_for_slides(slide['content'], slide['title'])
            processed_slides.extend(split_slides)

        # Format all slides
        html_slides = ""
        for i, slide in enumerate(processed_slides):
            html_slides += PresentationUtils.format_slide_html(
                slide['title'], slide['content'], i+1
            )

        total_slides = len(processed_slides)

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
        <button class="control-button" id="zoom-in-button" title="Zoom in">
            <i class="fas fa-search-plus"></i>
        </button>
        <button class="control-button" id="zoom-out-button" title="Zoom out">
            <i class="fas fa-search-minus"></i>
        </button>
        <button class="control-button" id="reset-zoom-button" title="Reset zoom">
            <i class="fas fa-sync-alt"></i>
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

        // Show the current slide with elegant transitions
        function showSlide(index) {{
            // Get previous slide index
            const prevIndex = currentSlide;

            // Hide all slides and remove transition classes
            slides.forEach(slide => {{
                slide.classList.remove('active', 'prev', 'next');
            }});

            // Add appropriate transition classes
            if (prevIndex !== index && prevIndex >= 0 && prevIndex < slides.length) {{
                if (prevIndex < index) {{
                    slides[prevIndex].classList.add('prev');
                }} else {{
                    slides[prevIndex].classList.add('next');
                }}
            }}

            // Show the current slide
            slides[index].classList.add('active');

            // Update progress
            updateProgress();

            // Reset zoom and auto-fit content for the new slide
            resetZoom();
            setTimeout(autoFitContent, 100);

            // Add animation delay to content elements
            const contentElements = slides[index].querySelectorAll('.content > *');
            contentElements.forEach((element, i) => {{
                element.style.setProperty('--animation-order', i);
            }});

            // Update document title with slide title
            const slideTitle = slides[index].querySelector('.slide-title').textContent;
            document.title = slideTitle + ' | Presentation';
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

        // Theme switching functionality with elegant themes
        const themes = ['elegant-dark', 'elegant-light', 'royal-purple', 'ocean-blue', 'sunset'];
        let currentTheme = 0;

        function switchTheme() {{
            currentTheme = (currentTheme + 1) % themes.length;
            document.body.setAttribute('data-theme', themes[currentTheme]);

            // Update CSS variables based on theme
            const themeColors = {{
                "elegant-dark": {{
                    "background": "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",
                    "text": "#ffffff",
                    "accent": "#0f3460",
                    "secondary": "#e94560",
                    "subtle_accent": "rgba(15, 52, 96, 0.2)",
                    "highlight": "#f1c40f",
                    "muted": "rgba(255, 255, 255, 0.7)",
                    "shadow": "rgba(0, 0, 0, 0.2)"
                }},
                "elegant-light": {{
                    "background": "linear-gradient(135deg, #f9f9f9 0%, #f0f0f0 100%)",
                    "text": "#333333",
                    "accent": "#3498db",
                    "secondary": "#2ecc71",
                    "subtle_accent": "rgba(52, 152, 219, 0.1)",
                    "highlight": "#e74c3c",
                    "muted": "rgba(0, 0, 0, 0.6)",
                    "shadow": "rgba(0, 0, 0, 0.1)"
                }},
                "royal-purple": {{
                    "background": "linear-gradient(135deg, #2c2157 0%, #1e1646 100%)",
                    "text": "#f5f5f5",
                    "accent": "#8a4fff",
                    "secondary": "#ff7eb6",
                    "subtle_accent": "rgba(138, 79, 255, 0.2)",
                    "highlight": "#ffcf5c",
                    "muted": "rgba(245, 245, 245, 0.7)",
                    "shadow": "rgba(0, 0, 0, 0.3)"
                }},
                "ocean-blue": {{
                    "background": "linear-gradient(135deg, #f0f5f9 0%, #e4f0f5 100%)",
                    "text": "#1e2022",
                    "accent": "#1e5f74",
                    "secondary": "#133b5c",
                    "subtle_accent": "rgba(30, 95, 116, 0.1)",
                    "highlight": "#fcdab7",
                    "muted": "rgba(30, 32, 34, 0.7)",
                    "shadow": "rgba(19, 59, 92, 0.1)"
                }},
                "sunset": {{
                    "background": "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",
                    "text": "#ffffff",
                    "accent": "#ff9a3c",
                    "secondary": "#ff6a88",
                    "subtle_accent": "rgba(255, 154, 60, 0.2)",
                    "highlight": "#ffde7d",
                    "muted": "rgba(255, 255, 255, 0.7)",
                    "shadow": "rgba(0, 0, 0, 0.25)"
                }}
            }};

            // Apply theme with smooth transition
            document.body.style.transition = 'background 0.5s ease';

            // Get the selected theme
            const selectedTheme = themeColors[themes[currentTheme]];

            // Set all CSS variables
            document.documentElement.style.setProperty('--background', selectedTheme.background);
            document.documentElement.style.setProperty('--text-color', selectedTheme.text);
            document.documentElement.style.setProperty('--accent-color', selectedTheme.accent);
            document.documentElement.style.setProperty('--secondary-color', selectedTheme.secondary);
            document.documentElement.style.setProperty('--subtle-accent', selectedTheme.subtle_accent);
            document.documentElement.style.setProperty('--highlight-color', selectedTheme.highlight);
            document.documentElement.style.setProperty('--muted-text', selectedTheme.muted);
            document.documentElement.style.setProperty('--shadow-color', selectedTheme.shadow);

            // Format theme name for display
            const themeName = themes[currentTheme].split('-').map(word =>
                word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ');

            document.getElementById('theme-toggle').textContent = themeName;

            // Add a visual feedback for theme change
            const feedback = document.createElement('div');
            feedback.className = 'theme-change-feedback';
            feedback.textContent = 'Theme: ' + themeName;
            feedback.style.position = 'fixed';
            feedback.style.top = '50%';
            feedback.style.left = '50%';
            feedback.style.transform = 'translate(-50%, -50%)';
            feedback.style.background = selectedTheme.accent;
            feedback.style.color = selectedTheme.text;
            feedback.style.padding = '1rem 2rem';
            feedback.style.borderRadius = '30px';
            feedback.style.boxShadow = '0 4px 20px ' + selectedTheme.shadow;
            feedback.style.zIndex = '1000';
            feedback.style.opacity = '0';
            feedback.style.transition = 'opacity 0.3s ease';

            document.body.appendChild(feedback);

            // Show and hide feedback
            setTimeout(() => {{ feedback.style.opacity = '1'; }}, 50);
            setTimeout(() => {{
                feedback.style.opacity = '0';
                setTimeout(() => {{ document.body.removeChild(feedback); }}, 300);
            }}, 1500);
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

        // Zoom functionality
        let currentZoom = 1;
        const MIN_ZOOM = 0.5;
        const MAX_ZOOM = 2;
        const ZOOM_STEP = 0.1;

        function setZoom(zoomLevel) {{
            currentZoom = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, zoomLevel));
            document.querySelectorAll('.content').forEach(content => {{
                content.style.transform = `scale(${{currentZoom}})`;
                content.style.transformOrigin = 'top left';
            }});
        }}

        function zoomIn() {{
            setZoom(currentZoom + ZOOM_STEP);
        }}

        function zoomOut() {{
            setZoom(currentZoom - ZOOM_STEP);
        }}

        function resetZoom() {{
            setZoom(1);
        }}

        // Auto-fit content if it overflows
        function autoFitContent() {{
            const activeSlide = document.querySelector('.slide.active');
            if (!activeSlide) return;

            const content = activeSlide.querySelector('.content');
            const slideHeight = activeSlide.clientHeight;
            const titleHeight = activeSlide.querySelector('.slide-title').offsetHeight;
            const footerHeight = activeSlide.querySelector('.slide-footer').offsetHeight;
            const availableHeight = slideHeight - titleHeight - footerHeight - 120; // 120px for padding

            if (content.scrollHeight > availableHeight) {{
                // Content is too tall, calculate zoom level to fit
                const zoomFactor = availableHeight / content.scrollHeight;
                if (zoomFactor < 1) {{
                    setZoom(Math.max(MIN_ZOOM, zoomFactor));
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
            document.getElementById('zoom-in-button').addEventListener('click', zoomIn);
            document.getElementById('zoom-out-button').addEventListener('click', zoomOut);
            document.getElementById('reset-zoom-button').addEventListener('click', resetZoom);

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
                }} else if (e.key === '+' || e.key === '=') {{
                    zoomIn();
                }} else if (e.key === '-') {{
                    zoomOut();
                }} else if (e.key === '0') {{
                    resetZoom();
                }}
            }});

            // Animate content elements with delay
            const contentElements = document.querySelectorAll('.content > *');
            contentElements.forEach((element, index) => {{
                element.classList.add('fade-in');
                element.style.animationDelay = `${{index * 0.2}}s`;
            }});

            // Set initial theme
            switchTheme(); // Apply the first theme

            // Initialize syntax highlighting for code blocks
            document.querySelectorAll('pre code').forEach((block) => {{
                hljs.highlightElement(block);
            }});

            // Auto-fit content if needed
            setTimeout(autoFitContent, 500);

            // Add resize listener to handle window size changes
            window.addEventListener('resize', function() {{
                resetZoom();
                setTimeout(autoFitContent, 200);
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
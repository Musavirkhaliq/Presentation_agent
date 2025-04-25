"""
A robust markdown to HTML converter for elegant presentations.
"""
import re
from typing import List, Dict, Tuple, Optional, Match


class MarkdownConverter:
    """
    A class to convert markdown to HTML with elegant styling.
    """

    @staticmethod
    def convert(markdown_text: str) -> str:
        """
        Convert markdown text to HTML.

        Args:
            markdown_text: The markdown text to convert

        Returns:
            HTML representation of the markdown
        """
        # Preprocess the markdown text
        text = MarkdownConverter._preprocess(markdown_text)

        # Process code blocks first to protect their content
        text, code_blocks = MarkdownConverter._extract_code_blocks(text)

        # Process elements in the correct order
        text = MarkdownConverter._process_headers(text)
        text = MarkdownConverter._process_horizontal_rules(text)
        text = MarkdownConverter._process_blockquotes(text)
        text = MarkdownConverter._process_lists(text)
        text = MarkdownConverter._process_tables(text)
        text = MarkdownConverter._process_images(text)
        text = MarkdownConverter._process_links(text)
        text = MarkdownConverter._process_emphasis(text)

        # Restore code blocks
        text = MarkdownConverter._restore_code_blocks(text, code_blocks)

        # Process paragraphs
        text = MarkdownConverter._process_paragraphs(text)

        # Final cleanup
        text = MarkdownConverter._postprocess(text)

        return text

    @staticmethod
    def _preprocess(text: str) -> str:
        """Prepare the text for conversion."""
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # Escape HTML entities in the text (except in code blocks, which we'll handle separately)
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        # Add newlines around block elements for easier processing
        block_elements = [
            r'^#{1,6}\s+.+$',  # Headers
            r'^-{3,}$',         # Horizontal rules
            r'^={3,}$',         # Horizontal rules
            r'^\s*\*\s+.+$',    # Unordered lists
            r'^\s*\d+\.\s+.+$', # Ordered lists
            r'^\s*>\s+.+$',     # Blockquotes
            r'^\s*```',         # Code blocks
            r'^\|.+\|$',        # Tables
        ]

        for pattern in block_elements:
            text = re.sub(f'({pattern})', r'\n\1\n', text, flags=re.MULTILINE)

        # Remove extra newlines
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text

    @staticmethod
    def _extract_code_blocks(text: str) -> Tuple[str, Dict[str, str]]:
        """
        Extract code blocks from the text and replace them with placeholders.

        Returns:
            Tuple of (text with placeholders, dictionary of placeholders to code blocks)
        """
        code_blocks = {}

        # Extract fenced code blocks (```code```)
        def replace_fenced_code_block(match: Match) -> str:
            block_id = f"CODE_BLOCK_{len(code_blocks)}"
            lang = match.group(1).strip() if match.group(1) else ""
            code = match.group(2)

            # Store the code block with its language
            code_blocks[block_id] = (lang, code)

            return f"\n\n{block_id}\n\n"

        text = re.sub(r'```([^\n]*)\n(.*?)```', replace_fenced_code_block, text, flags=re.DOTALL)

        # Extract inline code (`code`)
        def replace_inline_code(match: Match) -> str:
            block_id = f"INLINE_CODE_{len(code_blocks)}"
            code = match.group(1)

            # Store the inline code
            code_blocks[block_id] = ("inline", code)

            return block_id

        text = re.sub(r'`([^`\n]+?)`', replace_inline_code, text)

        return text, code_blocks

    @staticmethod
    def _restore_code_blocks(text: str, code_blocks: Dict[str, Tuple[str, str]]) -> str:
        """Restore code blocks from placeholders."""
        for block_id, (lang, code) in code_blocks.items():
            if block_id.startswith("CODE_BLOCK_"):
                # Format fenced code block
                html_code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

                # Add line numbers for multiline code
                if '\n' in html_code:
                    lines = html_code.split('\n')
                    code_with_lines = ""
                    for i, line in enumerate(lines):
                        if line.strip():  # Skip empty lines in numbering
                            code_with_lines += f'<span class="line-number">{i+1}</span>{line}\n'
                        else:
                            code_with_lines += f'<span class="line-number"></span>\n'

                    lang_attr = f' class="language-{lang}"' if lang else ''
                    html = f'<pre class="code-block"><code{lang_attr}>{code_with_lines}</code></pre>'
                else:
                    lang_attr = f' class="language-{lang}"' if lang else ''
                    html = f'<pre class="code-block"><code{lang_attr}>{html_code}</code></pre>'

                text = text.replace(block_id, html)

            elif block_id.startswith("INLINE_CODE_"):
                # Format inline code
                html_code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                html = f'<code class="inline-code">{html_code}</code>'
                text = text.replace(block_id, html)

        return text

    @staticmethod
    def _process_headers(text: str) -> str:
        """Process markdown headers."""
        def header_to_id(match: Match, level: int) -> str:
            header_text = match.group(1)
            header_id = re.sub(r"[^\w]+", "-", header_text.lower())
            return f'<h{level} id="{header_id}">{header_text}</h{level}>'

        # Process ATX headers (# Header)
        for i in range(6, 0, -1):  # Process h6 before h5, etc. to avoid conflicts
            pattern = r'^#{' + str(i) + r'}\s+(.+?)(?:\s+#+)?$'
            text = re.sub(pattern, lambda m: header_to_id(m, i), text, flags=re.MULTILINE)

        # Process Setext headers (Header\n====)
        text = re.sub(r'^(.+)\n=+$', lambda m: header_to_id(m, 1), text, flags=re.MULTILINE)
        text = re.sub(r'^(.+)\n-+$', lambda m: header_to_id(m, 2), text, flags=re.MULTILINE)

        return text

    @staticmethod
    def _process_horizontal_rules(text: str) -> str:
        """Process horizontal rules."""
        text = re.sub(r'^-{3,}$', r'<hr class="elegant-hr">', text, flags=re.MULTILINE)
        text = re.sub(r'^={3,}$', r'<hr class="thick elegant-hr">', text, flags=re.MULTILINE)
        text = re.sub(r'^\*{3,}$', r'<hr class="elegant-hr">', text, flags=re.MULTILINE)
        return text

    @staticmethod
    def _process_blockquotes(text: str) -> str:
        """Process blockquotes."""
        def replace_blockquote(match: Match) -> str:
            content = match.group(1)
            # Remove '>' from the beginning of each line
            content = re.sub(r'^\s*>\s?', '', content, flags=re.MULTILINE)
            # Process nested blockquotes recursively
            if '>' in content:
                content = MarkdownConverter._process_blockquotes(content)
            return f'<blockquote class="elegant-quote">{content}</blockquote>'

        # Find consecutive blockquote lines
        pattern = r'((?:^\s*>.*\n?)+)'
        text = re.sub(pattern, lambda m: replace_blockquote(m), text, flags=re.MULTILINE)

        return text

    @staticmethod
    def _process_lists(text: str) -> str:
        """Process ordered and unordered lists."""
        # Process unordered lists
        def replace_unordered_list(match: Match) -> str:
            content = match.group(0)

            # Split into lines and process
            lines = content.split('\n')

            # Initialize with the first list
            result = ['<ul class="elegant-list">']
            list_stack = [0]  # Stack to track list levels (using integers instead of strings)
            current_level = 0

            for line in lines:
                if not line.strip():
                    continue

                # Check if this is a list item
                list_match = re.match(r'^(\s*)(?:\*|\+|-)\s+(.+)$', line)
                if not list_match:
                    continue

                indent = list_match.group(1)
                item_content = list_match.group(2)
                level = len(indent) // 2

                # Handle level changes
                if level > current_level:
                    # Start a new nested list
                    result.append('<ul class="nested-list">')
                    list_stack.append(level)
                elif level < current_level:
                    # Close nested lists
                    while list_stack and list_stack[-1] > level:
                        result.append('</ul>')
                        list_stack.pop()

                # Add the list item
                result.append(f'<li>{item_content}</li>')
                current_level = level

            # Close any remaining open lists
            while len(list_stack) > 0:
                result.append('</ul>')
                list_stack.pop()

            return '\n'.join(result)

        # Find blocks of unordered lists
        unordered_pattern = r'(?:^(?:\s*)(?:\*|\+|-)\s+.+\n?)+'
        text = re.sub(unordered_pattern, replace_unordered_list, text, flags=re.MULTILINE)

        # Process ordered lists
        def replace_ordered_list(match: Match) -> str:
            content = match.group(0)

            # Split into lines and process
            lines = content.split('\n')
            result = ['<ol class="elegant-list">']

            for line in lines:
                if not line.strip():
                    continue

                # Check if this is a list item
                list_match = re.match(r'^\s*\d+\.\s+(.+)$', line)
                if not list_match:
                    continue

                item_content = list_match.group(1)
                result.append(f'<li>{item_content}</li>')

            result.append('</ol>')
            return '\n'.join(result)

        # Find blocks of ordered lists
        ordered_pattern = r'(?:^\s*\d+\.\s+.+\n?)+'
        text = re.sub(ordered_pattern, replace_ordered_list, text, flags=re.MULTILINE)

        # Process task lists
        def replace_task_list(match: Match) -> str:
            content = match.group(0)

            # Split into lines and process
            lines = content.split('\n')
            result = ['<ul class="task-list">']

            for line in lines:
                if not line.strip():
                    continue

                # Check if this is a task item
                task_match = re.match(r'^\s*-\s+\[([ xX])\]\s+(.+)$', line)
                if not task_match:
                    continue

                is_completed = task_match.group(1).lower() == 'x'
                item_content = task_match.group(2)

                checkbox_class = 'completed' if is_completed else 'pending'
                checkbox_icon = '✓' if is_completed else '○'

                result.append(f'<li class="task-item {checkbox_class}"><span class="checkbox">{checkbox_icon}</span> {item_content}</li>')

            result.append('</ul>')
            return '\n'.join(result)

        # Find blocks of task lists
        task_pattern = r'(?:^\s*-\s+\[[ xX]\]\s+.+\n?)+'
        text = re.sub(task_pattern, replace_task_list, text, flags=re.MULTILINE)

        return text

    @staticmethod
    def _process_tables(text: str) -> str:
        """Process markdown tables."""
        def replace_table(match: Match) -> str:
            table_content = match.group(0)
            rows = table_content.strip().split('\n')

            if len(rows) < 2:
                return table_content

            # Extract header row
            header = rows[0]
            header_cells = [cell.strip() for cell in header.split('|')[1:-1]]

            # Extract alignment row
            alignment = rows[1]
            alignments = []
            for align in alignment.split('|')[1:-1]:
                align = align.strip()
                if align.startswith(':') and align.endswith(':'):
                    alignments.append('center')
                elif align.endswith(':'):
                    alignments.append('right')
                else:
                    alignments.append('left')

            # Build HTML table
            html_table = ['<div class="table-container"><table class="elegant-table">']

            # Add header
            html_table.append('<thead><tr>')
            for i, cell in enumerate(header_cells):
                align = alignments[i] if i < len(alignments) else 'left'
                html_table.append(f'<th align="{align}">{cell}</th>')
            html_table.append('</tr></thead>')

            # Add data rows
            html_table.append('<tbody>')
            for row in rows[2:]:
                if not row.strip():
                    continue

                cells = [cell.strip() for cell in row.split('|')[1:-1]]
                html_table.append('<tr>')

                for i, cell in enumerate(cells):
                    align = alignments[i] if i < len(alignments) else 'left'
                    html_table.append(f'<td align="{align}">{cell}</td>')

                html_table.append('</tr>')

            html_table.append('</tbody></table></div>')

            return '\n'.join(html_table)

        # Find markdown tables
        table_pattern = r'^\|.+\|\n\|[-:]+\|[-:]+\|.+\n(?:\|.+\|\n)+'
        text = re.sub(table_pattern, replace_table, text, flags=re.MULTILINE)

        return text

    @staticmethod
    def _process_images(text: str) -> str:
        """Process markdown images."""
        def replace_image(match: Match) -> str:
            alt_text = match.group(1)
            url = match.group(2)
            title = match.group(3) if match.group(3) else alt_text

            return f'<figure class="elegant-image"><img src="{url}" alt="{alt_text}" title="{title}" loading="lazy"><figcaption>{title}</figcaption></figure>'

        # Find markdown images
        image_pattern = r'!\[(.+?)\]\((.+?)(?:\s+"(.+?)")?\)'
        text = re.sub(image_pattern, replace_image, text)

        return text

    @staticmethod
    def _process_links(text: str) -> str:
        """Process markdown links."""
        def replace_link(match: Match) -> str:
            link_text = match.group(1)
            url = match.group(2)
            title = match.group(3) if match.group(3) else ""

            title_attr = f' title="{title}"' if title else ''
            return f'<a href="{url}"{title_attr} target="_blank" rel="noopener">{link_text}</a>'

        # Find markdown links
        link_pattern = r'\[(.+?)\]\((.+?)(?:\s+"(.+?)")?\)'
        text = re.sub(link_pattern, replace_link, text)

        return text

    @staticmethod
    def _process_emphasis(text: str) -> str:
        """Process markdown emphasis (bold, italic, etc.)."""
        # Process strikethrough
        text = re.sub(r'~~(.+?)~~', r'<del>\1</del>', text)

        # Process bold and italic (nested)
        text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
        text = re.sub(r'___(.+?)___', r'<strong><em>\1</em></strong>', text)

        # Process bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)

        # Process italic
        text = re.sub(r'\*([^\*]+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_([^_]+?)_', r'<em>\1</em>', text)

        return text

    @staticmethod
    def _process_paragraphs(text: str) -> str:
        """Process paragraphs."""
        # Split text into blocks
        blocks = re.split(r'\n{2,}', text)

        for i, block in enumerate(blocks):
            if not block.strip():
                continue

            # Skip blocks that are already HTML elements
            if re.match(r'^\s*<(h[1-6]|ul|ol|pre|blockquote|hr|figure|div|table)', block.strip()):
                continue

            # Wrap in paragraph tags
            blocks[i] = f'<p class="elegant-paragraph">{block}</p>'

        return '\n\n'.join(blocks)

    @staticmethod
    def _postprocess(text: str) -> str:
        """Final cleanup of the HTML."""
        # Remove extra newlines
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Fix any remaining escaped HTML entities
        text = text.replace('&amp;lt;', '&lt;').replace('&amp;gt;', '&gt;')

        return text

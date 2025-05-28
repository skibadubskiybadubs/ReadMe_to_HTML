"""
GitHub README Converter
"""
import os
import re
import base64
import mimetypes
import argparse
import requests
from urllib.parse import urlparse, quote

def download_github_markdown(github_url, github_token=None):
    """
    Download markdown content directly from GitHub
    
    Args:
        github_url (str): URL to the GitHub markdown file
        github_token (str, optional): GitHub personal access token
        
    Returns:
        str: Markdown content
    """
    # Convert GitHub web URL to raw content URL
    if '/blob/' in github_url:
        raw_url = github_url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
    else:
        # If it's already a raw URL, use it directly
        raw_url = github_url
    
    print(f"Fetching markdown from: {raw_url}")
    
    # Set up headers with auth token if provided
    headers = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    try:
        response = requests.get(raw_url, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Failed to download markdown from {raw_url}: {e}")
        return None

def download_and_encode_image(url, github_token=None):
    """
    Download an image from GitHub and encode it as base64
    
    Args:
        url (str): URL of the image
        github_token (str, optional): GitHub personal access token
        
    Returns:
        str: Data URL with base64-encoded image
    """
    try:
        # Set up headers with auth token if provided
        headers = {}
        if github_token:
            headers["Authorization"] = f"token {github_token}"
        
        # Download the image
        print(f"Downloading image: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Get image data
        image_data = response.content
        
        # Determine mime type based on response headers
        content_type = response.headers.get('Content-Type')
        if not content_type or content_type == 'application/octet-stream':
            # Try to guess from URL if not provided in headers
            url_path = urlparse(url).path
            content_type = mimetypes.guess_type(url_path)[0]
            
        # Default to image/png if we can't determine the type
        if not content_type:
            content_type = 'image/png'
            
        # Encode as base64
        encoded = base64.b64encode(image_data).decode('utf-8')
        data_url = f"data:{content_type};base64,{encoded}"
        
        print(f"Successfully encoded image")
        return data_url
    except Exception as e:
        print(f"Failed to download/encode image {url}: {e}")
        return None

def preprocess_markdown(content, github_token=None, github_url=""):
    """
    Preprocess markdown content to embed images as base64
    
    Args:
        content (str): Markdown content
        github_token (str, optional): GitHub personal access token
        github_url (str): Original GitHub URL for resolving relative paths
        
    Returns:
        str: Preprocessed markdown content
    """
    # Keep track of how many images we process
    image_count = 0
    
    # Extract base URL for relative paths
    base_url = ""
    if github_url:
        # Convert GitHub web URL to raw base URL for relative paths
        if '/blob/' in github_url:
            # Extract user, repo, and branch from URL
            parts = github_url.split('/')
            if len(parts) >= 7:
                user = parts[3]
                repo = parts[4]
                branch = parts[6]
                base_url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/"
                print(f"Base URL for relative paths: {base_url}")
            else:
                print(f"Could not extract base URL from GitHub URL: {github_url}")
        else:
            print(f"GitHub URL format not recognized: {github_url}")
    
    # Process GitHub user-attachment URLs in markdown format
    md_pattern = r'!\[(.*?)\]\((https://github\.com/user-attachments/assets/[^)]+)\)'
    
    def replace_md_image(match):
        nonlocal image_count
        alt_text = match.group(1)
        url = match.group(2)
        
        data_url = download_and_encode_image(url, github_token)
        image_count += 1
        
        if data_url:
            return f'<img src="{data_url}" alt="{alt_text}">'
        else:
            # Keep original URL if download failed
            return f'<img src="{url}" alt="{alt_text}">'
    
    modified_content = re.sub(md_pattern, replace_md_image, content)
    
    # Process GitHub user-attachment URLs in HTML format
    html_pattern = r'<img src="(https://github\.com/user-attachments/assets/[^"]+)"([^>]*)>'
    
    def replace_html_image(match):
        nonlocal image_count
        url = match.group(1)
        attrs = match.group(2)
        
        data_url = download_and_encode_image(url, github_token)
        image_count += 1
        
        if data_url:
            return f'<img src="{data_url}"{attrs}>'
        else:
            # Keep original URL if download failed
            return f'<img src="{url}"{attrs}>'
    
    modified_content = re.sub(html_pattern, replace_html_image, modified_content)
    
    # Process relative path images in HTML format
    if base_url:
        relative_html_pattern = r'<img src="([^"]+)"([^>]*)>'
        
        def replace_relative_html_image(match):
            nonlocal image_count
            src = match.group(1)
            attrs = match.group(2)
            
            # Skip if it's already an absolute URL
            if src.startswith(('http://', 'https://', 'data:')):
                return match.group(0)  # Return original
            
            print(f"Processing relative HTML image: {src}")
            
            # Convert relative path to absolute GitHub raw URL
            # Handle path separators and URL encoding
            relative_path = src.replace('\\', '/')
            # URL encode the path components but preserve the forward slashes
            path_parts = relative_path.split('/')
            encoded_parts = [quote(part) for part in path_parts]
            encoded_path = '/'.join(encoded_parts)
            absolute_url = base_url + encoded_path
            
            print(f"Converted to absolute URL: {absolute_url}")
            
            data_url = download_and_encode_image(absolute_url, github_token)
            image_count += 1
            
            if data_url:
                return f'<img src="{data_url}"{attrs}>'
            else:
                # Keep original URL if download failed
                return f'<img src="{absolute_url}"{attrs}>'
        
        modified_content = re.sub(relative_html_pattern, replace_relative_html_image, modified_content)
    
    # Process relative path images in markdown format
    if base_url:
        relative_md_pattern = r'!\[(.*?)\]\(([^)]+)\)'
        
        def replace_relative_md_image(match):
            nonlocal image_count
            alt_text = match.group(1)
            src = match.group(2)
            
            # Skip if it's already an absolute URL
            if src.startswith(('http://', 'https://', 'data:')):
                return match.group(0)  # Return original
            
            print(f"Processing relative Markdown image: {src}")
            
            # Convert relative path to absolute GitHub raw URL
            relative_path = src.replace('\\', '/')
            # URL encode the path components but preserve the forward slashes
            path_parts = relative_path.split('/')
            encoded_parts = [quote(part) for part in path_parts]
            encoded_path = '/'.join(encoded_parts)
            absolute_url = base_url + encoded_path
            
            print(f"Converted to absolute URL: {absolute_url}")
            
            data_url = download_and_encode_image(absolute_url, github_token)
            image_count += 1
            
            if data_url:
                return f'<img src="{data_url}" alt="{alt_text}">'
            else:
                # Keep original URL if download failed
                return f'<img src="{absolute_url}" alt="{alt_text}">'
        
        modified_content = re.sub(relative_md_pattern, replace_relative_md_image, modified_content)
    
    # Process other GitHub image URLs
    other_md_pattern = r'!\[(.*?)\]\((https://github\.com/[^)]+)\)'
    raw_md_pattern = r'!\[(.*?)\]\((https://raw\.githubusercontent\.com/[^)]+)\)'
    camo_md_pattern = r'!\[(.*?)\]\((https://camo\.githubusercontent\.com/[^)]+)\)'
    
    # Combine all these patterns for replacement
    for pattern in [other_md_pattern, raw_md_pattern, camo_md_pattern]:
        modified_content = re.sub(pattern, replace_md_image, modified_content)
    
    # Process HTML img tags with GitHub URLs
    other_html_pattern = r'<img src="(https://github\.com/[^"]+)"([^>]*)>'
    raw_html_pattern = r'<img src="(https://raw\.githubusercontent\.com/[^"]+)"([^>]*)>'
    camo_html_pattern = r'<img src="(https://camo\.githubusercontent\.com/[^"]+)"([^>]*)>'
    
    # Combine all these patterns for replacement
    for pattern in [other_html_pattern, raw_html_pattern, camo_html_pattern]:
        modified_content = re.sub(pattern, replace_html_image, modified_content)
    
    print(f"Processed {image_count} images")
    
    return modified_content

def get_github_css():
    """Get GitHub-like CSS for styling the HTML output"""
    return """
    body {
        font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji";
        font-size: 16px;
        line-height: 1.5;
        word-wrap: break-word;
        padding: 45px;
        max-width: 900px;
        margin: 0 auto;
        color: #24292e;
    }
    
    @media (max-width: 767px) {
        body {
            padding: 15px;
        }
    }
    
    .markdown-body {
        background-color: #ffffff;
    }
    
    .markdown-body h1 {
        padding-bottom: .3em;
        font-size: 2em;
        border-bottom: 1px solid #eaecef;
    }
    
    .markdown-body h2 {
        padding-bottom: .3em;
        font-size: 1.5em;
        border-bottom: 1px solid #eaecef;
    }
    
    .markdown-body h3 {
        font-size: 1.25em;
    }
    
    .markdown-body h4 {
        font-size: 1em;
    }
    
    .markdown-body h5 {
        font-size: 0.875em;
    }
    
    .markdown-body h6 {
        font-size: 0.85em;
        color: #6a737d;
    }
    
    .markdown-body pre {
        padding: 16px;
        overflow: auto;
        font-size: 85%;
        line-height: 1.45;
        background-color: #f6f8fa;
        border-radius: 3px;
    }
    
    .markdown-body blockquote {
        padding: 0 1em;
        color: #6a737d;
        border-left: 0.25em solid #dfe2e5;
    }
    
    .markdown-body blockquote blockquote {
        margin-top: 0.5em;
    }
    
    .markdown-body code {
        padding: 0.2em 0.4em;
        margin: 0;
        font-size: 85%;
        background-color: rgba(27,31,35,0.05);
        border-radius: 3px;
        font-family: SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace;
    }
    
    .markdown-body img {
        max-width: 100%;
        box-sizing: content-box;
        background-color: #fff;
    }
    
    /* Table styling */
    .markdown-body table {
        display: block;
        width: 100%;
        overflow: auto;
        border-spacing: 0;
        border-collapse: collapse;
        margin-bottom: 16px;
    }
    
    .markdown-body table th {
        font-weight: 600;
        padding: 6px 13px;
        border: 1px solid #dfe2e5;
    }
    
    .markdown-body table td {
        padding: 6px 13px;
        border: 1px solid #dfe2e5;
    }
    
    .markdown-body table tr {
        background-color: #fff;
        border-top: 1px solid #c6cbd1;
    }
    
    .markdown-body table tr:nth-child(2n) {
        background-color: #f6f8fa;
    }
    
    /* List styling - properly handle nesting */
    .markdown-body ul,
    .markdown-body ol {
        padding-left: 2em;
        margin-top: 0;
        margin-bottom: 16px;
    }
    
    .markdown-body ul ul,
    .markdown-body ul ol,
    .markdown-body ol ol,
    .markdown-body ol ul {
        margin-top: 0;
        margin-bottom: 0;
    }
    
    .markdown-body li {
        word-wrap: break-all;
    }
    
    .markdown-body li > p {
        margin-top: 16px;
    }
    
    .markdown-body li + li {
        margin-top: 0.25em;
    }
    
    /* Specific styling for circle and square bullets */
    .markdown-body ul {
        list-style-type: disc;
    }
    
    .markdown-body ul ul {
        list-style-type: circle;
    }
    
    .markdown-body ul ul ul {
        list-style-type: square;
    }
    
    /* Proper styling for code blocks */
    .markdown-body pre > code {
        padding: 0;
        margin: 0;
        font-size: 100%;
        word-break: normal;
        white-space: pre;
        background: transparent;
        border: 0;
    }
    
    /* GitHub-style alerts/callouts */
    .markdown-body .tip {
        padding: 0.5em 1em;
        margin: 1em 0;
        border-left: 0.25em solid #22863a;
        background-color: #f0fff4;
    }
    
    .markdown-body .warning {
        padding: 0.5em 1em;
        margin: 1em 0;
        border-left: 0.25em solid #f9c513;
        background-color: #fffbdd;
    }
    
    .markdown-body .important {
        padding: 0.5em 1em;
        margin: 1em 0;
        border-left: 0.25em solid #cb2431;
        background-color: #ffeef0;
    }
    
    .markdown-body .note {
        padding: 0.5em 1em;
        margin: 1em 0;
        border-left: 0.25em solid #0366d6;
        background-color: #f1f8ff;
    }
    
    /* For code with no specified language */
    .markdown-body .highlight {
        background-color: #f6f8fa;
    }
    
    /* Additional styles for specific markdown elements */
    .markdown-body del {
        text-decoration: line-through;
    }
    
    .markdown-body ins {
        text-decoration: underline;
    }
    
    .markdown-body sub {
        vertical-align: sub;
        font-size: smaller;
    }
    
    .markdown-body sup {
        vertical-align: super;
        font-size: smaller;
    }
    
    /* Dark theme styles - optional */
    @media (prefers-color-scheme: dark) {
        body {
            background-color: #0d1117;
            color: #c9d1d9;
        }
        
        .markdown-body {
            background-color: #0d1117;
            color: #c9d1d9;
        }
        
        .markdown-body h1,
        .markdown-body h2 {
            border-bottom-color: #21262d;
        }
        
        .markdown-body blockquote {
            color: #8b949e;
            border-left-color: #3b434b;
        }
        
        .markdown-body code {
            background-color: rgba(110,118,129,0.4);
        }
        
        .markdown-body pre {
            background-color: #161b22;
        }
        
        .markdown-body table th,
        .markdown-body table td {
            border-color: #30363d;
        }
        
        .markdown-body table tr {
            background-color: #0d1117;
            border-top-color: #21262d;
        }
        
        .markdown-body table tr:nth-child(2n) {
            background-color: #161b22;
        }
    }
    """

def format_text(text):
    """
    Apply markdown formatting to text (bold, italic, code, links)
    
    Args:
        text (str): Text to format
        
    Returns:
        str: Formatted HTML
    """
    # Format bold text - **text**
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Format italic text - *text*
    text = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    
    # Format strikethrough text - ~~text~~
    text = re.sub(r'~~(.*?)~~', r'<del>\1</del>', text)
    
    # Format code - `text`
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    
    # Format links - [text](url)
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
    
    # Already HTML tags like <ins>, <sub>, <sup> should be preserved as-is
    
    return text

def parse_nested_blockquotes(blockquote_lines):
    """
    Parse a list of blockquote lines into properly nested HTML
    
    Args:
        blockquote_lines (list): List of lines starting with >
        
    Returns:
        str: HTML with properly nested blockquotes
    """
    html_output = []
    current_level = 0
    
    # Stack to track blockquote levels
    blockquote_stack = []
    
    for line in blockquote_lines:
        # Count the number of '>' characters to determine nesting level
        match = re.match(r'^(>+)\s*(.*?)$', line)
        if not match:
            continue
            
        level = len(match.group(1))
        content = match.group(2)
        
        # Adjust the blockquote nesting
        if level > current_level:
            # Open new blockquotes
            for _ in range(level - current_level):
                html_output.append('<blockquote>')
                blockquote_stack.append(level)
        elif level < current_level:
            # Close blockquotes
            for _ in range(current_level - level):
                html_output.append('</blockquote>')
                if blockquote_stack:
                    blockquote_stack.pop()
        
        # Add the content if not empty
        if content.strip():
            formatted_content = format_text(content)
            html_output.append(f'<p>{formatted_content}</p>')
        
        current_level = level
    
    # Close any remaining open blockquotes
    while blockquote_stack:
        html_output.append('</blockquote>')
        blockquote_stack.pop()
    
    return ''.join(html_output)

def parse_markdown_table(table_block):
    """
    Parse a markdown table block and convert to HTML table
    
    Args:
        table_block (str): Markdown table text
        
    Returns:
        str: HTML table
    """
    lines = table_block.strip().split('\n')
    
    # Ensure we have at least a header row and separator
    if len(lines) < 2:
        return f"<p>{table_block}</p>"
    
    # Process header row
    header_row = lines[0].strip()
    headers = [cell.strip() for cell in header_row.split('|')]
    
    # Remove empty cells at start/end if the row started/ended with |
    if not headers[0]:
        headers = headers[1:]
    if not headers[-1]:
        headers = headers[:-1]
    
    # Check for separator row (row with dashes)
    separator_row = lines[1].strip()
    separator_cells = separator_row.split('|')
    
    # Make sure this is a proper table separator
    if len(separator_cells) < len(headers):
        # Not a proper table, just return as text
        return f"<p>{table_block}</p>"
    
    # Check if each cell in separator row contains mostly dashes
    if not all(cell.strip() == '' or all(c in '-:' for c in cell.strip()) for cell in separator_cells[1:-1]):
        # Not a proper table, just return as text
        return f"<p>{table_block}</p>"
    
    # Process data rows
    html_rows = []
    
    # Add header row
    header_html = "<tr>"
    for header in headers:
        formatted_header = format_text(header)
        header_html += f"<th>{formatted_header}</th>"
    header_html += "</tr>"
    html_rows.append(header_html)
    
    # Add data rows (skip separator row)
    for line in lines[2:]:
        if not line.strip():
            continue
            
        cells = [cell.strip() for cell in line.split('|')]
        
        # Remove empty cells at start/end if the row started/ended with |
        if not cells[0]:
            cells = cells[1:]
        if not cells[-1]:
            cells = cells[:-1]
        
        row_html = "<tr>"
        for cell in cells:
            formatted_cell = format_text(cell)
            row_html += f"<td>{formatted_cell}</td>"
        row_html += "</tr>"
        html_rows.append(row_html)
    
    # Create the complete table
    table_html = f"<table>\n{''.join(html_rows)}\n</table>"
    return table_html

def parse_list_items(lines):
    """
    Parse a list of markdown lines into a structured HTML list
    with proper nesting and formatting
    
    Args:
        lines (list): List of markdown lines
        
    Returns:
        str: HTML list
    """
    html_output = []
    stack = []  # Stack of (level, list_type) to track nesting
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip empty lines
        if not line.strip():
            i += 1
            continue
        
        # Check for code blocks within list items
        if re.match(r'^\s*```', line):
            code_block = []
            lang_match = re.match(r'^\s*```(.*)$', line)
            language = lang_match.group(1).strip() if lang_match else ""
            i += 1
            
            # Collect code block content
            while i < len(lines) and not re.match(r'^\s*```', lines[i]):
                code_block.append(lines[i])
                i += 1
                
            # Skip closing ```
            if i < len(lines):
                i += 1
                
            # Add code block to output
            code_content = '\n'.join(code_block)
            code_content = code_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            if language:
                html_output.append(f'<pre><code class="language-{language}">{code_content}</code></pre>')
            else:
                html_output.append(f'<pre><code>{code_content}</code></pre>')
            continue
        
        # Check for ordered list item
        ol_match = re.match(r'^(\s*)(\d+)\.\s+(.*)$', line)
        # Check for unordered list item
        ul_match = re.match(r'^(\s*)[-*•○]\s+(.*)$', line)
        
        if ol_match:
            indent, number, content = ol_match.groups()
            indent_level = len(indent) // 2  # Assuming 2 spaces per indent level
            list_type = 'ol'
        elif ul_match:
            indent, content = ul_match.groups()
            indent_level = len(indent) // 2
            list_type = 'ul'
        else:
            # Handle content that's part of the previous list item
            if stack:
                last_level = stack[-1][0]
                current_indent = len(line) - len(line.lstrip())
                if current_indent >= last_level * 2:  # Indented enough to be part of the list
                    formatted_line = format_text(line.strip())
                    html_output.append(f"<p>{formatted_line}</p>")
                    i += 1
                    continue
            
            # Not a list item and not part of one
            break
        
        # Process content for formatting
        formatted_content = format_text(content)
        
        # Adjust the stack based on current indentation level
        while stack and stack[-1][0] >= indent_level:
            closed_level, closed_type = stack.pop()
            html_output.append(f"</{closed_type}>")
        
        # Start a new list if necessary
        if not stack or stack[-1][0] < indent_level:
            html_output.append(f"<{list_type}>")
            stack.append((indent_level, list_type))
        
        # Add the list item
        html_output.append(f"<li>{formatted_content}")
        
        # Look ahead to next line
        if i + 1 < len(lines):
            next_line = lines[i + 1]
            next_ol_match = re.match(r'^(\s*)(\d+)\.\s+', next_line) if next_line.strip() else None
            next_ul_match = re.match(r'^(\s*)[-*•○]\s+', next_line) if next_line.strip() else None
            
            # If next line is a list item at same or higher level, close this item
            if next_ol_match or next_ul_match:
                next_indent = len(next_ol_match.group(1) if next_ol_match else next_ul_match.group(1))
                next_level = next_indent // 2
                
                if next_level <= indent_level:
                    html_output.append("</li>")
            else:
                # Check if next line is a code block or content for this item
                if not next_line.strip() or re.match(r'^\s*```', next_line) or (next_line.strip() and len(next_line) - len(next_line.lstrip()) > indent_level * 2):
                    # Don't close the list item yet
                    pass
                else:
                    html_output.append("</li>")
        else:
            # End of the list, close the item
            html_output.append("</li>")
        
        i += 1
    
    # Close any remaining open lists
    while stack:
        closed_level, closed_type = stack.pop()
        if html_output and not html_output[-1].endswith("</li>"):
            html_output.append("</li>")
        html_output.append(f"</{closed_type}>")
    
    return ''.join(html_output)

def convert_markdown_to_html(markdown_text, github_url=""):
    """
    Convert markdown text to HTML with proper formatting
    
    Args:
        markdown_text (str): Markdown content
        github_url (str): GitHub URL for title
        
    Returns:
        str: HTML content
    """
    # Initialize HTML components
    html_output = []
    lines = markdown_text.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Skip empty lines
        if not line.strip():
            i += 1
            continue
        
        # Check for headers
        header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if header_match:
            level = len(header_match.group(1))
            text = header_match.group(2)
            formatted_text = format_text(text)
            html_output.append(f"<h{level}>{formatted_text}</h{level}>")
            i += 1
            continue
        
        # Check for code blocks - properly handle indented code blocks
        if re.match(r'^\s*```', line):
            code_block = []
            # Extract language and remove the ```
            lang_match = re.match(r'^\s*```(.*)$', line)
            language = lang_match.group(1).strip() if lang_match else ""
            i += 1
            
            # Collect all lines until closing ```
            while i < len(lines) and not re.match(r'^\s*```', lines[i]):
                code_block.append(lines[i])
                i += 1
            
            # Skip the closing ```
            if i < len(lines):
                i += 1
            
            # Preserve exact formatting including whitespace
            code_content = '\n'.join(code_block)
            
            # Escape HTML entities
            code_content = code_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            if language:
                html_output.append(f'<pre><code class="language-{language}">{code_content}</code></pre>')
            else:
                html_output.append(f'<pre><code>{code_content}</code></pre>')
            continue
        
        # Check for blockquotes with proper nesting
        if line.startswith('>'):
            blockquote_lines = [line]
            i += 1
            
            # Collect all blockquote lines
            while i < len(lines) and (lines[i].startswith('>') or not lines[i].strip()):
                if lines[i].strip():  # Skip empty lines but keep track of them
                    blockquote_lines.append(lines[i])
                i += 1
            
            blockquote_html = parse_nested_blockquotes(blockquote_lines)
            html_output.append(blockquote_html)
            continue
        
        # Check for tables
        if '|' in line and i + 1 < len(lines) and '|' in lines[i + 1] and '-' in lines[i + 1]:
            # Collect all table lines
            table_lines = [line]
            i += 1
            while i < len(lines) and '|' in lines[i]:
                table_lines.append(lines[i])
                i += 1
            
            table_html = parse_markdown_table('\n'.join(table_lines))
            html_output.append(table_html)
            continue
        
        # Check for lists
        list_match = re.match(r'^(\s*)(\d+\.|[-*•○])\s+', line)
        if list_match:
            # Collect all list items
            list_lines = []
            
            while i < len(lines):
                current = lines[i]
                if not current.strip():
                    list_lines.append(current)
                    i += 1
                    continue
                    
                current_match = re.match(r'^(\s*)(\d+\.|[-*•○])\s+', current)
                
                # If it's a list item or empty line or indented content, include it
                if current_match or re.match(r'^\s+', current):
                    list_lines.append(current)
                    i += 1
                elif re.match(r'^\s*```', current):
                    # It's a code block within the list
                    list_lines.append(current)
                    i += 1
                    
                    # Collect code block content
                    while i < len(lines) and not re.match(r'^\s*```', lines[i]):
                        list_lines.append(lines[i])
                        i += 1
                    
                    # Add closing code fence if found
                    if i < len(lines):
                        list_lines.append(lines[i])
                        i += 1
                else:
                    # Not a list-related line, end list processing
                    break
            
            list_html = parse_list_items(list_lines)
            html_output.append(list_html)
            continue
        
        # Regular paragraph
        paragraph_lines = [line]
        i += 1
        
        # Collect all lines for this paragraph
        while i < len(lines) and lines[i].strip() and not (
            re.match(r'^(#{1,6}|\d+\.|[-*•○]|>|```|\|)\s+', lines[i]) or 
            re.match(r'^\s*```', lines[i])
        ):
            paragraph_lines.append(lines[i])
            i += 1
        
        # Preserve spacing by joining with space only if needed
        paragraph_text = ' '.join(line.rstrip() for line in paragraph_lines)
        formatted_paragraph = format_text(paragraph_text)
        html_output.append(f"<p>{formatted_paragraph}</p>")
    
    return '\n'.join(html_output)

def convert_github_url_to_html(github_url, output_path, github_token=None):
    """
    Download markdown from GitHub URL and convert to HTML
    
    Args:
        github_url (str): URL to the GitHub markdown file
        output_path (str): Path to save the HTML file
        github_token (str, optional): GitHub personal access token
        
    Returns:
        str: Path to the created HTML file
    """
    # Download markdown content
    content = download_github_markdown(github_url, github_token)
    
    if not content:
        print(f"Failed to download markdown from {github_url}")
        return None
    
    # Preprocess markdown to embed images as base64
    modified_content = preprocess_markdown(content, github_token, github_url)
    
    # Convert markdown to HTML
    html_body = convert_markdown_to_html(modified_content, github_url)
    
    # Extract repo/file name from URL for the title
    url_parts = github_url.split('/')
    if len(url_parts) >= 5:
        repo_name = url_parts[4]  # Repo name is typically the 5th part of the URL
        file_name = url_parts[-1] if url_parts[-1] else "README.md"
    else:
        repo_name = "GitHub"
        file_name = "README"
    
    # Create full HTML document
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{repo_name} - {file_name}</title>
    <style>
{get_github_css()}
    </style>
</head>
<body>
    <div class="markdown-body">
{html_body}
    </div>
</body>
</html>"""
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Write HTML to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Successfully converted to HTML: {output_path}")
    
    return output_path

def main():
    parser = argparse.ArgumentParser(description="Convert GitHub README URL to HTML with perfect formatting")
    parser.add_argument("github_url", help="URL to the GitHub README file")
    parser.add_argument("output_path", help="Path to save the HTML file")
    parser.add_argument("-t", "--token", help="GitHub personal access token")
    
    args = parser.parse_args()
    
    convert_github_url_to_html(
        args.github_url,
        args.output_path,
        args.token
    )

if __name__ == "__main__":
    main()
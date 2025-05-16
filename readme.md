# GitHub README Converter

Convert any GitHub README file to a self-contained HTML file with embedded images. No API limits, no dependencies on GitHub for rendering.

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)

## 🌟 Features

- **Direct URL Conversion**: Convert any GitHub README URL directly to HTML
- **No API Limits**: Doesn't use GitHub's API, so no rate limiting
- **Offline Access**: All images are embedded as base64 directly in the HTML
- **GitHub Styling**: Renders with GitHub's clean, familiar style
- **Private Repository Support**: Access private repos with a GitHub token
- **GitHub Callouts Support**: Properly renders tip/note/warning/important callouts
- **Self-Contained**: Single HTML file with everything included

## 📋 Requirements

- Python 3.6 or higher
- `markdown` and `requests` libraries

## 🚀 Installation

1. Clone this repository or download the script file:
```bash
git clone https://github.com/yourusername/github-readme-converter.git
cd github-readme-converter
```

2. Install required packages:
```bash
pip install markdown requests
```

## 💻 Usage

### Basic Usage

Convert a GitHub README to HTML:

```bash
python ReadmeToHTML.py "https://github.com/username/repo/blob/main/README.md" "output.html"
```

### Arguments

- **github_url**: URL to the GitHub README file
- **output_path**: Path where to save the HTML file
- **-t, --token**: (Optional) GitHub personal access token for private repos

### Examples

1. Convert a README with a specific output location:
```bash
python ReadmeToHTML.py "https://github.com/skibadubskiybadubs/energyplus_multiprocessing/blob/main/readme.md" "C:/Output/energyplus_readme.html"
```

2. Access a private repository:
```bash
python ReadmeToHTML.py "https://github.com/username/private-repo/blob/main/README.md" "output.html" -t YOUR_GITHUB_TOKEN
```

## 🔍 How It Works

1. **Downloads Markdown**: Fetches the raw markdown content from GitHub
2. **Processes Images**: Downloads each image and encodes it as base64
3. **Converts Markdown**: Transforms markdown to HTML using Python's markdown library
4. **Adds GitHub Styling**: Includes CSS to match GitHub's styling
5. **Creates Self-Contained File**: Saves everything in a single HTML file

## 🔒 Private Repository Access

To access private repositories:

1. Create a GitHub personal access token:
   - Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate a new token with the "repo" scope
   - Copy the generated token

2. Use the token with the script:
```bash
python ReadmeToHTML.py "https://github.com/username/private-repo/blob/main/README.md" "output.html" -t YOUR_GITHUB_TOKEN
```

## ⚠️ Troubleshooting

### Image Download Issues

If images aren't being downloaded correctly:
- Check your internet connection
- Verify you have proper access to the repository
- For private repos, ensure your token has sufficient permissions

### Markdown Rendering Issues

If markdown isn't rendering correctly:
- Make sure you have the latest version of the `markdown` package
- Try using additional markdown extensions if needed

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🙏 Acknowledgements

- Python Markdown library
- Requests library
- GitHub for the styling inspiration

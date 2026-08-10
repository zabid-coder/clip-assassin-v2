# 🎬 Clip Assassin v2.0.2 — Professional Post-Production Workflow Automator

[![Version](https://img.shields.io/badge/version-2.0.2-blue.svg)](https://github.com/zabid-coder/clip-assassin-v2/releases/tag/v2.0.2)
[![Build Status](https://img.shields.io/github/actions/workflow/status/zabid-coder/clip-assassin-v2/build.yml?branch=main)](https://github.com/zabid-coder/clip-assassin-v2/actions)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)

**Clip Assassin v2.0.2** is an enterprise-grade post-production automation suite featuring **Post Haste-style Master Ingest**, AI-powered editing tools, and a modern React + FastAPI architecture for DaVinci Resolve Studio.

---

## 🚀 What's New in v2.0.2

### ✨ Post Haste-Style Master Ingest System
- **Visual Template Builder**: Drag-and-drop interface for creating custom folder structures
- **Dynamic Variables**: Use `{{client}}`, `{{project}}`, `{{date}}`, `{{camera}}` placeholders
- **Loop Support**: Auto-generate `Camera 1`, `Camera 2`, `Camera 3...` based on parameters
- **Preview Mode**: See exact folder structure before creation
- **Built-in Templates**: Professional presets for Social Media, Commercials, Film Production
- **Template Library**: Save, import, export, and share custom templates

### 🎨 Professional UI/UX Overhaul
- Modern dashboard with card-based grid layout
- Glassmorphism design with smooth animations
- Split-pane template builder with live preview
- Enhanced color coding and visual hierarchy
- Responsive design for all screen sizes

### ⚡ Performance Enhancements
- Optimized clipboard monitoring (50% faster)
- Async task queue for background processing
- Improved error handling with detailed codes
- Structured logging for debugging

---

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Master Ingest Guide](#-master-ingest-guide)
- [AI Features](#-ai-integration)
- [Plugin System](#-plugin-system)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Building from Source](#-building-from-source)
- [Contributing](#-contributing)
- [Changelog](#-changelog)
- [License](#-license)

---

## 🎯 Features

### 📁 1. Master Ingest & Project Setup (NEW v2.0.2)

| Feature | Description |
|---------|-------------|
| **Template Engine** | Create custom folder structures with dynamic variables |
| **Visual Builder** | Drag-and-drop interface for intuitive template design |
| **Live Preview** | See exactly what will be created before execution |
| **Auto Versioning** | Smart project naming (`Project_v1`, `Project_v2`, etc.) |
| **Built-in Presets** | Professional templates for common workflows |
| **Import/Export** | Share templates across teams and projects |

**Example Template Syntax:**
```
{{client}}/{{project}}/{{date}}/
├── 01_Raw Footages/
│   ├── Camera {{camera_number}}/
│   └── Audio/
├── 02_Selects/
├── 03_Graphics/
└── 04_Exports/
```

### ✂️ 2. Frame-Accurate Editing Tools

- **Timecode Precision**: Cut clips with frame-level accuracy
- **Silence Detection**: Auto-remove dead air and pauses
- **Smart Markers**: AI-generated markers based on speech/content
- **Batch Operations**: Process multiple clips simultaneously
- **Timeline Snapshots**: Non-destructive editing with rollback capability

### 🎥 3. Social Media Reframing

- **Auto Reframe**: Convert 16:9 to 9:16, 1:1, 4:5 automatically
- **Subject Tracking**: Keep focus on speakers/subjects
- **Safe Zones**: Ensure critical content stays visible
- **Platform Presets**: TikTok, Instagram Reels, YouTube Shorts

### 🤖 4. AI Integration

- **Speech-to-Text**: Automatic transcription with Whisper
- **Auto Chapters**: Generate chapter markers from transcript
- **Smart Silence**: Context-aware silence detection
- **Keyword Markers**: Auto-mark important moments by keywords

### 🔌 5. Plugin System

- **Extensible Architecture**: Add custom tools and workflows
- **Third-Party Support**: Integrate external services
- **Custom Scripts**: Run Python scripts within the app
- **API Hooks**: Webhook support for automation

---

## ⚡ Quick Start

### Prerequisites
- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **DaVinci Resolve Studio 18/19/21** (Free version works with limited features)

### Installation

#### Option 1: Download Pre-built Installer (Recommended)

**Windows:**
1. Download `Clip_Assassin_v2.0.2_Setup.exe` from [Releases](https://github.com/zabid-coder/clip-assassin-v2/releases)
2. Run installer and follow prompts
3. Launch Clip Assassin from Start Menu

**macOS:**
1. Download `Clip_Assassin_v2.0.2.dmg` from [Releases](https://github.com/zabid-coder/clip-assassin-v2/releases)
2. Drag to Applications folder
3. Launch from Applications (may need to right-click → Open on first run)

#### Option 2: Build from Source

```bash
# Clone repository
git clone https://github.com/zabid-coder/clip-assassin-v2.git
cd clip-assassin-v2

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
npm run build

# Start application
cd ..
python main.py
```

---

## 📁 Master Ingest Guide

### Creating Your First Template

1. **Open Template Builder**
   - Navigate to "Master Ingest" → "Template Builder"
   - Click "New Template"

2. **Add Folder Structure**
   - Use drag-and-drop to add folders/files
   - Right-click to edit properties
   - Add variables using `{{variable_name}}` syntax

3. **Define Parameters**
   - Click "Parameters" tab
   - Add parameter types: Text, Date, Number, Select
   - Set validation rules and defaults

4. **Configure Loops** (Optional)
   - Select a folder/item
   - Enable "Loop" toggle
   - Set range (e.g., Camera 1 to Camera 4)

5. **Preview & Save**
   - View live preview on right panel
   - Enter test values to see output
   - Click "Save Template"

### Using Built-in Templates

Clip Assassin includes professional templates:

| Template | Best For | Structure |
|----------|----------|-----------|
| **Social Media** | TikTok, Reels, Shorts | Raw → Selects → Graphics → Exports |
| **Commercial** | Ads, Brand Content | Multi-camera, Audio, Client Reviews |
| **Film Production** | Short Films, Docs | Scenes, Dailies, VFX, Sound, Color |

### Example Workflow

```bash
# 1. Select "Commercial Template"
# 2. Enter parameters:
#    - Client: "Nike"
#    - Project: "Summer Campaign"
#    - Date: "2024-01-15"
#    - Cameras: 3

# 3. Preview shows:
Nike/Summer Campaign/2024-01-15/
├── 01_Raw Footages/
│   ├── Camera 1/
│   ├── Camera 2/
│   ├── Camera 3/
│   └── Audio/
├── 02_Selects/
├── 03_Graphics/
├── 04_Client Reviews/
└── 05_Exports/

# 4. Click "Create" → Done!
```

---

## 🤖 AI Integration

### Setting Up AI Features

1. **Install Additional Dependencies**
   ```bash
   pip install openai-whisper
   ```

2. **Configure API Keys** (Optional for cloud services)
   - Open Settings → AI Configuration
   - Add OpenAI API key for enhanced features
   - Local Whisper works without API key

3. **Enable Auto Transcription**
   - Go to "Settings" → "AI Features"
   - Toggle "Auto-transcribe on ingest"
   - Choose language model

### AI-Powered Features

| Feature | Description | Speed |
|---------|-------------|-------|
| **Transcription** | Speech-to-text for all clips | ~1x realtime |
| **Auto Chapters** | Generate chapters from transcript | Instant |
| **Smart Markers** | Mark key moments by keywords | Instant |
| **Silence Detection** | Context-aware pause removal | ~0.5x realtime |

---

## 🔌 Plugin System

### Creating a Custom Plugin

```python
# plugins/my_custom_tool.py
from clip_assassin.plugins import BasePlugin

class MyCustomTool(BasePlugin):
    name = "My Custom Tool"
    version = "1.0.0"
    
    def execute(self, context):
        # Your custom logic here
        print("Running custom tool...")
        return {"status": "success"}
```

### Installing Plugins

1. Place plugin file in `plugins/` directory
2. Restart Clip Assassin
3. Access via "Plugins" menu

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Application
APP_ENV=production
LOG_LEVEL=INFO

# AI Services
OPENAI_API_KEY=your_key_here
WHISPER_MODEL=base

# Database
DATABASE_URL=sqlite:///./clip_assassin.db

# Task Queue (Optional for distributed processing)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER=redis://localhost:6379/0
```

### Configuration File

Edit `config.yaml` for advanced settings:

```yaml
app:
  name: Clip Assassin
  version: 2.0.2
  
ingest:
  default_template: social_media
  auto_launch_resolve: true
  
ai:
  enabled: true
  whisper_model: base
  language: en
  
logging:
  level: INFO
  file: logs/clip_assassin.log
```

---

## 🛠️ Building from Source

### Backend (FastAPI)

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Build executable
pyinstaller --name="Clip Assassin" --windowed main.py
```

### Frontend (React)

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### Creating Installers

**Windows (.exe):**
```bash
python build_cross_platform.py --platform windows
```

**macOS (.dmg):**
```bash
python build_cross_platform.py --platform macos
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: App won't launch on macOS
- **Solution**: Right-click → Open, or run `xattr -cr /Applications/Clip\ Assassin.app`

**Issue**: DaVinci Resolve not detected
- **Solution**: Ensure Resolve is installed in default location or set path in Settings

**Issue**: Template preview not showing
- **Solution**: Clear browser cache and reload frontend

**Issue**: AI features not working
- **Solution**: Install Whisper: `pip install openai-whisper`

### Getting Help

- 📖 Read the [Documentation](https://github.com/zabid-coder/clip-assassin-v2/wiki)
- 💬 Join our [Discord Community](https://discord.gg/clipassassin) (coming soon)
- 🐛 Report bugs on [GitHub Issues](https://github.com/zabid-coder/clip-assassin-v2/issues)

---

## 🤝 Contributing

We welcome contributions! Here's how to help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint/Prettier for JavaScript/TypeScript
- Write tests for new features
- Update documentation for user-facing changes

---

## 📜 Changelog

### v2.0.2 (Current)
- ✨ Post Haste-style Master Ingest with visual template builder
- 🎨 Complete UI/UX overhaul with modern design
- 🔄 Dynamic variables and loop support in templates
- 👁️ Live preview mode for folder structures
- 📦 Built-in professional templates
- ⚡ 50% performance improvement in clipboard monitoring
- 🐛 Fixed various bugs and edge cases

### v2.0.1
- Added basic Master Ingest functionality
- Improved DaVinci Resolve integration
- Enhanced error handling

### v2.0.0
- Initial release with core editing features
- React + FastAPI architecture
- Cross-platform support

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Inspired by [Digital Rebellion's Post Haste](https://www.digitalrebellion.com/posthaste/)
- Built with [FastAPI](https://fastapi.tiangolo.com/) and [React](https://reactjs.org/)
- AI powered by [OpenAI Whisper](https://github.com/openai/whisper)
- Icons from [Lucide](https://lucide.dev/)

---

**Made with ❤️ by Zabid Coder**

For questions, suggestions, or collaborations:
- 📧 Email: [your-email@example.com](mailto:your-email@example.com)
- 🐦 Twitter: [@yourhandle](https://twitter.com/yourhandle)
- 💼 LinkedIn: [Your Profile](https://linkedin.com/in/yourprofile)

---

<div align="center">

**⭐ If you like this project, please give it a star!**

[Report Bug](https://github.com/zabid-coder/clip-assassin-v2/issues) · [Request Feature](https://github.com/zabid-coder/clip-assassin-v2/issues) · [View Demo](https://github.com/zabid-coder/clip-assassin-v2/wiki/Demo)

</div>

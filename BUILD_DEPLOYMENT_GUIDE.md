# 🚀 Clip Assassin - Build & Deployment Guide

## Overview
This guide explains how to build production-ready installers for macOS (.dmg) and Windows (.exe) and deploy them via GitHub.

## ✅ Verified Build Status

### Current Build (Linux Environment)
- **Frontend**: ✅ Built successfully (`frontend/dist/`)
- **Backend Executable**: ✅ Built successfully (`dist/Clip Assassin/`)
- **Size**: ~13.6 MB (Linux portable)

### Platform-Specific Builds
To create final installers, you need to run the build on each target platform:

| Platform | Output File | Build Requirement |
|----------|-------------|-------------------|
| **macOS** | `Clip_Assassin_v2.0.1.dmg` | macOS with Xcode Command Line Tools |
| **Windows** | `Clip_Assassin_v2.0.1_Setup.exe` | Windows with Inno Setup |

---

## 📋 Prerequisites

### For All Platforms
```bash
# Python 3.8+
python --version

# Node.js 18+
node --version

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend && npm install
```

### macOS Specific
```bash
# Xcode Command Line Tools
xcode-select --install

# Verify hdiutil and codesign exist
which hdiutil
which codesign
```

### Windows Specific
```powershell
# Inno Setup (download from https://jrsoftware.org/isdl.php)
# Or install via Chocolatey:
choco install innosetup

# Verify ISCC compiler
iscc
```

---

## 🔨 Building on Each Platform

### Option 1: Automated Cross-Platform Build Script

Run the enhanced build script on each platform:

```bash
python build_cross_platform.py
```

This script will:
1. Build the React frontend
2. Run PyInstaller with platform-specific options
3. Create .dmg (macOS) or .iss installer script (Windows)
4. Verify the build outputs
5. Generate a BUILD_README.md

### Option 2: Manual Build Steps

#### macOS Build
```bash
# 1. Build frontend
cd frontend && npm run build

# 2. Build app bundle
pyinstaller --noconfirm --clean --windowed \
  --name="Clip Assassin" \
  --icon=app_icon.icns \
  --osx-bundle-identifier=com.zabidstudio.clipassassin \
  --target-architecture=universal2 \
  --add-data="frontend/dist:frontend/dist" \
  --add-data="presets:presets" \
  --add-data="templates:templates" \
  --collect-all=pywebview \
  --collect-all=uvicorn \
  --collect-all=fastapi \
  desktop_app.py

# 3. Create DMG
mkdir dist/dmg_contents
cp -r "dist/Clip Assassin.app" dist/dmg_contents/
ln -s /Applications dist/dmg_contents/Applications

hdiutil create -volname "Clip Assassin" \
  -srcfolder dist/dmg_contents \
  -ov -format UDRO dist/temp.dmg

hdiutil convert dist/temp.dmg \
  -format UDZO -imagekey zlib-level=9 \
  -o "dist/Clip_Assassin_v2.0.1.dmg"

rm dist/temp.dmg
rm -rf dist/dmg_contents
```

#### Windows Build
```powershell
# 1. Build frontend
cd frontend
npm run build

# 2. Build executable
pyinstaller --noconfirm --clean --windowed `
  --name="Clip Assassin" `
  --icon=icon.ico `
  --add-data="frontend/dist;frontend/dist" `
  --add-data="presets;presets" `
  --add-data="templates;templates" `
  --collect-all=pywebview `
  --collect-all=uvicorn `
  --collect-all=fastapi `
  desktop_app.py

# 3. Create installer with Inno Setup
iscc.exe clip_assassin_installer.iss
```

---

## 🧪 Testing the Build

### Before Distribution

#### macOS Testing Checklist
- [ ] Open DMG on clean macOS system (10.15+)
- [ ] Drag to Applications folder
- [ ] Launch app (may require Right-click → Open first time)
- [ ] Verify DaVinci Resolve connection works
- [ ] Test all major features:
  - [ ] Cut tools
  - [ ] Master ingest
  - [ ] Export/rendering
  - [ ] Settings persistence
- [ ] Check app doesn't crash on quit

#### Windows Testing Checklist
- [ ] Run installer on clean Windows 10+ system
- [ ] Verify Start Menu and Desktop shortcuts created
- [ ] Launch app as Administrator first time
- [ ] Verify DaVinci Resolve connection works
- [ ] Test all major features:
  - [ ] Cut tools
  - [ ] Master ingest
  - [ ] Export/rendering
  - [ ] Settings persistence
- [ ] Test uninstaller works correctly

---

## 📤 Uploading to GitHub

### Option 1: Manual Upload

1. Go to your GitHub repository
2. Click **Releases** → **Create a new release**
3. Tag version: `v2.0.1`
4. Upload files:
   - `Clip_Assassin_v2.0.1.dmg` (macOS)
   - `Clip_Assassin_v2.0.1_Setup.exe` (Windows)
5. Add release notes (see template below)
6. Publish release

### Option 2: Automated via GitHub Actions

The repository includes a CI/CD workflow that automatically builds and creates releases:

```bash
# Tag a release
git tag v2.0.1
git push origin v2.0.1
```

GitHub Actions will:
1. Build on macOS runner → creates .dmg
2. Build on Windows runner → creates .exe installer
3. Create GitHub Release with both files attached

---

## 📝 Release Notes Template

```markdown
## Clip Assassin v2.0.1

### 🎯 What's New
- AI-powered silence detection
- Auto-chapter generation
- Plugin system for extensions
- Enhanced error handling
- Cross-platform installers

### 📥 Downloads
- **macOS**: [Clip_Assassin_v2.0.1.dmg](link) (Intel & Apple Silicon)
- **Windows**: [Clip_Assassin_v2.0.1_Setup.exe](link) (64-bit)

### 🛠 Installation

#### macOS
1. Download the .dmg file
2. Open and drag Clip Assassin to Applications
3. Right-click → Open to bypass Gatekeeper on first launch
4. Ensure DaVinci Resolve is installed and running

#### Windows
1. Download and run the setup.exe
2. Follow installation wizard
3. Launch from Start Menu or Desktop
4. Run as Administrator on first launch

### ⚙️ System Requirements
- **macOS**: 10.15 (Catalina) or later
- **Windows**: Windows 10 (64-bit) or later
- **Required**: DaVinci Resolve 17+
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 500MB free space

### 🐛 Known Issues
- First launch may be slow (5-10 seconds)
- macOS: May require disabling Gatekeeper temporarily

### 📞 Support
- Documentation: [Link to docs]
- Issues: [GitHub Issues](https://github.com/yourusername/clip-assassin/issues)
- Email: support@zabidstudio.com
```

---

## 🔐 Code Signing & Notarization (Optional but Recommended)

### macOS Notarization
```bash
# 1. Get Apple Developer ID from Keychain
codesign --list-signatures

# 2. Sign with Developer ID
codesign --force --deep --sign "Developer ID Application: Your Name" \
  "dist/Clip Assassin.app"

# 3. Notarize
xcrun notarytool submit "dist/Clip_Assassin_v2.0.1.dmg" \
  --apple-id "your@email.com" \
  --password "app-specific-password" \
  --team-id "YOUR_TEAM_ID" \
  --wait

# 4. Staple notarization ticket
xcrun stapler staple "dist/Clip Assassin.app"
```

### Windows Code Signing
```powershell
# Use SignTool with your certificate
signtool sign /f MyCert.pfx /p password /t http://timestamp.digicert.com `
  "dist\Clip_Assassin_v2.0.1_Setup.exe"
```

---

## 📊 Build Artifacts Structure

After successful build, your `dist/` folder should contain:

```
dist/
├── Clip_Assassin_v2.0.1.dmg          # macOS installer
├── Clip_Assassin_v2.0.1_Setup.exe    # Windows installer (after ISCC)
├── Clip Assassin/                    # Portable Windows build
│   ├── Clip Assassin.exe
│   └── _internal/
├── Clip Assassin.app                 # macOS app bundle
└── BUILD_README.md                   # Build information
```

---

## 🔄 Continuous Integration

The `.github/workflows/build.yml` file configures automated builds:

### Trigger Conditions
- Push to tags matching `v*` (e.g., `v2.0.1`)
- Manual trigger via GitHub Actions UI

### Build Matrix
- **macOS-latest**: Creates universal2 binary + DMG
- **windows-latest**: Creates exe + Inno Setup installer

### Artifacts
Builds are uploaded as artifacts and attached to GitHub Releases automatically.

---

## 🆘 Troubleshooting

### Build Fails on macOS
**Error**: `hdiutil: creation failed - Invalid argument`
- **Solution**: Ensure DMG contents folder exists and has correct permissions

**Error**: `codesign: resource envelope is obsolete`
- **Solution**: Run `xattr -cr dist/Clip\ Assassin.app` before signing

### Build Fails on Windows
**Error**: `ISCC.exe not found`
- **Solution**: Install Inno Setup or add to PATH

**Error**: `ModuleNotFoundError: No module named 'xxx'`
- **Solution**: Add `--hidden-import=xxx` to PyInstaller command

### App Crashes on Launch
**macOS**: 
- Check Console.app for crash logs
- Try: `xattr -cr /Applications/Clip\ Assassin.app`

**Windows**:
- Run as Administrator
- Check Event Viewer → Windows Logs → Application
- Ensure Visual C++ Redistributables are installed

---

## 📈 Next Steps After Build

1. ✅ Test on clean systems (both platforms)
2. ✅ Create GitHub Release with installers
3. ✅ Update README with download links
4. ✅ Announce release on social media/newsletter
5. ✅ Monitor GitHub Issues for bug reports
6. ✅ Plan next release based on feedback

---

## 📞 Support

For build issues or questions:
- **GitHub Issues**: https://github.com/yourusername/clip-assassin/issues
- **Documentation**: See `/docs` folder
- **Email**: support@zabidstudio.com

**Happy Building! 🎬✂️**

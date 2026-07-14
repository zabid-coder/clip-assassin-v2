"""
Setup script for building Clip Assassin with Timecode as a macOS .app bundle.

Usage:
    python3 setup_mac.py py2app
"""

from setuptools import setup
import os

APP = ['clip_assassin.py']
APP_NAME = 'Clip Assassin with Timecode'

# Collect data files to include in the bundle
DATA_FILES = []
ICON_FILE = None

# Check for icon files
for icon_candidate in ['app_icon.jpg', 'Clip_assassin_icon.png', 'icon.ico']:
    if os.path.exists(icon_candidate):
        DATA_FILES.append(icon_candidate)

# Try to use .icns icon if available, otherwise we'll convert later
if os.path.exists('app_icon.icns'):
    ICON_FILE = 'app_icon.icns'

OPTIONS = {
    'argv_emulation': False,
    'packages': ['customtkinter', 'tkinter'],
    'includes': [
        'resolve_core',
        'time_parser',
    ],
    'frameworks': [],
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleIdentifier': 'com.zabidalmuttaki.clipassassin',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '12.0',
        'CFBundleDevelopmentRegion': 'English',
        'NSHumanReadableCopyright': 'Created by Zabid Al Muttaki',
    },
}

if ICON_FILE:
    OPTIONS['iconfile'] = ICON_FILE

setup(
    name=APP_NAME,
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

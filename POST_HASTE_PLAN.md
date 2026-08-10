# 🚀 Post Haste-Style Master Ingest System - Implementation Plan

## 📋 Overview
Integrate **Digital Rebellion's Post Haste** features into Clip Assassin's Master Ingest system for complete template customization.

## ✨ Features to Implement

### 1. Custom Folder Templates
- Unlimited templates with visual editor
- Variables: `{date}`, `{project_name}`, `{client}`, `{camera}`
- Loop support: `Camera {cam}` where `cam in 1..3`
- Nested folder structures

### 2. Parameter System
- Text, Date, Number, Select, Boolean types
- Validation rules (regex, min/max, required)
- Default values
- Custom date formats (YYYY-MM-DD, DD.MM.YYYY)

### 3. Preview Mode (Dry Run)
- Show what would be created before actual creation
- Count folders and files
- Validate paths

### 4. Placeholder Files
- Auto-create `.gitkeep` files
- Template documents (Shot List.txt, Budget.xlsx)

### 5. Template Management
- Save/Load custom templates
- Built-in presets (Social, Commercial, Film)
- Import/Export JSON format

---

## 🏗️ Architecture

### New Files Structure
```
/workspace/
├── models/
│   └── ingest_template.py       # Pydantic schema
├── services/
│   └── template_engine.py       # Core rendering logic
├── templates/
│   └── ingest_profiles/         # JSON templates
│       ├── social_media.json
│       ├── commercial.json
│       └── film_production.json
├── modules/
│   └── master_ingest.py         # Enhanced
├── server.py                    # New endpoints
└── frontend/src/pages/
    └── TemplateBuilder.tsx      # Visual editor UI
```

### Template Schema Example
```json
{
  "template_id": "multi_cam_interview",
  "name": "Multi-Cam Interview",
  "parameters": [
    {"name": "project_name", "type": "text", "required": true},
    {"name": "client", "type": "text", "required": false},
    {"name": "date", "type": "date", "default": "today"},
    {"name": "camera_count", "type": "number", "default": 2, "min": 1, "max": 8}
  ],
  "folder_structure": [
    {"path": "{date}_{client}_{project_name}"},
    {"path": "Raw Footages"},
    {"path": "Camera {cam}", "loop_variable": "cam in 1..camera_count"},
    {"path": "Davinci Resolve Database"},
    {"path": "Audio & Voiceover"},
    {"path": "Exports"},
    {"path": "Exports/Finals"}
  ],
  "placeholder_files": ["Exports/Finals/.gitkeep"],
  "variables": {"date_format": "YYYY-MM-DD", "slugify_strings": true}
}
```

---

## 📝 Step-by-Step Implementation

### Phase 1: Backend Core
1. Create `models/ingest_template.py` with Pydantic models
2. Create `services/template_engine.py` with rendering logic
3. Enhance `modules/master_ingest.py` to use templates
4. Add API endpoints to `server.py`:
   - `GET /api/v1/templates` - List all templates
   - `POST /api/v1/templates` - Save custom template
   - `POST /api/v1/templates/preview` - Dry run preview
   - `POST /api/v1/ingest/create_from_template` - Create from template

### Phase 2: Frontend UI
5. Create `TemplateBuilder.tsx` page with:
   - Template list view
   - Visual folder structure editor
   - Parameter configuration form
   - Live preview panel
6. Update `MasterIngestPage.tsx` to:
   - Add template selector dropdown
   - Show dynamic parameters based on selected template
   - Preview before creation

### Phase 3: Built-in Templates
7. Create default templates:
   - `social_media.json` - Reels/Shorts workflow
   - `commercial.json` - Corporate multi-cam
   - `film_production.json` - Narrative film structure

### Phase 4: Testing & Deployment
8. Test all workflows
9. Bump version to v2.0.2
10. Auto-push to GitHub

---

## 🔒 Security & Safety
- Path traversal protection (block `../`)
- Strict regex validation on inputs
- Dry-run mode before creation
- Rollback manifest on failure
- Permission checks

---

## ✅ Approval Checklist

Please confirm these decisions:

| Feature | Option | Your Choice |
|---------|--------|-------------|
| Template Editor | Visual drag-drop vs Text-based | Visual |
| Loop Syntax | `cam in 1..count` | OK? |
| Placeholder Files | Auto-create `.gitkeep` etc. | Yes/No |
| Storage Location | Global (`~/.clip_assassin`) | OK? |
| Preview Mode | Include dry-run | Highly Recommended |
| Post Haste Import | Support `.phstyle` files | Future/Now |

**Reply with "APPROVED" to proceed with full implementation!**

Once approved, I will execute all phases and auto-push to GitHub with version v2.0.2.

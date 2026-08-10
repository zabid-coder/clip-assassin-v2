# Clip Assassin Integration Guide

This guide explains how to integrate the new enterprise-grade features into Clip Assassin.

## 📦 New Components Added

### 1. Configuration Management (`config.py`)
Centralized configuration with environment variable support.

**Usage:**
```python
from config import config

# Access settings
api_port = config.API_PORT
redis_url = config.REDIS_URL
openai_key = config.OPENAI_API_KEY

# Validate paths
is_valid, msg = config.validate_path("/Users/myname/videos")
```

**Environment Variables:**
See `.env.example` for all available options.

---

### 2. Custom Exceptions (`exceptions.py`)
Structured error handling with error codes.

**Usage:**
```python
from exceptions import (
    ResolveConnectionError,
    TimelineNotFoundError,
    RenderError,
    AIIntegrationError
)

try:
    # Your code
    pass
except ResolveConnectionError as e:
    logger.error(f"Resolve error {e.code}: {e.message}")
```

---

### 3. Enhanced Logging (`logger.py`)
Structured logging with performance tracking.

**Usage:**
```python
from logger import setup_logging, get_logger, log_execution_time

# Initialize
setup_logging()
logger = get_logger(__name__)

# Decorator for timing
@log_execution_time(logger)
def slow_operation():
    pass
```

---

### 4. Background Task Queue (`task_queue.py`)
Async task processing for long-running operations.

**Setup:**
```bash
pip install celery[redis]
redis-server
```

**Usage:**
```python
from task_queue import get_task_manager, track_task

# For sync operations (automatic fallback)
@track_task
def batch_render(timelines, preset, target_dir, task_id=None):
    # Long running operation
    return {"rendered": len(timelines)}

# Get task status
manager = get_task_manager()
status = manager.get_task_status(task_id)
```

---

### 5. AI Integration (`ai_integration.py`)
Speech-to-text, auto-chapters, smart silence detection.

**Setup:**
```bash
# Option 1: OpenAI API
export OPENAI_API_KEY="sk-..."

# Option 2: Local Whisper
pip install openai-whisper
```

**Usage:**
```python
from ai_integration import get_ai_service

ai = get_ai_service()

# Transcribe audio
transcript = ai.transcribe_audio("/path/to/audio.mp3")

# Generate chapters
chapters = ai.generate_chapters(transcript)

# Smart silence detection
silence_regions = ai.detect_smart_silence("/path/to/audio.mp3")

# Suggest markers
markers = ai.suggest_markers(transcript)
```

---

### 6. Plugin System (`plugin_system.py`)
Extensible architecture for third-party tools.

**Enable Plugins:**
```bash
export CLIP_ASSASSIN_PLUGINS=true
```

**Create a Plugin:**
```python
# plugins/my_plugin.py
from clip_assassin_plugins import BasePlugin

class MyPlugin(BasePlugin):
    name = "my_plugin"
    version = "1.0.0"
    description = "My custom plugin"
    
    def initialize(self):
        return True
    
    def execute(self, **kwargs):
        resolve = kwargs.get("resolve")
        # Custom logic here
        return {"success": True}

plugin = MyPlugin()
```

**Use Plugins:**
```python
from plugin_system import get_plugin_manager

manager = get_plugin_manager()

# List plugins
plugins = manager.list_plugins()

# Execute plugin
result = manager.execute_plugin("my_plugin", resolve=resolve_instance)
```

---

## 🔧 Integration Steps

### Step 1: Update `server.py`

Add imports and update error handling:

```python
from config import config
from exceptions import ClipAssassinError, ResolveConnectionError
from logger import setup_logging, get_logger, log_execution_time
from task_queue import track_task
from ai_integration import get_ai_service
from plugin_system import get_plugin_manager

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Update FastAPI app
app = FastAPI(
    title="Clip Assassin API",
    version="2.1.0",
    description="Enhanced with AI, async tasks, and plugins"
)

# Add exception handler
@app.exception_handler(ClipAssassinError)
async def handle_clip_assassin_error(request, exc: ClipAssassinError):
    return JSONResponse(
        status_code=400,
        content=exc.to_dict()
    )
```

### Step 2: Update `db.py` for Migrations

Create `alembic` configuration:

```bash
alembic init alembic
```

Update `alembic/env.py`:
```python
from db import DB_PATH
from sqlalchemy import create_engine

config.set_main_option('sqlalchemy.url', f'sqlite:///{DB_PATH}')
```

Create first migration:
```bash
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

### Step 3: Add AI Endpoints to `server.py`

```python
class TranscribeRequest(BaseModel):
    audio_path: str
    language: str = "en"

class ChapterRequest(BaseModel):
    max_chapters: int = 10

@app.post("/api/ai/transcribe", response_model=dict)
@log_execution_time(logger)
def transcribe_audio(req: TranscribeRequest):
    try:
        ai = get_ai_service()
        result = ai.transcribe_audio(req.audio_path, req.language)
        return {"success": True, "data": result}
    except AIIntegrationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())

@app.post("/api/ai/generate_chapters", response_model=dict)
def generate_chapters(req: ChapterRequest):
    # Implementation here
    pass

@app.post("/api/ai/suggest_markers", response_model=dict)
def suggest_markers():
    # Implementation here
    pass
```

### Step 4: Add Plugin Endpoints

```python
@app.get("/api/plugins", response_model=list)
def list_plugins():
    manager = get_plugin_manager()
    return manager.list_plugins()

@app.post("/api/plugins/{plugin_name}/execute", response_model=dict)
def execute_plugin(plugin_name: str, payload: dict = {}):
    manager = get_plugin_manager()
    result = manager.execute_plugin(plugin_name, **payload)
    return result
```

### Step 5: Add Task Status Endpoint

```python
@app.get("/api/tasks/{task_id}")
def get_task_status(task_id: str):
    from task_queue import get_task_manager
    manager = get_task_manager()
    return manager.get_task_status(task_id)

@app.delete("/api/tasks/{task_id}")
def cancel_task(task_id: str):
    from task_queue import get_task_manager
    manager = get_task_manager()
    success = manager.revoke_task(task_id, terminate=True)
    return {"success": success}
```

---

## 🚀 Quick Start Commands

```bash
# Install enhanced dependencies
pip install -r requirements-enhanced.txt

# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env

# Initialize Alembic migrations
alembic init alembic
alembic revision --autogenerate -m "Initial"
alembic upgrade head

# Start Redis (for task queue)
redis-server

# Start Celery workers (optional)
celery -A tasks worker --loglevel=info -Q renders,ingest,ai

# Run the server
python server.py
```

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/WebSocket
┌────────────────────▼────────────────────────────────────┐
│                   FastAPI Server                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │   Config    │  │  Exceptions │  │    Logger       │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │ Task Queue  │  │     AI      │  │    Plugins      │ │
│  │  (Celery)   │  │  (Whisper)  │  │   (Extensible)  │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   ┌─────────┐ ┌──────────┐ ┌──────────┐
   │ SQLite  │ │  Redis   │ │  OpenAI  │
   │ (Alembic)│ │  (Queue) │ │ (Cloud)  │
   └─────────┘ └──────────┘ └──────────┘
```

---

## 🎯 Next Steps

1. **P0 - Critical**: Integrate config, exceptions, and logging into `server.py`
2. **P1 - High Priority**: Set up Alembic migrations and async task queue
3. **P2 - Medium Priority**: Add AI endpoints and test transcription
4. **P3 - Future**: Build plugin ecosystem and community contributions

---

## 📝 Migration Checklist

- [ ] Copy `.env.example` to `.env` and configure
- [ ] Install enhanced dependencies
- [ ] Update `server.py` with new imports
- [ ] Add structured error handling
- [ ] Set up Alembic migrations
- [ ] Configure Redis (optional)
- [ ] Test AI integration (optional)
- [ ] Enable plugin system (optional)
- [ ] Add monitoring/observability (optional)


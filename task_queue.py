"""
Clip Assassin Background Task Queue
Async task processing with Celery and Redis
"""
import os
import json
import uuid
from typing import Any, Dict, Optional, List
from datetime import datetime
from enum import Enum

try:
    from celery import Celery, Task
    from celery.result import AsyncResult
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

from config import config
from exceptions import TaskQueueError
from logger import get_logger

logger = get_logger(__name__)


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PROGRESS = "PROGRESS"


class TaskManager:
    """Manages background tasks for long-running operations"""
    
    def __init__(self):
        self.celery_app = None
        self.enabled = config.TASK_QUEUE_ENABLED and CELERY_AVAILABLE
        
        if self.enabled:
            self._init_celery()
        else:
            logger.warning("Task queue disabled. Install celery[redis] to enable async tasks.")
    
    def _init_celery(self):
        """Initialize Celery app with Redis broker"""
        try:
            self.celery_app = Celery(
                'clip_assassin',
                broker=config.REDIS_URL,
                backend=config.REDIS_URL,
                include=['tasks']
            )
            
            self.celery_app.conf.update(
                task_serializer='json',
                accept_content=['json'],
                result_serializer='json',
                timezone='UTC',
                enable_utc=True,
                task_track_started=True,
                task_time_limit=config.RENDER_TIMEOUT,
                worker_prefetch_multiplier=1,
                task_routes={
                    'tasks.render_timeline': {'queue': 'renders'},
                    'tasks.batch_render': {'queue': 'renders'},
                    'tasks.master_ingest': {'queue': 'ingest'},
                    'tasks.ai_transcribe': {'queue': 'ai'},
                }
            )
            
            logger.info(f"Celery initialized with Redis: {config.REDIS_URL}")
        except Exception as e:
            logger.error(f"Failed to initialize Celery: {e}")
            self.enabled = False
    
    def submit_task(self, task_name: str, *args, **kwargs) -> str:
        """Submit a task to the queue"""
        if not self.enabled or not self.celery_app:
            raise TaskQueueError("Task queue not enabled")
        
        try:
            task = self.celery_app.send_task(task_name, args=args, kwargs=kwargs)
            logger.info(f"Task submitted: {task.id} ({task_name})")
            return task.id
        except Exception as e:
            logger.error(f"Failed to submit task: {e}")
            raise TaskQueueError(str(e))
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a task"""
        if not self.enabled or not self.celery_app:
            raise TaskQueueError("Task queue not enabled")
        
        try:
            result = AsyncResult(task_id, app=self.celery_app)
            return {
                "task_id": task_id,
                "status": result.status,
                "ready": result.ready(),
                "successful": result.successful() if result.ready() else None,
                "result": result.result if result.ready() else None,
                "info": result.info if hasattr(result, 'info') else None
            }
        except Exception as e:
            logger.error(f"Failed to get task status: {e}")
            raise TaskQueueError(str(e), task_id=task_id)
    
    def revoke_task(self, task_id: str, terminate: bool = False) -> bool:
        """Revoke/cancel a task"""
        if not self.enabled or not self.celery_app:
            raise TaskQueueError("Task queue not enabled")
        
        try:
            self.celery_app.control.revoke(task_id, terminate=terminate)
            logger.info(f"Task revoked: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to revoke task: {e}")
            raise TaskQueueError(str(e), task_id=task_id)


# In-memory task store for fallback when queue is disabled
class SimpleTaskStore:
    """Simple in-memory task tracking for sync operations"""
    
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
    
    def create_task(self, task_type: str, **kwargs) -> str:
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "task_id": task_id,
            "task_type": task_type,
            "status": TaskStatus.PENDING,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "progress": 0,
            "result": None,
            "error": None,
            **kwargs
        }
        return task_id
    
    def update_task(self, task_id: str, **updates):
        if task_id in self.tasks:
            self.tasks[task_id].update(updates)
            self.tasks[task_id]["updated_at"] = datetime.utcnow().isoformat()
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self.tasks.get(task_id)
    
    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[Dict[str, Any]]:
        tasks = list(self.tasks.values())
        if status:
            tasks = [t for t in tasks if t["status"] == status]
        return tasks


# Global task manager instance
task_manager = TaskManager()
simple_store = SimpleTaskStore()


def get_task_manager() -> TaskManager:
    """Get the task manager instance"""
    return task_manager


def track_task(func):
    """Decorator to track synchronous long-running tasks"""
    import functools
    from time import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        task_id = simple_store.create_task(func.__name__)
        start_time = time()
        
        try:
            simple_store.update_task(task_id, status=TaskStatus.STARTED)
            result = func(*args, task_id=task_id, **kwargs)
            duration = time() - start_time
            
            simple_store.update_task(
                task_id,
                status=TaskStatus.SUCCESS,
                result=result,
                duration=duration
            )
            
            return {"task_id": task_id, "success": True, "result": result}
        except Exception as e:
            duration = time() - start_time
            simple_store.update_task(
                task_id,
                status=TaskStatus.FAILURE,
                error=str(e),
                duration=duration
            )
            logger.error(f"Task {task_id} failed: {e}")
            return {"task_id": task_id, "success": False, "error": str(e)}
    
    return wrapper

"""
Clip Assassin Custom Exceptions
Provides structured error handling with error codes
"""
from typing import Optional, Dict, Any


class ClipAssassinError(Exception):
    """Base exception for Clip Assassin"""
    
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR", details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": False,
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details
            }
        }


class ResolveConnectionError(ClipAssassinError):
    """DaVinci Resolve connection failed"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="RESOLVE_CONNECTION_ERROR", details=details)


class TimelineNotFoundError(ClipAssassinError):
    """Timeline not found in project"""
    
    def __init__(self, timeline_name: str):
        super().__init__(
            f"Timeline '{timeline_name}' not found",
            code="TIMELINE_NOT_FOUND",
            details={"timeline_name": timeline_name}
        )


class ClipNotFoundError(ClipAssassinError):
    """Clip not found in Media Pool"""
    
    def __init__(self, clip_name: str):
        super().__init__(
            f"Clip '{clip_name}' not found",
            code="CLIP_NOT_FOUND",
            details={"clip_name": clip_name}
        )


class RenderError(ClipAssassinError):
    """Render job failed"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="RENDER_ERROR", details=details)


class ValidationError(ClipAssassinError):
    """Input validation failed"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message,
            code="VALIDATION_ERROR",
            details={"field": field} if field else {}
        )


class PathSecurityError(ClipAssassinError):
    """Path validation failed for security reasons"""
    
    def __init__(self, path: str, reason: str):
        super().__init__(
            f"Path access denied: {reason}",
            code="PATH_SECURITY_ERROR",
            details={"path": path, "reason": reason}
        )


class PluginError(ClipAssassinError):
    """Plugin execution failed"""
    
    def __init__(self, plugin_name: str, message: str):
        super().__init__(
            f"Plugin '{plugin_name}' error: {message}",
            code="PLUGIN_ERROR",
            details={"plugin_name": plugin_name}
        )


class AIIntegrationError(ClipAssassinError):
    """AI service integration failed"""
    
    def __init__(self, service: str, message: str):
        super().__init__(
            f"AI service '{service}' error: {message}",
            code="AI_INTEGRATION_ERROR",
            details={"service": service}
        )


class TaskQueueError(ClipAssassinError):
    """Background task queue error"""
    
    def __init__(self, message: str, task_id: Optional[str] = None):
        super().__init__(
            message,
            code="TASK_QUEUE_ERROR",
            details={"task_id": task_id} if task_id else {}
        )

"""
Clip Assassin Plugin System
Extensible architecture for third-party tools and custom workflows
"""
import os
import json
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod

from config import config
from exceptions import PluginError
from logger import get_logger

logger = get_logger(__name__)


class BasePlugin(ABC):
    """Base class for all Clip Assassin plugins"""
    
    name: str = "base_plugin"
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the plugin. Return True if successful."""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the plugin's main functionality"""
        pass
    
    def shutdown(self):
        """Cleanup when plugin is unloaded"""
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return plugin metadata"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author
        }


class PluginManager:
    """Manages plugin lifecycle and execution"""
    
    def __init__(self):
        self.enabled = config.PLUGINS_ENABLED
        self.plugin_dir = Path(config.PLUGIN_DIR)
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
        
        if self.enabled:
            self._ensure_plugin_dir()
            self._load_plugins()
        else:
            logger.info("Plugin system disabled")
    
    def _ensure_plugin_dir(self):
        """Create plugin directory if it doesn't exist"""
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        
        # Create example plugin if directory is empty
        if not any(self.plugin_dir.glob("*.py")):
            self._create_example_plugin()
    
    def _create_example_plugin(self):
        """Create an example plugin template"""
        example_code = '''"""
Example Clip Assassin Plugin
Copy this file to create your own plugin
"""
from clip_assassin_plugins import BasePlugin
from typing import Dict, Any


class ExamplePlugin(BasePlugin):
    name = "example_plugin"
    version = "1.0.0"
    description = "An example plugin demonstrating the plugin API"
    author = "Your Name"
    
    def initialize(self) -> bool:
        \"\"\"Initialize the plugin\"\"\"
        print(f"{self.name} initialized")
        return True
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        \"\"\"Execute plugin functionality\"\"\"
        # Access Resolve connection if needed
        resolve = kwargs.get("resolve")
        
        # Your custom logic here
        return {
            "success": True,
            "message": f"{self.name} executed successfully",
            "data": {"example": "data"}
        }
    
    def shutdown(self):
        \"\"\"Cleanup\"\"\"
        print(f"{self.name} shutting down")


# Register the plugin
plugin = ExamplePlugin()
'''
        
        example_path = self.plugin_dir / "example_plugin.py"
        if not example_path.exists():
            example_path.write_text(example_code)
            logger.info(f"Created example plugin at {example_path}")
    
    def _load_plugins(self):
        """Load all plugins from plugin directory"""
        if not self.plugin_dir.exists():
            return
        
        for plugin_file in self.plugin_dir.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue
            
            try:
                self._load_plugin_file(plugin_file)
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_file}: {e}")
    
    def _load_plugin_file(self, plugin_file: Path):
        """Load a single plugin file"""
        spec = importlib.util.spec_from_file_location(
            plugin_file.stem,
            plugin_file
        )
        
        if not spec or not spec.loader:
            raise ImportError(f"Cannot load spec for {plugin_file}")
        
        module = importlib.util.module_from_spec(spec)
        
        # Add base plugin class to module namespace
        module.BasePlugin = BasePlugin
        
        spec.loader.exec_module(module)
        
        # Look for plugin instance
        if hasattr(module, 'plugin'):
            plugin_instance = module.plugin
            if isinstance(plugin_instance, BasePlugin):
                if plugin_instance.initialize():
                    self.plugins[plugin_instance.name] = plugin_instance
                    logger.info(f"Loaded plugin: {plugin_instance.name} v{plugin_instance.version}")
                else:
                    logger.warning(f"Plugin {plugin_instance.name} failed to initialize")
    
    def execute_plugin(self, plugin_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a specific plugin"""
        if plugin_name not in self.plugins:
            raise PluginError(plugin_name, f"Plugin not found: {plugin_name}")
        
        try:
            plugin = self.plugins[plugin_name]
            result = plugin.execute(**kwargs)
            logger.info(f"Executed plugin: {plugin_name}")
            return result
        except Exception as e:
            logger.error(f"Plugin execution failed: {e}")
            raise PluginError(plugin_name, str(e))
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all loaded plugins with metadata"""
        return [
            {
                **plugin.get_metadata(),
                "enabled": True
            }
            for plugin in self.plugins.values()
        ]
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin"""
        if plugin_name not in self.plugins:
            return False
        
        try:
            plugin = self.plugins[plugin_name]
            plugin.shutdown()
            del self.plugins[plugin_name]
            logger.info(f"Unloaded plugin: {plugin_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def reload_all(self):
        """Reload all plugins"""
        for plugin in list(self.plugins.values()):
            self.unload_plugin(plugin.name)
        
        self._load_plugins()


class PluginHook:
    """Hook system for extending core functionality"""
    
    def __init__(self):
        self.hooks: Dict[str, List[Callable]] = {}
    
    def register(self, hook_name: str, callback: Callable):
        """Register a callback for a hook"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)
        logger.debug(f"Registered hook: {hook_name}")
    
    def trigger(self, hook_name: str, *args, **kwargs):
        """Trigger all callbacks for a hook"""
        if hook_name not in self.hooks:
            return
        
        for callback in self.hooks[hook_name]:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Hook {hook_name} callback failed: {e}")
    
    def trigger_with_result(self, hook_name: str, initial_value: Any, *args, **kwargs) -> Any:
        """Trigger hooks and pass results between them"""
        value = initial_value
        if hook_name not in self.hooks:
            return value
        
        for callback in self.hooks[hook_name]:
            try:
                result = callback(value, *args, **kwargs)
                if result is not None:
                    value = result
            except Exception as e:
                logger.error(f"Hook {hook_name} callback failed: {e}")
        
        return value


# Available hooks in Clip Assassin
HOOK_TIMELINE_CREATED = "timeline_created"
HOOK_CLIP_IMPORTED = "clip_imported"
HOOK_RENDER_STARTED = "render_started"
HOOK_RENDER_COMPLETED = "render_completed"
HOOK_MARKER_ADDED = "marker_added"


# Global plugin manager instance
plugin_manager = PluginManager()
plugin_hooks = PluginHook()


def get_plugin_manager() -> PluginManager:
    """Get the plugin manager instance"""
    return plugin_manager


def get_plugin_hooks() -> PluginHook:
    """Get the plugin hooks instance"""
    return plugin_hooks

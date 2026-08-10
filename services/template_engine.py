"""
Template Engine - Post Haste Style
Handles variable substitution, loop expansion, conditional creation, and folder structure generation
"""
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import shutil

from models.ingest_template import IngestTemplate, FolderNode, TemplateParameter, ParameterType


class TemplateEngine:
    """Engine for processing ingest templates and generating folder structures"""
    
    def __init__(self):
        self.variable_pattern = re.compile(r'\{(\w+)(?::([^}]+))?\}')  # {var} or {var:format}
        self.loop_pattern = re.compile(r'^(.+?)\s*\.\.(\d+)$')  # Name..N pattern
    
    def validate_parameters(self, template: IngestTemplate, values: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate user-provided parameter values against template definition"""
        errors = []
        
        # Check built-in parameters
        for param_name, param_def in template.builtin_params.items():
            if param_def.get('required', False) and param_name not in values:
                errors.append(f"Missing required parameter: {param_name}")
        
        # Check custom parameters
        for param in template.parameters:
            if param.required and param.name not in values:
                errors.append(f"Missing required parameter: {param.label}")
                continue
            
            if param.name in values:
                value = values[param.name]
                
                # Type validation
                if param.type == ParameterType.NUMBER:
                    try:
                        num_val = float(value)
                        if param.min_value is not None and num_val < param.min_value:
                            errors.append(f"{param.label} must be >= {param.min_value}")
                        if param.max_value is not None and num_val > param.max_value:
                            errors.append(f"{param.label} must be <= {param.max_value}")
                    except (ValueError, TypeError):
                        errors.append(f"{param.label} must be a number")
                
                elif param.type == ParameterType.DATE:
                    try:
                        datetime.strptime(value, param.date_format or "%Y-%m-%d")
                    except ValueError:
                        errors.append(f"{param.label} must be in format {param.date_format or '%Y-%m-%d'}")
                
                elif param.type == ParameterType.SELECT:
                    if param.options and value not in param.options:
                        errors.append(f"{param.label} must be one of: {', '.join(param.options)}")
                
                # Pattern validation
                if param.validation_pattern:
                    if not re.match(param.validation_pattern, str(value)):
                        errors.append(f"{param.label} does not match required pattern")
        
        return len(errors) == 0, errors
    
    def substitute_variables(self, text: str, values: Dict[str, Any], date_format: str = "%Y-%m-%d") -> str:
        """Replace variables in text with actual values"""
        def replace_var(match):
            var_name = match.group(1)
            format_spec = match.group(2)
            
            if var_name not in values:
                return match.group(0)  # Keep original if not found
            
            value = values[var_name]
            
            # Handle date formatting
            if var_name == 'date' and isinstance(value, str):
                try:
                    dt = datetime.strptime(value, date_format)
                    if format_spec:
                        return dt.strftime(format_spec)
                    return value
                except ValueError:
                    pass
            
            # Handle client name sanitization for folders
            if var_name == 'client' and value:
                value = re.sub(r'[^\w\s-]', '', str(value)).strip().replace(' ', '_')
            
            return str(value)
        
        return self.variable_pattern.sub(replace_var, text)
    
    def expand_loops(self, node: FolderNode, values: Dict[str, Any]) -> List[FolderNode]:
        """Expand loop nodes into multiple instances"""
        if not node.loop_variable:
            return [node]
        
        # Determine loop count
        loop_count = node.loop_end
        if loop_count is None:
            # Get from parameter values
            loop_count = values.get(node.loop_variable, 1)
            try:
                loop_count = int(loop_count)
            except (ValueError, TypeError):
                loop_count = 1
        
        expanded = []
        for i in range(node.loop_start, loop_count + 1):
            new_node = node.copy()
            new_node.loop_variable = None  # Remove loop after expansion
            new_node.loop_end = None
            
            # Substitute loop index in name
            new_node.name = self.substitute_variables(
                node.name.replace(f'{{{node.loop_variable}}}', str(i)),
                {**values, node.loop_variable: str(i)}
            )
            
            expanded.append(new_node)
        
        return expanded
    
    def evaluate_condition(self, condition: str, values: Dict[str, Any]) -> bool:
        """Evaluate conditional creation rules"""
        if not condition:
            return True
        
        # Simple condition evaluation (can be extended)
        # Examples: "camera_count > 1", "deliverables == 'all'"
        try:
            # Safe evaluation with limited scope
            safe_values = {k: v for k, v in values.items() if isinstance(v, (int, float, str, bool))}
            return eval(condition, {"__builtins__": {}}, safe_values)
        except Exception:
            return True  # Default to true on error
    
    def generate_structure(self, template: IngestTemplate, values: Dict[str, Any], 
                          base_path: str, dry_run: bool = False) -> Dict[str, Any]:
        """Generate complete folder structure from template"""
        # Validate first
        is_valid, errors = self.validate_parameters(template, values)
        if not is_valid:
            return {"success": False, "errors": errors, "created": [], "preview": []}
        
        # Prepare values with defaults
        all_values = self._prepare_values(template, values)
        
        created_items = []
        preview_items = []
        
        def process_node(node: FolderNode, current_path: str, depth: int = 0):
            # Check condition
            if not self.evaluate_condition(node.condition, all_values):
                return
            
            # Expand loops
            nodes_to_process = self.expand_loops(node, all_values)
            
            for proc_node in nodes_to_process:
                # Substitute variables in name
                node_name = self.substitute_variables(proc_node.name, all_values)
                node_path = os.path.join(current_path, node_name)
                
                item_info = {
                    "name": node_name,
                    "path": node_path,
                    "type": proc_node.type,
                    "depth": depth
                }
                
                if dry_run:
                    preview_items.append(item_info)
                else:
                    # Create folder or file
                    if proc_node.type == "folder":
                        os.makedirs(node_path, exist_ok=True)
                        created_items.append(item_info)
                        
                        # Process children
                        if proc_node.children:
                            for child in proc_node.children:
                                process_node(child, node_path, depth + 1)
                    
                    elif proc_node.type == "file":
                        # Create file with optional placeholder content
                        parent_dir = os.path.dirname(node_path)
                        os.makedirs(parent_dir, exist_ok=True)
                        
                        content = proc_node.placeholder_content or ""
                        content = self.substitute_variables(content, all_values)
                        
                        with open(node_path, 'w') as f:
                            f.write(content)
                        
                        created_items.append(item_info)
        
        # Process root structure
        for root_node in template.structure:
            process_node(root_node, base_path)
        
        return {
            "success": True,
            "errors": [],
            "created": created_items if not dry_run else [],
            "preview": preview_items if dry_run else created_items,
            "total_items": len(created_items) if not dry_run else len(preview_items),
            "base_path": base_path
        }
    
    def _prepare_values(self, template: IngestTemplate, values: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user values with defaults and built-in parameters"""
        all_values = {}
        
        # Add built-in params with defaults
        for param_name, param_def in template.builtin_params.items():
            if param_name in values:
                all_values[param_name] = values[param_name]
            elif 'default' in param_def:
                all_values[param_name] = param_def['default']
            elif param_def.get('type') == 'date':
                all_values[param_name] = datetime.now().strftime(param_def.get('default_format', '%Y-%m-%d'))
        
        # Add custom params with defaults
        for param in template.parameters:
            if param.name in values:
                all_values[param.name] = values[param.name]
            elif param.default is not None:
                all_values[param.name] = param.default
        
        return all_values
    
    def export_template(self, template: IngestTemplate, filepath: str):
        """Export template to JSON file"""
        with open(filepath, 'w') as f:
            f.write(template.to_json())
    
    def import_template(self, filepath: str) -> IngestTemplate:
        """Import template from JSON file"""
        with open(filepath, 'r') as f:
            return IngestTemplate.from_json(f.read())
    
    def get_preview_tree(self, template: IngestTemplate, values: Dict[str, Any], 
                         base_path: str = "/preview") -> str:
        """Generate ASCII tree preview of structure"""
        result = self.generate_structure(template, values, base_path, dry_run=True)
        
        if not result["success"]:
            return "Error: " + ", ".join(result["errors"])
        
        def build_tree(items, prefix=""):
            output = []
            items_sorted = sorted(items, key=lambda x: (x['type'] != 'folder', x['name']))
            
            for i, item in enumerate(items_sorted):
                is_last = i == len(items_sorted) - 1
                connector = "└── " if is_last else "├── "
                icon = "📁 " if item['type'] == 'folder' else "📄 "
                output.append(f"{prefix}{connector}{icon}{item['name']}")
                
                # Find children
                children = [x for x in items if x['path'].startswith(item['path'] + os.sep) 
                           and x['depth'] == item['depth'] + 1]
                
                if children:
                    extension = "    " if is_last else "│   "
                    output.append(build_tree(children, prefix + extension))
            
            return "\n".join(output)
        
        # Group by depth
        preview_items = result["preview"]
        return build_tree(preview_items)


# Singleton instance
template_engine = TemplateEngine()

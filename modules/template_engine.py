"""
Ingest Template Model - Post Haste Style
Supports dynamic variables, loops, and custom parameters
"""
import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any


class IngestTemplateDB:
    """Database manager for ingest templates using SQLite"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Templates table
        c.execute('''
            CREATE TABLE IF NOT EXISTS ingest_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT DEFAULT 'Custom',
                structure TEXT NOT NULL,
                parameters TEXT NOT NULL,
                placeholders TEXT NOT NULL,
                is_builtin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Presets table
        c.execute('''
            CREATE TABLE IF NOT EXISTS ingest_presets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                template_id INTEGER,
                param_values TEXT NOT NULL,
                FOREIGN KEY (template_id) REFERENCES ingest_templates(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_template(self, name: str, structure: List[Dict], parameters: List[Dict], 
                       placeholders: Dict[str, str], description: str = "", 
                       category: str = "Custom", is_builtin: int = 0) -> int:
        """Create a new template"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO ingest_templates 
            (name, description, category, structure, parameters, placeholders, is_builtin)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, description, category, json.dumps(structure), 
              json.dumps(parameters), json.dumps(placeholders), is_builtin))
        
        template_id = c.lastrowid
        conn.commit()
        conn.close()
        return template_id
    
    def get_template(self, template_id: int) -> Optional[Dict[str, Any]]:
        """Get a template by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('SELECT * FROM ingest_templates WHERE id = ?', (template_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row["id"],
                "name": row["name"],
                "description": row["description"],
                "category": row["category"],
                "structure": json.loads(row["structure"]),
                "parameters": json.loads(row["parameters"]),
                "placeholders": json.loads(row["placeholders"]),
                "is_builtin": bool(row["is_builtin"]),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            }
        return None
    
    def get_all_templates(self, include_builtin: bool = True) -> List[Dict[str, Any]]:
        """Get all templates"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        if include_builtin:
            c.execute('SELECT * FROM ingest_templates ORDER BY category, name')
        else:
            c.execute('SELECT * FROM ingest_templates WHERE is_builtin = 0 ORDER BY name')
        
        rows = c.fetchall()
        conn.close()
        
        templates = []
        for row in rows:
            templates.append({
                "id": row["id"],
                "name": row["name"],
                "description": row["description"],
                "category": row["category"],
                "structure": json.loads(row["structure"]),
                "parameters": json.loads(row["parameters"]),
                "placeholders": json.loads(row["placeholders"]),
                "is_builtin": bool(row["is_builtin"]),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            })
        return templates
    
    def update_template(self, template_id: int, name: str = None, structure: List[Dict] = None,
                       parameters: List[Dict] = None, placeholders: Dict[str, str] = None,
                       description: str = None, category: str = None) -> bool:
        """Update an existing template"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        updates = []
        values = []
        
        if name is not None:
            updates.append("name = ?")
            values.append(name)
        if structure is not None:
            updates.append("structure = ?")
            values.append(json.dumps(structure))
        if parameters is not None:
            updates.append("parameters = ?")
            values.append(json.dumps(parameters))
        if placeholders is not None:
            updates.append("placeholders = ?")
            values.append(json.dumps(placeholders))
        if description is not None:
            updates.append("description = ?")
            values.append(description)
        if category is not None:
            updates.append("category = ?")
            values.append(category)
        
        if not updates:
            conn.close()
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(template_id)
        
        c.execute(f'UPDATE ingest_templates SET {", ".join(updates)} WHERE id = ?', values)
        conn.commit()
        conn.close()
        return True
    
    def delete_template(self, template_id: int) -> bool:
        """Delete a template (only if not builtin)"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Check if builtin
        c.execute('SELECT is_builtin FROM ingest_templates WHERE id = ?', (template_id,))
        row = c.fetchone()
        
        if row and row[0] == 1:
            conn.close()
            return False  # Cannot delete builtin templates
        
        c.execute('DELETE FROM ingest_templates WHERE id = ?', (template_id,))
        c.execute('DELETE FROM ingest_presets WHERE template_id = ?', (template_id,))
        conn.commit()
        conn.close()
        return True
    
    def create_preset(self, name: str, template_id: int, param_values: Dict[str, Any]) -> int:
        """Create a preset with pre-filled parameter values"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO ingest_presets (name, template_id, param_values)
            VALUES (?, ?, ?)
        ''', (name, template_id, json.dumps(param_values)))
        
        preset_id = c.lastrowid
        conn.commit()
        conn.close()
        return preset_id
    
    def get_presets_for_template(self, template_id: int) -> List[Dict[str, Any]]:
        """Get all presets for a template"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('SELECT * FROM ingest_presets WHERE template_id = ? ORDER BY name', (template_id,))
        rows = c.fetchall()
        conn.close()
        
        presets = []
        for row in rows:
            presets.append({
                "id": row["id"],
                "name": row["name"],
                "template_id": row["template_id"],
                "param_values": json.loads(row["param_values"])
            })
        return presets
    
    def delete_preset(self, preset_id: int) -> bool:
        """Delete a preset"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('DELETE FROM ingest_presets WHERE id = ?', (preset_id,))
        conn.commit()
        conn.close()
        return True


# Initialize with app's database
import db as app_db
template_db = IngestTemplateDB(app_db.DB_PATH)

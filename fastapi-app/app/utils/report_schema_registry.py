"""
Report Schema Registry - Introspects database tables and provides schema information
for the reporting system.
"""
from typing import List, Dict, Optional, Any
from sqlalchemy import inspect, MetaData
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine

from app.core.database import engine


class ReportSchemaRegistry:
    """Registry for database table schemas used in reporting."""
    
    def __init__(self, db_engine: Engine = None):
        self.engine = db_engine or engine
        self.inspector = inspect(self.engine)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)
    
    def get_available_tables(self, extension: str = "core", category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of available tables for reporting."""
        tables = []
        
        # Get all table names from database
        table_names = self.inspector.get_table_names()
        
        # Filter out system tables
        excluded_tables = {
            'alembic_version', 'migrations', 'telescope_entries', 'telescope_entries_tags',
            'telescope_monitoring', 'cache', 'cache_locks', 'sessions', 'jobs', 'failed_jobs',
            'password_resets', 'personal_access_tokens'
        }
        
        for table_name in table_names:
            if table_name in excluded_tables or table_name.startswith('telescope_'):
                continue
            
            try:
                columns = self.get_table_columns(table_name)
                relationships = self.get_table_relationships(table_name)
                
                tables.append({
                    'name': table_name,
                    'label': self._humanize_table_name(table_name),
                    'description': f"Table: {table_name}",
                    'category': category or 'general',
                    'extension': extension,
                    'columns': columns,
                    'relationships': relationships,
                    'supports_aggregates': True,
                    'max_rows': 50000,
                    'has_auto_joins': len(relationships) > 0,
                    'has_manual_joins': False,
                })
            except Exception:
                # Skip tables that can't be introspected
                continue
        
        return tables
    
    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Get columns for a specific table."""
        if table_name not in self.inspector.get_table_names():
            return []
        
        columns = []
        table_columns = self.inspector.get_columns(table_name)
        primary_keys = self.inspector.get_pk_constraint(table_name)['constrained_columns']
        
        for col in table_columns:
            col_name = col['name']
            col_type = str(col['type'])
            
            # Skip internal columns
            if col_name in ['id', 'uuid', '_key', 'created_at', 'updated_at', 'deleted_at']:
                continue
            
            columns.append({
                'name': col_name,
                'label': self._humanize_column_name(col_name),
                'type': self._normalize_type(col_type),
                'nullable': col.get('nullable', True),
                'default': str(col.get('default', '')) if col.get('default') is not None else None,
                'primary_key': col_name in primary_keys,
                'auto_join_path': None,
                'relationship_labels': [],
            })
        
        return columns
    
    def get_table_relationships(self, table_name: str) -> List[Dict[str, Any]]:
        """Get foreign key relationships for a table."""
        if table_name not in self.inspector.get_table_names():
            return []
        
        relationships = []
        foreign_keys = self.inspector.get_foreign_keys(table_name)
        
        for fk in foreign_keys:
            local_col = fk['constrained_columns'][0] if fk['constrained_columns'] else None
            ref_table = fk['referred_table']
            ref_col = fk['referred_columns'][0] if fk['referred_columns'] else None
            
            if local_col and ref_table and ref_col:
                relationships.append({
                    'name': f"{table_name}.{local_col}",
                    'type': 'belongs_to',
                    'local_table': table_name,
                    'local_column': local_col,
                    'foreign_table': ref_table,
                    'foreign_column': ref_col,
                    'label': self._humanize_table_name(ref_table),
                })
        
        return relationships
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get complete schema for a table including columns and relationships."""
        if table_name not in self.inspector.get_table_names():
            raise ValueError(f"Table '{table_name}' not found")
        
        columns = self.get_table_columns(table_name)
        relationships = self.get_table_relationships(table_name)
        
        return {
            'table_name': table_name,
            'columns': columns,
            'relationships': relationships,
            'primary_key': self.inspector.get_pk_constraint(table_name).get('constrained_columns', []),
            'indexes': [idx['name'] for idx in self.inspector.get_indexes(table_name)],
        }
    
    def has_table(self, table_name: str) -> bool:
        """Check if a table exists."""
        return table_name in self.inspector.get_table_names()
    
    def get_table(self, table_name: str) -> Optional[Any]:
        """Get table object from metadata."""
        if table_name in self.metadata.tables:
            return self.metadata.tables[table_name]
        return None
    
    def _humanize_table_name(self, name: str) -> str:
        """Convert table name to human-readable label."""
        # Remove common prefixes
        name = name.replace('fleetops_', '').replace('storefront_', '').replace('int_', '')
        # Convert snake_case to Title Case
        return ' '.join(word.capitalize() for word in name.split('_'))
    
    def _humanize_column_name(self, name: str) -> str:
        """Convert column name to human-readable label."""
        # Convert snake_case to Title Case
        return ' '.join(word.capitalize() for word in name.split('_'))
    
    def _normalize_type(self, sql_type: str) -> str:
        """Normalize SQL type to standard type names."""
        sql_type_lower = sql_type.lower()
        
        if 'int' in sql_type_lower:
            return 'integer'
        elif 'varchar' in sql_type_lower or 'char' in sql_type_lower or 'text' in sql_type_lower:
            return 'string'
        elif 'decimal' in sql_type_lower or 'float' in sql_type_lower or 'double' in sql_type_lower or 'numeric' in sql_type_lower:
            return 'decimal'
        elif 'date' in sql_type_lower:
            return 'date'
        elif 'time' in sql_type_lower:
            return 'datetime'
        elif 'bool' in sql_type_lower or 'tinyint(1)' in sql_type_lower:
            return 'boolean'
        elif 'json' in sql_type_lower:
            return 'json'
        else:
            return 'string'


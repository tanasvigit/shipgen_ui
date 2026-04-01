"""
Report Query Validator - Validates query configurations for security and correctness.
"""
from typing import Dict, List, Any, Optional

from app.utils.report_schema_registry import ReportSchemaRegistry


class ReportQueryValidator:
    """Validates query configurations."""
    
    def __init__(self, registry: ReportSchemaRegistry):
        self.registry = registry
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self, query_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a complete query configuration."""
        self.errors = []
        self.warnings = []
        
        # Basic structure validation
        self._validate_basic_structure(query_config)
        
        if not self.errors:
            # Detailed validation
            self._validate_table(query_config)
            self._validate_columns(query_config)
            self._validate_conditions(query_config)
            self._validate_group_by(query_config)
            self._validate_sort_by(query_config)
            self._validate_limit(query_config)
            self._perform_security_checks(query_config)
            self._perform_performance_checks(query_config)
        
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'summary': self._generate_validation_summary(query_config),
        }
    
    def _validate_basic_structure(self, query_config: Dict[str, Any]):
        """Validate basic query structure."""
        if 'table' not in query_config:
            self.errors.append("Query config must include 'table'")
            return
        
        if 'name' not in query_config.get('table', {}):
            self.errors.append("Query config must include 'table.name'")
            return
        
        if 'columns' not in query_config or not query_config['columns']:
            self.errors.append("Query config must include at least one column in 'columns'")
            return
        
        # Validate limit
        limit = query_config.get('limit')
        if limit is not None:
            if not isinstance(limit, int) or limit < 1 or limit > 50000:
                self.errors.append("Limit must be an integer between 1 and 50000")
    
    def _validate_table(self, query_config: Dict[str, Any]):
        """Validate table configuration."""
        table_name = query_config.get('table', {}).get('name')
        if not table_name:
            return
        
        if not self.registry.has_table(table_name):
            self.errors.append(f"Table '{table_name}' is not available for reporting")
            return
        
        # Check limit against table max
        limit = query_config.get('limit')
        if limit and limit > 50000:
            self.warnings.append(f"Requested limit ({limit}) exceeds recommended maximum (50000)")
    
    def _validate_columns(self, query_config: Dict[str, Any]):
        """Validate columns configuration."""
        table_name = query_config.get('table', {}).get('name')
        if not table_name:
            return
        
        available_columns = self.registry.get_table_columns(table_name)
        available_column_names = [col['name'] for col in available_columns]
        
        for idx, column in enumerate(query_config.get('columns', [])):
            if 'name' not in column:
                self.errors.append(f"Column {idx}: 'name' is required")
                continue
            
            col_name = column['name']
            
            # Check if it's a computed column
            if column.get('computed') and column.get('expression'):
                # Computed columns are validated separately
                continue
            
            # Check if column exists (handle relationship paths)
            base_col = col_name.split('.')[-1] if '.' in col_name else col_name
            if base_col not in available_column_names and not col_name.startswith('payload.'):
                self.warnings.append(f"Column '{col_name}' may not exist in table '{table_name}'")
        
        # Check for too many columns
        if len(query_config.get('columns', [])) > 50:
            self.warnings.append(f"Selecting many columns ({len(query_config['columns'])}) may impact performance")
    
    def _validate_conditions(self, query_config: Dict[str, Any]):
        """Validate WHERE conditions."""
        for idx, condition in enumerate(query_config.get('conditions', [])):
            if 'column' not in condition:
                self.errors.append(f"Condition {idx}: 'column' is required")
            if 'operator' not in condition:
                self.errors.append(f"Condition {idx}: 'operator' is required")
            if 'value' not in condition:
                self.errors.append(f"Condition {idx}: 'value' is required")
    
    def _validate_group_by(self, query_config: Dict[str, Any]):
        """Validate GROUP BY configuration."""
        group_by = query_config.get('groupBy', [])
        for idx, group in enumerate(group_by):
            if 'column' not in group:
                self.errors.append(f"GroupBy {idx}: 'column' is required")
    
    def _validate_sort_by(self, query_config: Dict[str, Any]):
        """Validate ORDER BY configuration."""
        sort_by = query_config.get('sortBy', [])
        for idx, sort in enumerate(sort_by):
            if 'column' not in sort:
                self.errors.append(f"SortBy {idx}: 'column' is required")
            direction = sort.get('direction', 'ASC').upper()
            if direction not in ['ASC', 'DESC']:
                self.errors.append(f"SortBy {idx}: 'direction' must be 'ASC' or 'DESC'")
    
    def _validate_limit(self, query_config: Dict[str, Any]):
        """Validate LIMIT configuration."""
        limit = query_config.get('limit')
        if limit is not None:
            if not isinstance(limit, int) or limit < 1:
                self.errors.append("Limit must be a positive integer")
            elif limit > 50000:
                self.warnings.append("Limit exceeds recommended maximum (50000)")
    
    def _perform_security_checks(self, query_config: Dict[str, Any]):
        """Perform security checks."""
        # Check for SQL injection patterns in computed columns
        for col in query_config.get('columns', []):
            if col.get('computed') and col.get('expression'):
                expr = col['expression'].upper()
                forbidden = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'TRUNCATE', 'ALTER', 'CREATE']
                if any(keyword in expr for keyword in forbidden):
                    self.errors.append(f"Computed column '{col.get('name')}' contains forbidden SQL keywords")
    
    def _perform_performance_checks(self, query_config: Dict[str, Any]):
        """Perform performance checks."""
        joins_count = len(query_config.get('joins', []))
        if joins_count > 3:
            self.warnings.append(f"Multiple joins ({joins_count}) may impact performance")
        
        conditions_count = len(query_config.get('conditions', []))
        if conditions_count > 10:
            self.warnings.append(f"Many conditions ({conditions_count}) may impact performance")
    
    def _generate_validation_summary(self, query_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate validation summary."""
        return {
            'table': query_config.get('table', {}).get('name', ''),
            'columns_count': len(query_config.get('columns', [])),
            'conditions_count': len(query_config.get('conditions', [])),
            'joins_count': len(query_config.get('joins', [])),
            'has_group_by': len(query_config.get('groupBy', [])) > 0,
            'has_sort_by': len(query_config.get('sortBy', [])) > 0,
            'limit': query_config.get('limit'),
        }


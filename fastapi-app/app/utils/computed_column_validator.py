"""
Computed Column Validator - Validates computed column expressions for security.
"""
from typing import Dict, List, Any

from app.utils.report_schema_registry import ReportSchemaRegistry


class ComputedColumnValidator:
    """Validates computed column expressions."""
    
    ALLOWED_FUNCTIONS = [
        # Date/Time
        'DATEDIFF', 'DATE_ADD', 'DATE_SUB', 'NOW', 'CURDATE', 'CURTIME',
        'YEAR', 'MONTH', 'DAY', 'HOUR', 'MINUTE', 'SECOND', 'DATE_FORMAT',
        # String
        'CONCAT', 'SUBSTRING', 'REPLACE', 'UPPER', 'LOWER', 'TRIM', 'LENGTH',
        # Numeric
        'ROUND', 'ABS', 'CEIL', 'FLOOR', 'MOD', 'POW', 'SQRT',
        # Conditional
        'CASE', 'IF', 'IFNULL', 'COALESCE',
        # Aggregate
        'COUNT', 'SUM', 'AVG', 'MIN', 'MAX',
        # Type Conversion
        'CAST', 'CONVERT',
    ]
    
    FORBIDDEN_KEYWORDS = [
        'DROP', 'DELETE', 'UPDATE', 'INSERT', 'TRUNCATE',
        'ALTER', 'CREATE', 'GRANT', 'REVOKE',
        'EXEC', 'EXECUTE', 'UNION', 'INTO',
        'INFORMATION_SCHEMA', 'LOAD_FILE', 'OUTFILE',
    ]
    
    def __init__(self, registry: ReportSchemaRegistry):
        self.registry = registry
    
    def validate(self, expression: str, table_name: str) -> Dict[str, Any]:
        """Validate a computed column expression."""
        errors = []
        
        if not expression:
            return {'valid': False, 'errors': ['Expression is required']}
        
        if not table_name:
            return {'valid': False, 'errors': ['Table name is required']}
        
        # Check if table exists
        if not self.registry.has_table(table_name):
            return {'valid': False, 'errors': [f"Table '{table_name}' not found"]}
        
        # Check for forbidden keywords
        expr_upper = expression.upper()
        for keyword in self.FORBIDDEN_KEYWORDS:
            if keyword in expr_upper:
                errors.append(f"Expression contains forbidden keyword: {keyword}")
        
        # Basic syntax check (ensure balanced parentheses)
        if expression.count('(') != expression.count(')'):
            errors.append("Unbalanced parentheses in expression")
        
        # Check for SQL injection patterns
        dangerous_patterns = [';', '--', '/*', '*/', 'xp_', 'sp_']
        for pattern in dangerous_patterns:
            if pattern in expression.upper():
                errors.append(f"Expression contains potentially dangerous pattern: {pattern}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
        }


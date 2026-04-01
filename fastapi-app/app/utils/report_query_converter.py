"""
Report Query Converter - Converts query_config to SQL and executes queries.
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import time

from sqlalchemy import text, select, func, and_, or_
from sqlalchemy.orm import Session

from app.utils.report_schema_registry import ReportSchemaRegistry


class ReportQueryConverter:
    """Converts query configuration to SQL and executes it."""
    
    def __init__(self, registry: ReportSchemaRegistry, query_config: Dict[str, Any], company_uuid: Optional[str] = None):
        self.registry = registry
        self.query_config = query_config
        self.company_uuid = company_uuid
        self.alias_counter = 0
    
    def execute(self, db: Session) -> Dict[str, Any]:
        """Execute the query and return results."""
        start_time = time.time()
        
        try:
            # Validate basic structure
            self._validate_basic_structure()
            
            # Build SQL query
            sql_query, bind_params = self._build_sql_query()
            
            # Execute query
            result = db.execute(text(sql_query), bind_params)
            rows = result.fetchall()
            
            # Convert rows to dictionaries
            columns = [col for col in result.keys()]
            data = [dict(zip(columns, row)) for row in rows]
            
            execution_time = round((time.time() - start_time) * 1000, 2)
            
            return {
                'success': True,
                'data': data,
                'columns': self._get_selected_columns(),
                'meta': {
                    'total_rows': len(data),
                    'execution_time_ms': execution_time,
                    'query_sql': sql_query,
                    'selected_columns': self._get_selected_column_names(),
                    'table_name': self.query_config.get('table', {}).get('name', ''),
                },
            }
        except Exception as e:
            execution_time = round((time.time() - start_time) * 1000, 2)
            return {
                'success': False,
                'error': str(e),
                'meta': {
                    'execution_time_ms': execution_time,
                },
            }
    
    def _validate_basic_structure(self):
        """Validate basic query structure."""
        if 'table' not in self.query_config or 'name' not in self.query_config['table']:
            raise ValueError("Query config must include 'table.name'")
        
        if 'columns' not in self.query_config or not self.query_config['columns']:
            raise ValueError("Query config must include at least one column in 'columns'")
        
        table_name = self.query_config['table']['name']
        if not self.registry.has_table(table_name):
            raise ValueError(f"Table '{table_name}' not found in registry")
    
    def _build_sql_query(self) -> Tuple[str, Dict[str, Any]]:
        """Build SQL query from query_config."""
        table_name = self.query_config['table']['name']
        bind_params = {}
        
        # Build SELECT clause
        select_parts = []
        for col in self.query_config.get('columns', []):
            col_name = col.get('name', '')
            alias = col.get('alias') or col_name
            
            # Handle computed columns
            if col.get('computed') and col.get('expression'):
                select_parts.append(f"({col['expression']}) AS \"{alias}\"")
            else:
                # Handle relationship paths (e.g., "payload.pickup.street1")
                if '.' in col_name:
                    parts = col_name.split('.')
                    if len(parts) == 2:
                        # Simple join: table.column
                        select_parts.append(f"\"{parts[0]}\".\"{parts[1]}\" AS \"{alias}\"")
                    else:
                        # Complex path - use first part as table, rest as column
                        select_parts.append(f"\"{parts[0]}\".\"{'.'.join(parts[1:])}\" AS \"{alias}\"")
                else:
                    select_parts.append(f"\"{table_name}\".\"{col_name}\" AS \"{alias}\"")
        
        sql = f"SELECT {', '.join(select_parts)} FROM \"{table_name}\""
        
        # Add company scope if company_uuid provided
        if self.company_uuid:
            sql += f" WHERE \"{table_name}\".\"company_uuid\" = :company_uuid"
            bind_params['company_uuid'] = self.company_uuid
        
        # Add WHERE conditions
        conditions = self.query_config.get('conditions', [])
        if conditions:
            where_clauses = []
            for idx, condition in enumerate(conditions):
                col = condition.get('column', '')
                operator = condition.get('operator', '=')
                value = condition.get('value')
                
                param_name = f"param_{idx}"
                if operator.upper() == 'IN' and isinstance(value, list):
                    placeholders = ', '.join([f":{param_name}_{i}" for i in range(len(value))])
                    where_clauses.append(f"\"{col}\" {operator} ({placeholders})")
                    for i, v in enumerate(value):
                        bind_params[f"{param_name}_{i}"] = v
                elif operator.upper() == 'LIKE':
                    where_clauses.append(f"\"{col}\" {operator} :{param_name}")
                    bind_params[param_name] = f"%{value}%"
                else:
                    where_clauses.append(f"\"{col}\" {operator} :{param_name}")
                    bind_params[param_name] = value
            
            if where_clauses:
                where_sql = ' AND '.join(where_clauses)
                if self.company_uuid:
                    sql += f" AND {where_sql}"
                else:
                    sql += f" WHERE {where_sql}"
        
        # Add GROUP BY
        group_by = self.query_config.get('groupBy', [])
        if group_by:
            group_cols = [f"`{g.get('column', '')}`" for g in group_by if g.get('column')]
            if group_cols:
                # Replace backticks with double quotes for PostgreSQL compatibility
                group_cols = [c.replace('`', '\"') for c in group_cols]
                sql += f" GROUP BY {', '.join(group_cols)}"
        
        # Add ORDER BY
        sort_by = self.query_config.get('sortBy', [])
        if sort_by:
            order_parts = []
            for sort in sort_by:
                col = sort.get('column', '')
                direction = sort.get('direction', 'ASC').upper()
                order_parts.append(f"`{col}` {direction}")
            if order_parts:
                sql += f" ORDER BY {', '.join(order_parts)}"
        
        # Add LIMIT
        limit = self.query_config.get('limit', 1000)
        if limit:
            sql += f" LIMIT {int(limit)}"
        
        return sql, bind_params
    
    def _get_selected_columns(self) -> List[Dict[str, Any]]:
        """Get selected columns metadata."""
        columns = []
        for col in self.query_config.get('columns', []):
            columns.append({
                'name': col.get('alias') or col.get('name', ''),
                'label': col.get('label') or col.get('name', ''),
                'type': col.get('type', 'string'),
            })
        return columns
    
    def _get_selected_column_names(self) -> List[str]:
        """Get list of selected column names."""
        return [col.get('alias') or col.get('name', '') for col in self.query_config.get('columns', [])]
    
    def get_available_export_formats(self) -> Dict[str, str]:
        """Get available export formats."""
        return {
            'csv': 'CSV (Comma Separated Values)',
            'xlsx': 'Excel (XLSX)',
            'json': 'JSON',
            'pdf': 'PDF',
        }
    
    def get_query_analysis(self) -> Dict[str, Any]:
        """Analyze query complexity and provide insights."""
        columns_count = len(self.query_config.get('columns', []))
        conditions_count = len(self.query_config.get('conditions', []))
        joins_count = len(self.query_config.get('joins', []))
        group_by_count = len(self.query_config.get('groupBy', []))
        
        complexity = 'simple'
        if columns_count > 20 or joins_count > 3 or group_by_count > 2:
            complexity = 'complex'
        elif columns_count > 10 or joins_count > 1:
            complexity = 'medium'
        
        return {
            'complexity': complexity,
            'selected_columns_count': columns_count,
            'conditions_count': conditions_count,
            'joins_count': joins_count,
            'group_by_count': group_by_count,
            'has_aggregates': group_by_count > 0,
            'estimated_rows': self.query_config.get('limit', 1000),
        }


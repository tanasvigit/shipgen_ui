from typing import List, Optional, Any
import uuid
import csv
import json
from datetime import datetime
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.report import Report
from app.models.user import User
from app.utils.report_schema_registry import ReportSchemaRegistry
from app.utils.report_query_converter import ReportQueryConverter
from app.utils.report_query_validator import ReportQueryValidator
from app.utils.computed_column_validator import ComputedColumnValidator

router = APIRouter(prefix="/int/v1/reports", tags=["reports"])


class ReportCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category_uuid: Optional[str] = None
    subject_uuid: Optional[str] = None
    subject_type: Optional[str] = None
    query_config: dict[str, Any]
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    tags: Optional[list[str]] = None
    options: Optional[dict[str, Any]] = None
    type: Optional[str] = None


class ReportUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_uuid: Optional[str] = None
    query_config: Optional[dict[str, Any]] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    tags: Optional[list[str]] = None
    options: Optional[dict[str, Any]] = None
    status: Optional[str] = None


def _serialize_report(report: Report) -> dict:
    """
    Convert a Report SQLAlchemy model to a plain dict safe for JSON serialization.
    Removes internal SQLAlchemy state and returns only field data.
    """
    data = report.__dict__.copy()
    data.pop("_sa_instance_state", None)
    return data


@router.get("/", response_model=List[dict])
def list_reports(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    reports = (
        db.query(Report)
        .filter(
            Report.company_uuid == current.company_uuid,
            Report.deleted_at.is_(None),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [_serialize_report(r) for r in reports]


@router.get("/tables", response_model=dict)
def get_tables(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    extension: str = Query("core", description="Extension filter"),
    category: Optional[str] = Query(None, description="Category filter"),
):
    """List available database tables and schema metadata for reporting."""
    registry = ReportSchemaRegistry()
    tables = registry.get_available_tables(extension, category)

    return {
        "success": True,
        "tables": tables,
        "meta": {
            "total_tables": len(tables),
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


@router.get("/tables/{table}/schema", response_model=dict)
def get_table_schema(
    table: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Get full schema (columns + relationships) for a single table."""
    registry = ReportSchemaRegistry()

    try:
        schema = registry.get_table_schema(table)
        return {
            "success": True,
            "schema": schema,
            "meta": {
                "table_name": table,
                "columns_count": len(schema.get("columns", [])),
                "relationships_count": len(schema.get("relationships", [])),
                "timestamp": datetime.utcnow().isoformat(),
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/tables/{table}/columns", response_model=dict)
def get_table_columns(
    table: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Get columns for a table."""
    registry = ReportSchemaRegistry()

    if not registry.has_table(table):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Table '{table}' not found")

    columns = registry.get_table_columns(table)
    return {
        "success": True,
        "columns": columns,
        "meta": {
            "table_name": table,
            "total_columns": len(columns),
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


@router.get("/tables/{table}/relationships", response_model=dict)
def get_table_relationships(
    table: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Get foreign-key style relationships for a table."""
    registry = ReportSchemaRegistry()

    if not registry.has_table(table):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Table '{table}' not found")

    relationships = registry.get_table_relationships(table)
    return {
        "success": True,
        "relationships": relationships,
        "meta": {
            "table_name": table,
            "total_relationships": len(relationships),
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


@router.post("/validate-query", response_model=dict)
def validate_query(
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Validate a report query_config without executing it."""
    query_config = payload.get("query_config")

    if not query_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"valid": False, "errors": ["Query configuration is required"]},
        )

    registry = ReportSchemaRegistry()
    validator = ReportQueryValidator(registry)
    validation_result = validator.validate(query_config)

    if validation_result["valid"]:
        return {
            "valid": True,
            "message": "Query configuration is valid",
            "warnings": validation_result["warnings"],
            "summary": validation_result["summary"],
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
            },
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "valid": False,
                "errors": validation_result["errors"],
                "warnings": validation_result["warnings"],
                "summary": validation_result["summary"],
            },
        )


@router.post("/execute-query", response_model=dict)
def execute_query(
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Execute a one-off query_config directly (not a saved report)."""
    query_config = payload.get("query_config")

    if not query_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_CONFIGURATION",
                    "message": "Query configuration is required",
                },
            },
        )

    registry = ReportSchemaRegistry()
    validator = ReportQueryValidator(registry)
    validation_result = validator.validate(query_config)

    if not validation_result["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "VALIDATION_FAILED",
                    "message": "Query validation failed",
                    "errors": validation_result["errors"],
                    "warnings": validation_result["warnings"],
                },
            },
        )

    converter = ReportQueryConverter(registry, query_config, current.company_uuid)
    result = converter.execute(db)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "EXECUTION_FAILED",
                    "message": result.get("error", "Query execution failed"),
                },
            },
        )

    return result


@router.get("/export-formats", response_model=dict)
def get_export_formats(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """List supported export formats for reports/queries."""
    registry = ReportSchemaRegistry()
    converter = ReportQueryConverter(registry, {"table": {"name": "users"}, "columns": []}, None)
    formats = converter.get_available_export_formats()

    return {
        "success": True,
        "formats": formats,
        "meta": {
            "total_formats": len(formats),
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


@router.post("/validate-computed-column", response_model=dict)
def validate_computed_column(
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Validate a computed column expression against a table."""
    expression = payload.get("expression")
    table_name = payload.get("table_name")

    if not expression:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"valid": False, "errors": ["Expression is required"]},
        )

    if not table_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"valid": False, "errors": ["Table name is required"]},
        )

    registry = ReportSchemaRegistry()
    validator = ComputedColumnValidator(registry)
    validation_result = validator.validate(expression, table_name)

    if validation_result["valid"]:
        return {
            "valid": True,
            "message": "Expression is valid",
            "meta": {
                "expression": expression,
                "table_name": table_name,
                "timestamp": datetime.utcnow().isoformat(),
            },
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "valid": False,
                "errors": validation_result["errors"],
                "meta": {
                    "expression": expression,
                    "table_name": table_name,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            },
        )


@router.post("/analyze-query", response_model=dict)
def analyze_query(
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Analyze a query_config and return complexity + recommendations."""
    query_config = payload.get("query_config")

    if not query_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_CONFIGURATION",
                    "message": "Query configuration is required",
                },
            },
        )

    registry = ReportSchemaRegistry()
    converter = ReportQueryConverter(registry, query_config, current.company_uuid)
    validator = ReportQueryValidator(registry)

    analysis = converter.get_query_analysis()
    validation_result = validator.validate(query_config)

    recommendations = _get_query_recommendations(analysis, validation_result)

    return {
        "success": True,
        "analysis": analysis,
        "validation": validation_result,
        "recommendations": recommendations,
        "meta": {
            "analyzed_at": datetime.utcnow().isoformat(),
        },
    }


@router.post("/export-query", response_model=dict)
def export_query(
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Execute and export a one-off query in a given format."""
    query_config = payload.get("query_config")
    export_format = payload.get("format", "csv")
    options = payload.get("options", {})

    if not query_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_CONFIGURATION",
                    "message": "Query configuration is required",
                },
            },
        )

    registry = ReportSchemaRegistry()
    validator = ReportQueryValidator(registry)
    validation_result = validator.validate(query_config)

    if not validation_result["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "VALIDATION_FAILED",
                    "message": "Query validation failed",
                    "errors": validation_result["errors"],
                },
            },
        )

    converter = ReportQueryConverter(registry, query_config, current.company_uuid)
    result = converter.execute(db)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "EXECUTION_FAILED",
                    "message": result.get("error", "Query execution failed"),
                },
            },
        )

    if export_format == "csv":
        return _export_csv(result["data"], result["columns"], "export")
    elif export_format == "json":
        return _export_json(result["data"], result["columns"])
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_FORMAT",
                    "message": f"Unsupported export format: {export_format}",
                    "allowed_formats": ["csv", "json", "xlsx"],
                },
            },
        )


@router.get("/query-recommendations", response_model=List[dict])
def get_query_recommendations(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Return general query best-practice recommendations."""
    return [
        {
            "type": "performance",
            "priority": "medium",
            "message": "Consider adding indexes on frequently filtered columns",
            "suggestions": [
                "Add indexes on foreign key columns",
                "Add indexes on date/time columns used in filters",
            ],
        },
        {
            "type": "best_practice",
            "priority": "low",
            "message": "Use appropriate data types for better performance",
            "suggestions": [
                "Use integers for IDs instead of strings where possible",
                "Use appropriate date/time types",
            ],
        },
    ]


@router.get("/{id}", response_model=dict)
def get_report(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    report = (
        db.query(Report)
        .filter(
            Report.company_uuid == current.company_uuid,
            (Report.uuid == id) | (Report.public_id == id),
            Report.deleted_at.is_(None),
        )
        .first()
    )
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return _serialize_report(report)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_report(
    payload: ReportCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    report = Report()
    report.uuid = str(uuid.uuid4())
    report.company_uuid = current.company_uuid
    report.created_by_uuid = current.uuid
    report.title = payload.title
    report.description = payload.description
    report.category_uuid = payload.category_uuid
    report.subject_uuid = payload.subject_uuid
    report.subject_type = payload.subject_type
    report.query_config = payload.query_config
    report.period_start = payload.period_start
    report.period_end = payload.period_end
    report.tags = payload.tags
    report.options = payload.options
    report.type = payload.type
    report.status = "draft"
    
    db.add(report)
    db.commit()
    db.refresh(report)
    return _serialize_report(report)


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_report(
    id: str,
    payload: ReportUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    report = (
        db.query(Report)
        .filter(
            Report.company_uuid == current.company_uuid,
            (Report.uuid == id) | (Report.public_id == id),
            Report.deleted_at.is_(None),
        )
        .first()
    )
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(report, field):
            setattr(report, field, value)
    
    report.updated_by_uuid = current.uuid
    db.add(report)
    db.commit()
    db.refresh(report)
    return _serialize_report(report)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_report(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    report = (
        db.query(Report)
        .filter(
            Report.company_uuid == current.company_uuid,
            (Report.uuid == id) | (Report.public_id == id),
            Report.deleted_at.is_(None),
        )
        .first()
    )
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    
    report.deleted_at = datetime.utcnow()
    db.add(report)
    db.commit()
    return _serialize_report(report)


@router.post("/{id}/execute", response_model=dict)
def execute_report(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    report = db.query(Report).filter(
        Report.company_uuid == current.company_uuid,
        (Report.uuid == id) | (Report.public_id == id),
        Report.deleted_at.is_(None)
    ).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    
    if not report.query_config:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Report has no query configuration")
    
    # Validate query configuration
    registry = ReportSchemaRegistry()
    validator = ReportQueryValidator(registry)
    validation_result = validator.validate(report.query_config)
    
    if not validation_result['valid']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Query validation failed",
                "errors": validation_result['errors'],
                "warnings": validation_result['warnings']
            }
        )
    
    # Execute query
    converter = ReportQueryConverter(registry, report.query_config, current.company_uuid)
    result = converter.execute(db)
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get('error', 'Query execution failed')
        )
    
    # Update report execution stats
    report.last_executed_at = datetime.utcnow()
    report.execution_time = result['meta']['execution_time_ms']
    report.row_count = result['meta']['total_rows']
    report.result_columns = result['columns']
    report.data = result['data']
    db.add(report)
    db.commit()
    
    return result


@router.post("/{id}/export", response_model=dict)
def export_report(
    id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    export_format = payload.get("format", "csv")
    report = db.query(Report).filter(
        Report.company_uuid == current.company_uuid,
        (Report.uuid == id) | (Report.public_id == id),
        Report.deleted_at.is_(None)
    ).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    
    if not report.query_config:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Report has no query configuration")
    
    # Execute query if not already executed or data is stale
    if not report.data or not report.last_executed_at:
        # Execute the report first
        registry = ReportSchemaRegistry()
        converter = ReportQueryConverter(registry, report.query_config, current.company_uuid)
        result = converter.execute(db)
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('error', 'Query execution failed')
            )
        
        report.data = result['data']
        report.result_columns = result['columns']
        report.last_executed_at = datetime.utcnow()
        db.add(report)
        db.commit()
    
    # Export based on format
    if export_format == "csv":
        return _export_csv(report.data, report.result_columns, report.title)
    elif export_format == "json":
        return _export_json(report.data, report.result_columns)
    elif export_format == "xlsx":
        return _export_xlsx(report.data, report.result_columns, report.title)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported export format: {export_format}"
        )


def _export_csv(data: List[dict], columns: List[dict], title: str) -> Response:
    """Export data as CSV."""
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=[col['name'] for col in columns])
    writer.writeheader()
    writer.writerows(data)
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={title.replace(' ', '_')}.csv"
        }
    )


def _export_json(data: List[dict], columns: List[dict]) -> dict:
    """Export data as JSON."""
    return {
        "success": True,
        "format": "json",
        "columns": columns,
        "data": data,
        "meta": {
            "total_rows": len(data),
        }
    }


def _export_xlsx(data: List[dict], columns: List[dict], title: str) -> dict:
    """Export data as XLSX using openpyxl."""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment
        import base64
        from io import BytesIO
        
        wb = Workbook()
        ws = wb.active
        ws.title = title[:31]  # Excel sheet name limit
        
        # Write headers
        header_row = [col.get("label", col.get("key", "")) for col in columns]
        ws.append(header_row)
        
        # Style headers
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center")
        
        # Write data
        for row in data:
            row_data = []
            for col in columns:
                key = col.get("key", "")
                value = row.get(key, "")
                row_data.append(value)
            ws.append(row_data)
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Save to BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        # Encode to base64
        file_content = output.read()
        base64_content = base64.b64encode(file_content).decode('utf-8')
        
        return {
            "success": True,
            "format": "xlsx",
            "filename": f"{title}.xlsx",
            "content": base64_content,
            "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
    except ImportError:
        return {
            "success": False,
            "message": "XLSX export requires openpyxl library",
            "format": "xlsx",
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error exporting XLSX: {str(e)}",
            "format": "xlsx",
        }


@router.get("/tables", response_model=dict)
def get_tables(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    extension: str = Query("core", description="Extension filter"),
    category: Optional[str] = Query(None, description="Category filter"),
):
    registry = ReportSchemaRegistry()
    tables = registry.get_available_tables(extension, category)
    
    return {
        "success": True,
        "tables": tables,
        "meta": {
            "total_tables": len(tables),
            "timestamp": datetime.utcnow().isoformat(),
        }
    }


@router.get("/tables/{table}/schema", response_model=dict)
def get_table_schema(
    table: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    registry = ReportSchemaRegistry()
    
    try:
        schema = registry.get_table_schema(table)
        return {
            "success": True,
            "schema": schema,
            "meta": {
                "table_name": table,
                "columns_count": len(schema.get("columns", [])),
                "relationships_count": len(schema.get("relationships", [])),
                "timestamp": datetime.utcnow().isoformat(),
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/tables/{table}/columns", response_model=dict)
def get_table_columns(
    table: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    registry = ReportSchemaRegistry()
    
    if not registry.has_table(table):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Table '{table}' not found")
    
    columns = registry.get_table_columns(table)
    return {
        "success": True,
        "columns": columns,
        "meta": {
            "table_name": table,
            "total_columns": len(columns),
            "timestamp": datetime.utcnow().isoformat(),
        }
    }


@router.get("/tables/{table}/relationships", response_model=dict)
def get_table_relationships(
    table: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    registry = ReportSchemaRegistry()
    
    if not registry.has_table(table):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Table '{table}' not found")
    
    relationships = registry.get_table_relationships(table)
    return {
        "success": True,
        "relationships": relationships,
        "meta": {
            "table_name": table,
            "total_relationships": len(relationships),
            "timestamp": datetime.utcnow().isoformat(),
        }
    }


@router.post("/validate-query", response_model=dict)
def validate_query(
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    query_config = payload.get("query_config")
    
    if not query_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"valid": False, "errors": ["Query configuration is required"]}
        )
    
    registry = ReportSchemaRegistry()
    validator = ReportQueryValidator(registry)
    validation_result = validator.validate(query_config)
    
    if validation_result['valid']:
        return {
            "valid": True,
            "message": "Query configuration is valid",
            "warnings": validation_result['warnings'],
            "summary": validation_result['summary'],
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
            }
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "valid": False,
                "errors": validation_result['errors'],
                "warnings": validation_result['warnings'],
                "summary": validation_result['summary'],
            }
        )


@router.post("/execute-query", response_model=dict)
def execute_query(
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    query_config = payload.get("query_config")
    
    if not query_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_CONFIGURATION",
                    "message": "Query configuration is required"
                }
            }
        )
    
    # Validate query configuration
    registry = ReportSchemaRegistry()
    validator = ReportQueryValidator(registry)
    validation_result = validator.validate(query_config)
    
    if not validation_result['valid']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "VALIDATION_FAILED",
                    "message": "Query validation failed",
                    "errors": validation_result['errors'],
                    "warnings": validation_result['warnings']
                }
            }
        )
    
    # Execute query with timeout protection
    converter = ReportQueryConverter(registry, query_config, current.company_uuid)
    result = converter.execute(db)
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "EXECUTION_FAILED",
                    "message": result.get('error', 'Query execution failed')
                }
            }
        )
    
    return result


@router.get("/export-formats", response_model=dict)
def get_export_formats(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    registry = ReportSchemaRegistry()
    converter = ReportQueryConverter(registry, {"table": {"name": "users"}, "columns": []}, None)
    formats = converter.get_available_export_formats()
    
    return {
        "success": True,
        "formats": formats,
        "meta": {
            "total_formats": len(formats),
            "timestamp": datetime.utcnow().isoformat(),
        }
    }


@router.post("/validate-computed-column", response_model=dict)
def validate_computed_column(
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    expression = payload.get("expression")
    table_name = payload.get("table_name")
    
    if not expression:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"valid": False, "errors": ["Expression is required"]}
        )
    
    if not table_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"valid": False, "errors": ["Table name is required"]}
        )
    
    registry = ReportSchemaRegistry()
    validator = ComputedColumnValidator(registry)
    validation_result = validator.validate(expression, table_name)
    
    if validation_result['valid']:
        return {
            "valid": True,
            "message": "Expression is valid",
            "meta": {
                "expression": expression,
                "table_name": table_name,
                "timestamp": datetime.utcnow().isoformat(),
            }
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "valid": False,
                "errors": validation_result['errors'],
                "meta": {
                    "expression": expression,
                    "table_name": table_name,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            }
        )


@router.post("/analyze-query", response_model=dict)
def analyze_query(
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    query_config = payload.get("query_config")
    
    if not query_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_CONFIGURATION",
                    "message": "Query configuration is required"
                }
            }
        )
    
    registry = ReportSchemaRegistry()
    converter = ReportQueryConverter(registry, query_config, current.company_uuid)
    validator = ReportQueryValidator(registry)
    
    analysis = converter.get_query_analysis()
    validation_result = validator.validate(query_config)
    
    # Generate recommendations
    recommendations = _get_query_recommendations(analysis, validation_result)
    
    return {
        "success": True,
        "analysis": analysis,
        "validation": validation_result,
        "recommendations": recommendations,
        "meta": {
            "analyzed_at": datetime.utcnow().isoformat(),
        }
    }


@router.post("/export-query", response_model=dict)
def export_query(
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    query_config = payload.get("query_config")
    export_format = payload.get("format", "csv")
    options = payload.get("options", {})
    
    if not query_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_CONFIGURATION",
                    "message": "Query configuration is required"
                }
            }
        )
    
    # Validate query configuration
    registry = ReportSchemaRegistry()
    validator = ReportQueryValidator(registry)
    validation_result = validator.validate(query_config)
    
    if not validation_result['valid']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "VALIDATION_FAILED",
                    "message": "Query validation failed",
                    "errors": validation_result['errors']
                }
            }
        )
    
    # Execute query
    converter = ReportQueryConverter(registry, query_config, current.company_uuid)
    result = converter.execute(db)
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "EXECUTION_FAILED",
                    "message": result.get('error', 'Query execution failed')
                }
            }
        )
    
    # Export based on format
    if export_format == "csv":
        return _export_csv(result['data'], result['columns'], "export")
    elif export_format == "json":
        return _export_json(result['data'], result['columns'])
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_FORMAT",
                    "message": f"Unsupported export format: {export_format}",
                    "allowed_formats": ["csv", "json", "xlsx"]
                }
            }
        )


@router.get("/query-recommendations", response_model=List[dict])
def get_query_recommendations(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    # Return general query recommendations
    return [
        {
            "type": "performance",
            "priority": "medium",
            "message": "Consider adding indexes on frequently filtered columns",
            "suggestions": [
                "Add indexes on foreign key columns",
                "Add indexes on date/time columns used in filters",
            ]
        },
        {
            "type": "best_practice",
            "priority": "low",
            "message": "Use appropriate data types for better performance",
            "suggestions": [
                "Use integers for IDs instead of strings where possible",
                "Use appropriate date/time types",
            ]
        }
    ]


def _get_query_recommendations(analysis: dict, validation_result: dict) -> List[dict]:
    """Generate query recommendations based on analysis."""
    recommendations = []
    
    # Performance recommendations
    if analysis.get('complexity') == 'complex':
        recommendations.append({
            "type": "performance",
            "priority": "high",
            "message": "Consider simplifying the query to improve performance",
            "suggestions": [
                "Reduce the number of selected columns",
                "Add more specific filters",
                "Remove unnecessary joins",
            ]
        })
    
    if analysis.get('joins_count', 0) > 3:
        recommendations.append({
            "type": "performance",
            "priority": "medium",
            "message": "Multiple joins may impact performance",
            "suggestions": [
                "Consider if all joins are necessary",
                "Ensure join conditions use indexed columns",
            ]
        })
    
    if analysis.get('selected_columns_count', 0) > 20:
        recommendations.append({
            "type": "performance",
            "priority": "medium",
            "message": "Selecting many columns may slow down the query",
            "suggestions": [
                "Select only the columns you need",
                "Consider creating multiple smaller reports",
            ]
        })
    
    # Add validation-based recommendations
    if validation_result.get('warnings'):
        recommendations.append({
            "type": "validation",
            "priority": "low",
            "message": "Query has validation warnings",
            "suggestions": validation_result['warnings'],
        })
    
    return recommendations


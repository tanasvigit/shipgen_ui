from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.api import api_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="ShipGen API",
        description="""
        ShipGen API - Complete REST API for Fleet Management and Logistics Platform.
        
        This API provides comprehensive endpoints for:
        
        * **Authentication & Authorization**: JWT-based auth, 2FA, roles, permissions
        * **Fleet Operations**: Orders, drivers, vehicles, tracking, telematics
        * **Storefront**: Products, customers, carts, orders, checkouts
        * **Core Utilities**: Files, chat, comments, settings, webhooks, dashboards, reports
        * **Administration**: API credentials, activities, extensions, custom fields
        
        ## Authentication
        
        Most endpoints require authentication via JWT token. Include the token in the Authorization header:
        ```
        Authorization: Bearer <your-token>
        ```
        
        ## API Versions
        
        * `/int/v1/*` - Internal API endpoints (admin/management)
        * `/fleetops/v1/*` - Fleet operations endpoints
        * `/storefront/v1/*` - Storefront endpoints
        * `/v1/*` - Public API endpoints
        
        ## Rate Limiting
        
        API requests are rate-limited. Check response headers for rate limit information.
        
        ## Support
        
        For API support, contact: support@shipgen.net
        """,
        version="1.0.0",
        terms_of_service="https://shipgen.net/terms",
        contact={
            "name": "ShipGen API Support",
            "url": "https://shipgen.net/support",
            "email": "support@shipgen.net",
        },
        license_info={
            "name": "Proprietary",
            "url": "https://shipgen.net/license",
        },
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": 2,
            "defaultModelExpandDepth": 2,
            "docExpansion": "list",
            "filter": True,
            "showExtensions": True,
            "showCommonExtensions": True,
            "tryItOutEnabled": True,
        },
    )

    # Custom OpenAPI schema with organized tags
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=[
                {
                    "name": "Authentication",
                    "description": "User authentication and authorization endpoints",
                },
                {
                    "name": "Users",
                    "description": "User management endpoints",
                },
                {
                    "name": "Companies",
                    "description": "Company/organization management",
                },
                {
                    "name": "Roles & Permissions",
                    "description": "Role-based access control (RBAC)",
                },
                {
                    "name": "2FA",
                    "description": "Two-factor authentication",
                },
                {
                    "name": "Notifications",
                    "description": "Notification management",
                },
                {
                    "name": "FleetOps - Orders",
                    "description": "Order management and tracking",
                },
                {
                    "name": "FleetOps - Drivers",
                    "description": "Driver management",
                },
                {
                    "name": "FleetOps - Vehicles",
                    "description": "Vehicle management",
                },
                {
                    "name": "FleetOps - Contacts",
                    "description": "Contact management",
                },
                {
                    "name": "FleetOps - Vendors",
                    "description": "Vendor management",
                },
                {
                    "name": "FleetOps - Places",
                    "description": "Place/location management",
                },
                {
                    "name": "FleetOps - Issues",
                    "description": "Issue tracking",
                },
                {
                    "name": "FleetOps - Fuel Reports",
                    "description": "Fuel reporting",
                },
                {
                    "name": "FleetOps - Entities",
                    "description": "Entity management",
                },
                {
                    "name": "FleetOps - Payloads",
                    "description": "Payload management",
                },
                {
                    "name": "FleetOps - Zones",
                    "description": "Zone management",
                },
                {
                    "name": "FleetOps - Service Areas",
                    "description": "Service area management",
                },
                {
                    "name": "FleetOps - Fleets",
                    "description": "Fleet management",
                },
                {
                    "name": "FleetOps - Tracking",
                    "description": "Tracking number and status management",
                },
                {
                    "name": "Service Rates",
                    "description": "Service rate management",
                },
                {
                    "name": "Service Quotes",
                    "description": "Service quote generation",
                },
                {
                    "name": "Telematics",
                    "description": "Telematics and device management",
                },
                {
                    "name": "Devices",
                    "description": "IoT device management",
                },
                {
                    "name": "Storefront - Customers",
                    "description": "Customer management",
                },
                {
                    "name": "Storefront - Products",
                    "description": "Product catalog management",
                },
                {
                    "name": "Storefront - Carts",
                    "description": "Shopping cart management",
                },
                {
                    "name": "Storefront - Orders",
                    "description": "Storefront order management",
                },
                {
                    "name": "Storefront - Checkouts",
                    "description": "Checkout process",
                },
                {
                    "name": "Storefront - Categories",
                    "description": "Product category management",
                },
                {
                    "name": "Storefront - Reviews",
                    "description": "Product review management",
                },
                {
                    "name": "Storefront - Food Trucks",
                    "description": "Food truck management",
                },
                {
                    "name": "Storefront - Stores",
                    "description": "Store management",
                },
                {
                    "name": "Storefront - Networks",
                    "description": "Store network management",
                },
                {
                    "name": "Files",
                    "description": "File upload and management",
                },
                {
                    "name": "Comments",
                    "description": "Comment system",
                },
                {
                    "name": "Settings",
                    "description": "System and company settings",
                },
                {
                    "name": "Webhooks",
                    "description": "Webhook endpoint management",
                },
                {
                    "name": "Dashboards",
                    "description": "Dashboard and widget management",
                },
                {
                    "name": "Reports",
                    "description": "Report generation and execution",
                },
                {
                    "name": "Chat",
                    "description": "Chat channels, messages, and participants",
                },
                {
                    "name": "API Management",
                    "description": "API credentials, events, and request logs",
                },
                {
                    "name": "Activities",
                    "description": "Activity logging",
                },
                {
                    "name": "Extensions",
                    "description": "Extension management",
                },
                {
                    "name": "Custom Fields",
                    "description": "Custom field management",
                },
                {
                    "name": "Transactions",
                    "description": "Transaction management",
                },
                {
                    "name": "Schedules",
                    "description": "Schedule and availability management",
                },
                {
                    "name": "Groups",
                    "description": "User group management",
                },
                {
                    "name": "User Devices",
                    "description": "User device management",
                },
                {
                    "name": "Lookup",
                    "description": "Lookup utilities (timezones, currencies, etc.)",
                },
                {
                    "name": "Installer",
                    "description": "System installation endpoints",
                },
                {
                    "name": "Onboard",
                    "description": "Onboarding endpoints",
                },
            ],
        )
        
        # Add security schemes
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT token authentication. Format: Bearer <token>",
            }
        }
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    # Add CORS middleware
    # Build list of allowed origins - must be specific (not wildcard) when credentials=True
    cors_origins = [
        "http://localhost:4201",
        "http://localhost:4200",
        "http://127.0.0.1:4201",
        "http://127.0.0.1:4200",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.0.171:5173",
        "http://192.168.1.129:5173",
    ]
    
    # Add configured origins from settings
    cors_origins.extend([str(origin) for origin in settings.BACKEND_CORS_ORIGINS])
    
    # Remove duplicates while preserving order
    seen = set()
    cors_origins = [x for x in cors_origins if not (x in seen or seen.add(x))]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    @app.get("/health", tags=["Health"])
    async def health():
        """
        Health check endpoint.
        
        Returns the health status of the API.
        """
        return {"status": "ok", "service": "ShipGen API"}

    @app.get("/", tags=["Root"])
    async def root():
        """
        API root endpoint.
        
        Returns API information and links to documentation.
        """
        return {
            "name": "ShipGen API",
            "version": "1.0.0",
            "description": "Fleet Management and Logistics Platform API",
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
        }

    app.include_router(api_router)

    return app


app = create_app()




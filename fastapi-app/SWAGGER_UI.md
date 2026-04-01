# Swagger UI Documentation

## Accessing Swagger UI

The TechLiv API includes comprehensive Swagger UI documentation that is automatically generated from the FastAPI codebase.

### URLs

Once the FastAPI server is running, you can access:

- **Swagger UI**: `http://localhost:9001/docs`
- **ReDoc**: `http://localhost:9001/redoc`
- **OpenAPI JSON Schema**: `http://localhost:9001/openapi.json`

### Features

The Swagger UI includes:

1. **Interactive API Testing**: Try out endpoints directly from the browser
2. **Organized Tags**: All endpoints are organized by functional area:
   - Authentication
   - Users & Companies
   - FleetOps (Orders, Drivers, Vehicles, etc.)
   - Storefront (Products, Customers, Orders, etc.)
   - Core Utilities (Files, Chat, Comments, Settings, etc.)
   - Reports & Dashboards
   - API Management
   - And more...

3. **Authentication Support**: 
   - Click the "Authorize" button at the top
   - Enter your JWT token in the format: `Bearer <your-token>`
   - All authenticated endpoints will use this token

4. **Request/Response Examples**: See example request bodies and responses for each endpoint

5. **Schema Documentation**: View detailed Pydantic models for request/response schemas

### Running the Server

To start the FastAPI server with Swagger UI:

```bash
cd fastapi-app
uvicorn app.main:app --reload --host 0.0.0.0 --port 9001
```

Or using the development script:

```bash
python -m uvicorn app.main:app --reload --port 9001
```

### Customization

The Swagger UI configuration can be customized in `app/main.py`:

- **Title & Description**: Set in the `FastAPI()` constructor
- **Tags**: Organized in the `custom_openapi()` function
- **Security Schemes**: JWT Bearer token authentication is configured
- **UI Parameters**: Customized via `swagger_ui_parameters`

### API Documentation Structure

The API is organized into the following main sections:

1. **Internal API** (`/int/v1/*`): Admin and management endpoints
2. **FleetOps API** (`/fleetops/v1/*`): Fleet operations endpoints
3. **Storefront API** (`/storefront/v1/*`): Storefront endpoints
4. **Public API** (`/v1/*`): Public-facing endpoints

### Tips

- Use the search/filter box to quickly find endpoints
- Expand/collapse sections using the arrow icons
- Click "Try it out" on any endpoint to test it
- View the request/response schemas by expanding the models section
- Use the "Authorize" button to set your authentication token once


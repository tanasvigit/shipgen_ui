# Test Data Generation and Testing Guide

This guide explains how to generate test data for all API endpoints and test them locally.

## Quick Start

### Step 1: Generate Test Data

```bash
# Using Docker
docker-compose exec api python scripts/generate_test_data.py

# Or locally (if API is running locally)
cd fastapi-app
python scripts/generate_test_data.py
```

This script will:
- ✅ Create test users (admin, manager, dispatcher, driver)
- ✅ Create test companies
- ✅ Create test roles and permissions
- ✅ Create test contacts, vendors, places
- ✅ Create test drivers, vehicles, orders
- ✅ Create test service rates
- ✅ Create test devices
- ✅ Create test storefront data
- ✅ Save all test data to `test_data.json`

### Step 2: Test All Endpoints

```bash
# Using Docker (requires API to be running)
docker-compose exec api python scripts/test_all_endpoints.py

# Or locally (requires API to be running on localhost:9001)
cd fastapi-app
python scripts/test_all_endpoints.py
```

This script will:
- ✅ Login with test credentials
- ✅ Test all GET endpoints (list operations)
- ✅ Test all POST endpoints (create operations)
- ✅ Test all PATCH/PUT endpoints (update operations)
- ✅ Validate responses
- ✅ Save test results to `test_results.json`

### Step 3: Review Documentation

Open `API_TEST_DATA_DOCUMENTATION.md` for:
- Complete list of all endpoints
- Request/response examples
- Database mapping information
- Test data for each endpoint

## Files Created

1. **`scripts/generate_test_data.py`** - Generates test data in database
2. **`scripts/test_all_endpoints.py`** - Tests all endpoints with requests
3. **`API_TEST_DATA_DOCUMENTATION.md`** - Complete endpoint documentation
4. **`test_data.json`** - Generated test data (UUIDs, etc.)
5. **`test_results.json`** - Test execution results

## Test Data Summary

The test data generator creates:

| Category | Items Created |
|----------|---------------|
| Users | 3 (manager, dispatcher, driver) |
| Companies | 2 additional companies |
| Roles | 3 (fleet-manager, dispatcher, driver) |
| Permissions | 5 (orders.*, drivers.*, vehicles.*) |
| Contacts | 2 |
| Vendors | 2 |
| Places | 2 |
| Drivers | 2 |
| Vehicles | 2 |
| Orders | 2 |
| Service Rates | 1 with rate fees |
| Devices | 1 |
| Storefront Products | 1 |
| Storefront Carts | 1 |

## Database Validation

All test data is validated to ensure:
- ✅ Required fields are present
- ✅ Data types match database schema
- ✅ Foreign key relationships are valid
- ✅ UUIDs are properly formatted
- ✅ Timestamps are in correct format

## Using Test Data in Swagger UI

1. **Login:**
   - Go to http://localhost:9001/docs
   - Find `POST /int/v1/auth/login`
   - Use: `{"identity": "admin@techliv.net", "password": "admin123"}`
   - Copy the token from response

2. **Authorize:**
   - Click "Authorize" button (top right)
   - Enter: `Bearer <your-token>`
   - Click "Authorize"

3. **Test Endpoints:**
   - Find any endpoint in Swagger UI
   - Use test data from `API_TEST_DATA_DOCUMENTATION.md`
   - Click "Try it out"
   - Enter test data
   - Click "Execute"

## Troubleshooting

### "Module not found" errors
- Make sure you're running from the correct directory
- Check that all dependencies are installed: `pip install -r requirements.txt`

### "Connection refused" errors
- Make sure the API is running: `docker-compose ps`
- Check API logs: `docker-compose logs api`

### "Authentication failed" errors
- Make sure initial users are created: `python scripts/create_initial_users.py`
- Use correct credentials from `QUICK_START.md`

### "Foreign key constraint" errors
- Make sure test data is generated in order (run `generate_test_data.py` first)
- Check that company UUID exists before creating related records

## Next Steps

1. Review `API_TEST_DATA_DOCUMENTATION.md` for complete endpoint details
2. Use test data in your API client or Postman
3. Customize test data in `generate_test_data.py` for your needs
4. Add more test cases in `test_all_endpoints.py`

## Support

For issues:
- Check database schema: `alembic/versions/`
- Review model definitions: `app/models/`
- Check schema definitions: `app/schemas/`


# Quick Start Guide - Create Users and Login

## Step 1: Create Initial Users

Run the script to create two users (super admin and regular user):

```bash
# If using Docker
docker-compose exec api python scripts/create_initial_users.py

# If running locally
cd fastapi-app
python scripts/create_initial_users.py
```

This will create:
- **Super Admin:** admin@techliv.net / admin123
- **Regular User:** user@techliv.net / user123

## Step 2: Login

### Using curl:

```bash
# Login as Super Admin
curl -X POST http://localhost:9001/int/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identity": "admin@techliv.net",
    "password": "admin123"
  }'
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "type": "admin"
}
```

### Using Swagger UI:

1. Open http://localhost:9001/docs
2. Navigate to **Authentication** → **POST /int/v1/auth/login**
3. Click "Try it out"
4. Enter:
   ```json
   {
     "identity": "admin@techliv.net",
     "password": "admin123"
   }
   ```
5. Click "Execute"
6. Copy the token from the response

## Step 3: Use the Token

### Using curl with token:

```bash
# Set token variable
TOKEN="your_token_here"

# Get current user info
curl -X GET http://localhost:9001/int/v1/users/current \
  -H "Authorization: Bearer $TOKEN"

# Get bootstrap data
curl -X GET http://localhost:9001/int/v1/auth/bootstrap \
  -H "Authorization: Bearer $TOKEN"
```

### Using Swagger UI with token:

1. Click the **Authorize** button (top right)
2. Enter: `Bearer your_token_here`
3. Click "Authorize"
4. Now you can test all protected endpoints

## Step 4: Create Additional Users (via API)

After logging in as admin, you can create more users:

```bash
# Get company UUID first
COMPANY_UUID=$(curl -s -X GET http://localhost:9001/int/v1/auth/bootstrap \
  -H "Authorization: Bearer $TOKEN" | jq -r '.organizations[0].uuid')

# Create a new user
curl -X POST http://localhost:9001/int/v1/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"name\": \"John Doe\",
    \"email\": \"john@techliv.net\",
    \"phone\": \"+1234567893\",
    \"password\": \"password123\",
    \"company_uuid\": \"$COMPANY_UUID\",
    \"timezone\": \"UTC\",
    \"country\": \"US\"
  }"
```

## Default Credentials Summary

| User Type | Email | Password | Role |
|-----------|-------|----------|------|
| Super Admin | admin@techliv.net | admin123 | super-admin |
| Regular User | user@techliv.net | user123 | user |

## Important Notes

⚠️ **Security:** Change default passwords in production!

🔐 **Token Expiry:** Tokens expire after 24 hours (configurable in `app/core/config.py`)

📝 **More Info:** See `CREATE_USERS.md` for detailed documentation


# Creating Initial Users

This guide explains how to create initial users for the TechLiv API, including a super admin user.

## Method 1: Using the Python Script (Recommended)

A Python script is provided to automatically create initial users.

### Prerequisites

- Docker containers are running
- Database migrations have been completed

### Steps

1. **Run the script inside the Docker container:**

```bash
docker-compose exec api python scripts/create_initial_users.py
```

Or if running locally:

```bash
cd fastapi-app
python scripts/create_initial_users.py
```

2. **The script will create:**
   - A super admin user (admin@techliv.net / admin123)
   - A regular user (user@techliv.net / user123)
   - A default company (TechLiv Company)
   - A "super-admin" role assigned to the admin user

3. **Login using the credentials:**

```bash
curl -X POST http://localhost:9001/int/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identity": "admin@techliv.net",
    "password": "admin123"
  }'
```

## Method 2: Using REST API (After First User is Created)

Once you have at least one user, you can create additional users via the REST API.

### Step 1: Login to get a token

```bash
TOKEN=$(curl -s -X POST http://localhost:9001/int/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identity": "admin@techliv.net",
    "password": "admin123"
  }' | jq -r '.token')
```

### Step 2: Create a new user

```bash
curl -X POST http://localhost:9001/int/v1/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "New User",
    "email": "newuser@techliv.net",
    "phone": "+1234567892",
    "password": "password123",
    "company_uuid": "YOUR_COMPANY_UUID",
    "timezone": "UTC",
    "country": "US"
  }'
```

### Step 3: Assign a role to the user

First, get the role ID:

```bash
ROLE_ID=$(curl -s -X GET http://localhost:9001/int/v1/roles \
  -H "Authorization: Bearer $TOKEN" | jq -r '.[] | select(.name=="super-admin") | .id')
```

Then assign the role (this requires direct database access or a custom endpoint):

```sql
INSERT INTO model_has_roles (role_id, model_type, model_uuid)
VALUES ('ROLE_ID', 'App\\Models\\User', 'USER_UUID');
```

## Default Credentials

After running the script, you'll have:

### Super Admin
- **Email:** admin@techliv.net
- **Password:** admin123
- **Type:** admin
- **Role:** super-admin

### Regular User
- **Email:** user@techliv.net
- **Password:** user123
- **Type:** user

## Security Note

⚠️ **Important:** Change the default passwords immediately after first login in a production environment!

## Troubleshooting

### "Users already exist" error

If you see this message, it means users already exist in the database. To create new users:

1. Delete existing users (via API or database)
2. Or modify the script to skip the check

### Database connection error

Make sure:
- Docker containers are running: `docker-compose ps`
- Database is accessible: `docker-compose exec db psql -U techliv -d techliv -c "SELECT 1;"`
- Migrations are complete: Check logs for migration errors

### Role assignment not working

If the super admin role is not being assigned:

1. Check if the role exists:
```sql
SELECT * FROM roles WHERE name = 'super-admin';
```

2. Check if the assignment exists:
```sql
SELECT * FROM model_has_roles WHERE model_uuid = 'ADMIN_USER_UUID';
```

3. Manually assign the role if needed (see Method 2, Step 3)


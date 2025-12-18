# Neon.tech PostgreSQL Setup

This guide walks you through setting up a PostgreSQL database on Neon.tech for your YouTube to MP3 API.

## Step 1: Create a Neon Account

1. Go to [neon.tech](https://neon.tech)
2. Sign up with GitHub or email
3. Create a new project

## Step 2: Get Your Database URL

1. After creating a project, click on "Connection String"
2. Select "Pooled connection" from the dropdown
3. Copy the connection string that looks like:
   ```
   postgresql://user:password@ep-xxxx-xxxx.us-east-1.neon.tech/dbname?sslmode=require
   ```
4. Save this URL - you'll need it for deployment

## Step 3: Initialize Your Database

### Option A: Using the provided init script

```bash
# Set your Neon DATABASE_URL
export DATABASE_URL="your-neon-connection-string-here"

# Run the initialization script
python scripts/init_db.py
```

### Option B: Manual initialization with psql

```bash
psql "your-neon-connection-string-here" -f scripts/schema.sql
```

## Step 4: Set Environment Variables

### For Local Development

Create a `.env` file (not committed to git):
```bash
DATABASE_URL="postgresql://user:password@ep-xxxx.us-east-1.neon.tech/dbname?sslmode=require"
SESSION_SECRET="your-secret-key-here"
```

Load it before running:
```bash
source .env
python main.py
```

### For Railway Deployment

1. Go to your Railway project
2. Go to Variables
3. Add these variables:
   - `DATABASE_URL`: Your Neon connection string
   - `SESSION_SECRET`: Generate a random secret key

```bash
# Generate a random secret (use this value in Railway)
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Step 5: Verify Your Setup

Test the connection:

```bash
# Set your DATABASE_URL first
export DATABASE_URL="your-neon-connection-string"

# Run the test script
python scripts/test_connection.py
```

Expected output:
```
✓ Database connection successful
✓ Tables created successfully
✓ Test data inserted
✓ All systems ready!
```

## Troubleshooting

### Connection refused
- Make sure you're using the "Pooled connection" string from Neon
- Add `?sslmode=require` to your connection string

### sslmode error
- Your Neon URL should include `?sslmode=require`
- This is required for security

### Table already exists
- This is normal if you've run the init script before
- The script safely handles existing tables

## Scaling Tips

- **Connection Pool**: Neon's "Pooled connection" is recommended for serverless deployments
- **Max Connections**: Default is fine for development
- **Storage**: Neon includes generous storage; upgrade if needed

## Security Notes

- Never commit `.env` files to git
- Rotate your `SESSION_SECRET` periodically
- Use environment variables for all secrets
- Keep your DATABASE_URL private

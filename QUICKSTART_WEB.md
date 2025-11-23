# Quick Start Guide - Luna Web Frontend

Get the Flask web frontend running in 3 simple steps!

## Prerequisites

- Docker and Docker Compose installed
- Ports 5000, 8000, and 5432 available

## Step 1: Start All Services

From the project root directory:

```bash
docker-compose up --build
```

This will start:
- **PostgreSQL** database on port 5432
- **FastAPI** backend on port 8000
- **Flask** web frontend on port 5000

Wait for the message: `Running on all addresses (0.0.0.0)`

## Step 2: Initialize Database

In a new terminal:

```bash
# Create database schema
docker-compose exec api python -c "from app.db import init_db; init_db()"

# Seed test data
docker-compose exec db psql -U luna -d luna -f /app/seed_data.sql
```

If the seed file isn't found:

```bash
docker cp backend/seed_data.sql luna_db:/seed_data.sql
docker-compose exec db psql -U luna -d luna -f /seed_data.sql
```

## Step 3: Open in Browser

Visit: **http://localhost:5000**

You should see the user selection screen!

## Usage

1. **Select a test user** (Alice, Bob, Charlie, etc.)
2. **Browse venues** in the Discover tab
3. **Tap a venue** to see details and recommended friends
4. **Confirm interest** to signal you want to go
5. **Check My Plans** to see reservations
6. **View Profile** to see your friends and interests
7. **Switch users** to test different perspectives

## Testing on Mobile Device

To test on your phone (on same WiFi network):

1. Find your computer's local IP:
   ```bash
   # macOS/Linux
   ifconfig | grep "inet "

   # Windows
   ipconfig
   ```

2. Visit from phone: `http://YOUR_IP:5000`

Example: `http://192.168.1.100:5000`

## Stopping Services

```bash
# Stop all containers
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## Troubleshooting

### Port already in use

```bash
# Change ports in docker-compose.yml
# Example: "5001:5000" instead of "5000:5000"
```

### Web can't connect to API

```bash
# Check API is running
curl http://localhost:8000/health

# Should return: {"status":"healthy"}
```

### No users showing up

```bash
# Verify database seeding
docker-compose exec db psql -U luna -d luna -c "SELECT * FROM users;"
```

### Blank screen / styling issues

- Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
- Check browser console for errors (F12 → Console tab)

## Comparing with iOS App

Both frontends use the same backend API and show identical data:

| Feature | Web Frontend | iOS App |
|---------|--------------|---------|
| Access | http://localhost:5000 | Xcode Simulator |
| Platform | Any browser | iOS only |
| Design | iOS-inspired CSS | Native SwiftUI |
| Features | 100% parity | 100% parity |

## Next Steps

- Explore the code in `frontend_web/`
- Check API docs at http://localhost:8000/docs
- Read the backend analysis in the main README
- Try different user accounts to see personalization

## Support

If you encounter issues:

1. Check Docker logs: `docker-compose logs web`
2. Verify all containers running: `docker-compose ps`
3. Check the detailed README in `frontend_web/README.md`

Enjoy exploring Luna! 🌟

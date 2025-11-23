# iOS App Build Instructions

## Prerequisites
- macOS with Xcode 15 or later
- iOS 16.0+ SDK

## Quick Start

1. **Open the project:**
   ```bash
   cd frontend
   open LunaTakeHome.xcodeproj
   ```

2. **Select a simulator:**
   - Click the device selector in Xcode toolbar
   - Choose any iPhone simulator (e.g., iPhone 15 Pro)

3. **Build and run:**
   - Press `Cmd+R` or click the Play button
   - Wait for build to complete

## Configuration

### API Endpoint
Before building, verify the API endpoint in `LunaTakeHome/Config.swift`:

```swift
static let apiBaseURL = "http://127.0.0.1:8000"
```

- **For iOS Simulator:** Use `http://127.0.0.1:8000` or `http://localhost:8000`
- **For Physical Device:** Use your Mac's local IP (e.g., `http://192.168.1.XXX:8000`)

To find your Mac's IP:
```bash
ipconfig getifaddr en0
```

## Build from Command Line (Optional)

If you want to build from terminal:

```bash
cd frontend

# Clean build folder
xcodebuild clean -project LunaTakeHome.xcodeproj -scheme LunaTakeHome

# Build for simulator
xcodebuild build -project LunaTakeHome.xcodeproj \
  -scheme LunaTakeHome \
  -destination 'platform=iOS Simulator,name=iPhone 15 Pro,OS=latest'

# Or run in simulator
xcodebuild test -project LunaTakeHome.xcodeproj \
  -scheme LunaTakeHome \
  -destination 'platform=iOS Simulator,name=iPhone 15 Pro,OS=latest'
```

## Troubleshooting

### Build Errors

**"No such module 'SwiftUI'"**
- Make sure you're targeting iOS 16.0+
- Check deployment target in project settings

**Cannot connect to API**
- Ensure backend is running: `docker-compose up`
- Verify API URL in `Config.swift`
- Check firewall settings

**Signing errors**
- For local development, automatic signing is fine
- You may need to select your development team in project settings

### Runtime Errors

**"No users available"**
- Backend is not running
- Database is not seeded
- API endpoint is incorrect

Run these backend commands:
```bash
# Start backend
docker-compose up

# Initialize database
docker-compose exec api python -c "from app.db import init_db; init_db()"

# Seed data
docker cp backend/seed_data.sql luna_db:/seed_data.sql
docker-compose exec db psql -U luna -d luna -f /seed_data.sql
```

## Project Structure

```
frontend/
├── LunaTakeHome.xcodeproj/       # Xcode project
└── LunaTakeHome/                 # Source code
    ├── LunaTakeHomeApp.swift     # App entry point
    ├── Config.swift              # API configuration
    ├── Models/                   # Data models
    │   ├── User.swift
    │   ├── Venue.swift
    │   ├── Interest.swift
    │   ├── Recommendation.swift
    │   └── Reservation.swift
    ├── Networking/               # API client
    │   └── APIClient.swift
    ├── ViewModels/               # MVVM ViewModels
    │   ├── SessionViewModel.swift
    │   ├── RecommendationsViewModel.swift
    │   ├── VenueDetailViewModel.swift
    │   ├── ReservationsViewModel.swift
    │   └── UserSelectionViewModel.swift
    └── Views/                    # SwiftUI Views
        ├── RootView.swift
        ├── UserSelectionView.swift
        ├── MainTabView.swift
        ├── RecommendationsView.swift
        ├── VenueDetailView.swift
        ├── MyReservationsView.swift
        └── ProfileView.swift
```

## Expected Build Behavior

1. **First Build:** May take 1-2 minutes
2. **Warnings:** Should be minimal or none
3. **Target:** iOS 16.0+
4. **Architectures:** ARM64 (for device), x86_64/ARM64 (for simulator)

## Testing the App

1. **Launch app** - Should show user selection screen
2. **Select a user** - Choose from seeded users (Alice, Bob, Charlie, etc.)
3. **Browse recommendations** - See personalized venue suggestions
4. **View venue details** - Tap a venue card
5. **Confirm interest** - Tap "Confirm Going" button
6. **View reservations** - Go to "My Plans" tab
7. **Switch users** - Use Profile tab to test different perspectives

## Performance

- **Cold start:** < 2 seconds
- **API calls:** < 500ms (local backend)
- **UI responsiveness:** 60fps animations

## Next Steps

After successful build:
1. Test all user flows
2. Verify recommendations change per user
3. Test error states (stop backend)
4. Test pull-to-refresh
5. Test on physical device (optional)

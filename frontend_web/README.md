# Luna Web Frontend

A Flask-based mobile-responsive web frontend that mirrors the iOS SwiftUI app functionality.

## Features

- **iOS-inspired design** - Uses iOS design patterns and Apple's San Francisco font
- **Mobile-first** - Optimized for mobile devices with responsive layout (max-width 428px)
- **Full feature parity** with iOS app:
  - User selection/switching
  - Venue discovery with recommendations
  - Venue details with recommended people
  - My Plans (reservations)
  - User profile with friends and interests
  - Interest confirmation
  - Reservation acceptance

## Technology Stack

- **Flask 3.0** - Lightweight Python web framework
- **Jinja2** - Template engine
- **Vanilla CSS** - iOS-inspired styling (no frameworks)
- **Vanilla JavaScript** - Minimal client-side logic

## Project Structure

```
frontend_web/
├── app.py                  # Flask application and routes
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container definition
├── templates/             # Jinja2 HTML templates
│   ├── base.html         # Base layout with nav
│   ├── index.html        # User selection
│   ├── discover.html     # Venue recommendations
│   ├── venue_detail.html # Venue detail page
│   ├── plans.html        # My Plans/Reservations
│   └── profile.html      # User profile
└── static/               # Static assets
    ├── css/
    │   └── style.css     # iOS-inspired styles
    └── js/
        └── main.js       # Client-side JavaScript
```

## Running Locally

### With Docker Compose (Recommended)

From the project root:

```bash
docker-compose up web
```

The web frontend will be available at: http://localhost:5000

### Without Docker

```bash
cd frontend_web
pip install -r requirements.txt

# Set API endpoint (defaults to http://api:8000)
export API_BASE_URL=http://localhost:8000

python app.py
```

Visit: http://localhost:5000

## Usage Flow

1. **Select a User** - Choose from available test users
2. **Discover Tab** - Browse personalized venue recommendations
3. **Tap a Venue** - View details and recommended friends
4. **Confirm Going** - Signal your interest in a venue
5. **My Plans Tab** - View your reservations
6. **Accept Invitations** - Confirm attendance at pending reservations
7. **Profile Tab** - View your friends, interests, and stats

## Design Decisions

### Why Flask?

- Lightweight and fast to implement
- Python matches the backend (FastAPI)
- Simple templating with Jinja2
- No complex build process
- Easy to deploy alongside backend

### iOS-Inspired Design

The CSS mimics iOS design patterns:

- **Typography**: -apple-system font stack (San Francisco)
- **Colors**: iOS system colors (primary blue #007AFF)
- **Spacing**: iOS standard spacing units
- **Cards**: Rounded corners (12-16px radius)
- **Shadows**: Subtle drop shadows
- **Navigation**: Bottom tab bar with icons
- **Interactions**: Active states with scale transforms

### Mobile-First Approach

- Max-width: 428px (iPhone 14 Pro Max)
- Touch-friendly tap targets (44px minimum)
- Pull-to-refresh gesture
- Viewport meta tags for proper scaling
- Safe area insets for notched devices

## API Integration

The Flask app communicates with the FastAPI backend via HTTP requests:

```python
API_BASE_URL = os.getenv('API_BASE_URL', 'http://api:8000')

# Example API call
def api_get(endpoint):
    response = requests.get(f"{API_BASE_URL}{endpoint}")
    return response.json()
```

**Endpoints Used:**
- `GET /users` - List users
- `GET /users/{id}` - User details
- `GET /recommendations/{id}` - Personalized recommendations
- `POST /users/{id}/interests` - Confirm interest
- `GET /reservations/{id}` - User's reservations
- `POST /reservations/accept` - Accept invitation

## Session Management

Uses Flask sessions to track the currently selected user:

```python
session['user_id'] = user_id
session['user_name'] = user['name']
```

No authentication is implemented (matches the iOS prototype).

## Comparison with iOS App

| Feature | iOS (SwiftUI) | Web (Flask) | Status |
|---------|---------------|-------------|--------|
| User Selection | ✅ | ✅ | Identical |
| Venue Discovery | ✅ | ✅ | Identical |
| Venue Details | ✅ | ✅ | Identical |
| Confirm Interest | ✅ | ✅ | Identical |
| My Plans | ✅ | ✅ | Identical |
| Accept Reservations | ✅ | ✅ | Identical |
| Profile View | ✅ | ✅ | Identical |
| Friends List | ✅ | ✅ | Identical |
| Location Services | ✅ | ❌ | Not implemented |
| Push Notifications | ❌ | ❌ | Neither implemented |

## Future Enhancements

- [ ] Add location services (browser geolocation API)
- [ ] Implement PWA (Progressive Web App) support
- [ ] Add service worker for offline functionality
- [ ] WebSocket integration for real-time updates
- [ ] Dark mode toggle
- [ ] Animation improvements
- [ ] Loading skeletons
- [ ] Optimistic UI updates

## Testing

### Manual Testing Checklist

- [ ] Select different users and verify personalized recommendations
- [ ] Confirm interest in venues and check toast notifications
- [ ] View venue details and see recommended people
- [ ] Accept reservation invitations
- [ ] Navigate between tabs
- [ ] Test on different screen sizes
- [ ] Test on actual mobile device (not just simulator)

### Browser Compatibility

Tested on:
- ✅ Safari (iOS)
- ✅ Chrome (iOS/Android)
- ✅ Firefox (Desktop)

## Troubleshooting

### Web frontend can't connect to API

```bash
# Check if API is running
curl http://localhost:8000/health

# Check Docker network
docker network inspect luna_takehome_technical_interview_default
```

### Styling looks wrong on mobile

- Clear browser cache
- Check viewport meta tag is present
- Verify CSS file is loading (check Network tab)

### Session data lost

- Check that `app.secret_key` is set
- Verify cookies are enabled in browser

## License

Part of Luna Take Home Technical Interview submission.

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'luna-dev-secret-key-change-in-production'

# Backend API configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://api:8000')

# Helper function to make API calls
def api_get(endpoint):
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return None

def api_post(endpoint, data):
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return None


@app.route('/')
def index():
    """Landing page - user selection"""
    if 'user_id' in session:
        return redirect(url_for('discover'))

    users = api_get('/users')
    if not users:
        users = []

    return render_template('index.html', users=users)


@app.route('/select_user/<int:user_id>')
def select_user(user_id):
    """Select a user to view as"""
    user = api_get(f'/users/{user_id}')
    if user:
        session['user_id'] = user_id
        session['user_name'] = user['name']
        session['user_avatar'] = user.get('avatar_url', '')
    return redirect(url_for('discover'))


@app.route('/logout')
def logout():
    """Clear session and return to user selection"""
    session.clear()
    return redirect(url_for('index'))


@app.route('/discover')
def discover():
    """Main discovery page - venue recommendations"""
    if 'user_id' not in session:
        return redirect(url_for('index'))

    user_id = session['user_id']

    # Get recommendations (you can add lat/lon from request if needed)
    recommendations = api_get(f'/recommendations/{user_id}')

    if not recommendations:
        recommendations = {'recommended_venues': []}

    return render_template('discover.html',
                         recommendations=recommendations['recommended_venues'],
                         current_page='discover')


@app.route('/venue/<int:venue_id>')
def venue_detail(venue_id):
    """Venue detail page with recommended people"""
    if 'user_id' not in session:
        return redirect(url_for('index'))

    user_id = session['user_id']

    # Get recommendations to find this venue
    recommendations = api_get(f'/recommendations/{user_id}')

    venue_data = None
    if recommendations:
        for rec in recommendations['recommended_venues']:
            if rec['venue']['id'] == venue_id:
                venue_data = rec
                break

    if not venue_data:
        return "Venue not found", 404

    return render_template('venue_detail.html',
                         venue_data=venue_data,
                         current_page='discover')


@app.route('/confirm_interest/<int:venue_id>', methods=['POST'])
def confirm_interest(venue_id):
    """Confirm interest in a venue"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    user_id = session['user_id']

    # Create/update interest
    result = api_post(f'/users/{user_id}/interests', {
        'venue_id': venue_id,
        'status': 'CONFIRMED'
    })

    if result:
        return jsonify({'success': True, 'message': 'Interest confirmed!'})
    else:
        return jsonify({'success': False, 'message': 'Failed to confirm interest'}), 500


@app.route('/plans')
def my_plans():
    """My Plans page - user's reservations"""
    if 'user_id' not in session:
        return redirect(url_for('index'))

    user_id = session['user_id']

    # Get user's reservations
    reservations = api_get(f'/reservations/{user_id}')

    if not reservations:
        reservations = []

    return render_template('plans.html',
                         reservations=reservations,
                         current_page='plans')


@app.route('/accept_reservation/<int:reservation_id>', methods=['POST'])
def accept_reservation(reservation_id):
    """Accept a reservation invitation"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    user_id = session['user_id']

    result = api_post('/reservations/accept', {
        'reservation_id': reservation_id,
        'user_id': user_id
    })

    if result:
        return jsonify({'success': True, 'message': result.get('message', 'Reservation accepted!')})
    else:
        return jsonify({'success': False, 'message': 'Failed to accept reservation'}), 500


@app.route('/cancel_reservation/<int:reservation_id>', methods=['POST'])
def cancel_reservation(reservation_id):
    """Cancel/delete a reservation"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        response = requests.delete(f"{API_BASE_URL}/reservations/{reservation_id}", timeout=5)
        response.raise_for_status()
        result = response.json()
        return jsonify({'success': True, 'message': result.get('message', 'Reservation cancelled!')})
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return jsonify({'success': False, 'message': 'Failed to cancel reservation'}), 500


@app.route('/profile')
def profile():
    """Profile page"""
    if 'user_id' not in session:
        return redirect(url_for('index'))

    user_id = session['user_id']

    # Get user details
    user = api_get(f'/users/{user_id}')

    # Get user's friends
    friends = api_get(f'/users/{user_id}/friends')

    # Get user's interests
    interests = api_get(f'/users/{user_id}/interests')

    return render_template('profile.html',
                         user=user,
                         friends=friends if friends else [],
                         interests=interests if interests else [],
                         current_page='profile')


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'luna-web-frontend'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

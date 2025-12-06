"""Test script to verify session is working."""
from app import create_app
from flask import session

app = create_app()

@app.route('/test-session')
def test_session():
    """Test if session is working."""
    user_id = session.get('user_id')
    username = session.get('username')
    role = session.get('role')
    return f"Session test: user_id={user_id}, username={username}, role={role}, permanent={session.permanent}"

if __name__ == '__main__':
    app.run(debug=True, port=5000)





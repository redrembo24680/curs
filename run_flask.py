#!/usr/bin/env python
"""Start Flask server."""
import subprocess
import sys
import os

os.chdir(r'd:\Roman\ПАЛІТЄХ\2 курс\Курсова Роман\web_flask')
sys.path.insert(0, r'd:\Roman\ПАЛІТЄХ\2 курс\Курсова Роман\web_flask')

# Start Flask
from start import app

if __name__ == '__main__':
    print("=" * 60)
    print("Starting Flask server...")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=False)

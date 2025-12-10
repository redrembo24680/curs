import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
ENV = os.environ.copy()
ENV.setdefault("FLASK_APP", "app.py")
ENV.setdefault("FLASK_ENV", "development")
ENV.setdefault("API_BASE_URL", "http://localhost:8080/api")
ENV.setdefault("PYTHONPATH", ROOT)

if __name__ == "__main__":
    requirements = os.path.join(ROOT, "requirements.txt")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements], check=True)
    subprocess.run([sys.executable, "-m", "flask", "run", "--host", "0.0.0.0", "--port", "5000"], check=True, cwd=ROOT, env=ENV)


















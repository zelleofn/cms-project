import os
from app import create_app
from flask_cors import CORS


env = os.getenv('FLASK_ENV', 'development')
app = create_app(env)


allowed_origins = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:4200').split(',')

CORS(app, resources={r"/*": {"origins": allowed_origins}}, supports_credentials=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
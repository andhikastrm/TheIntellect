from flask import Flask
from flask_cors import CORS
from extensions import db

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kelompok2f2.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inisialisasi database
    db.init_app(app)

    # Import model & route setelah db terhubung
    with app.app_context():
        import models
        import routes
        db.create_all()

    return app


# Jalankan langsung
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

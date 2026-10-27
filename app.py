"""Ponto de entrada: só configura o Flask e registra os serviços."""
import os
from flask import Flask
from database.models import db
from services import ativo_services, setor_services, lembrete_services, ping_services

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def create_app(config=None):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'database', 'ativos.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-only-troque-em-producao')
    app.config.update(config or {})

    db.init_app(app)

    for servico in (ativo_services, setor_services, lembrete_services, ping_services):
        servico.registrar(app)

    with app.app_context():
        db.create_all()
    return app


app = create_app()

if __name__ == '__main__':
    app.run(
        debug=os.environ.get('FLASK_DEBUG') == '0',
        host=os.environ.get('HOST', '127.0.0.1'),
    )
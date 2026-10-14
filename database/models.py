from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

# Define o fuso horário de São Paulo
fuso_sp = ZoneInfo("America/Fortaleza")
db = SQLAlchemy()


class Ativo(db.Model):
    __tablename__ = 'ativos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # PC, Projetor, Monitor, Catraca, Servidor, Switch, Roteador, Ap
    patrimonio = db.Column(db.String(50))
    localizacao = db.Column(db.String(150))
    status = db.Column(db.String(30), default='Ativo')
    observacoes = db.Column(db.Text, default='')
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(fuso_sp))

    configuracoes = db.relationship(
        'Configuracao',
        backref='ativo', 
        lazy=True, 
        cascade='all, delete-orphan'
    )


class Configuracao(db.Model):
    __tablename__ = 'configuracoes'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    nota = db.Column(db.Text, default='')
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(fuso_sp))
    ativo_id = db.Column(db.Integer, db.ForeignKey('ativos.id'), nullable=False)


class Lembrete(db.Model):
    __tablename__ = 'lembretes'

    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(fuso_sp))


class PingHost(db.Model):
    __tablename__ = 'ping_hosts'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    ip = db.Column(db.String(45), nullable=False)

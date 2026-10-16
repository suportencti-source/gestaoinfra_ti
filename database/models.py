from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from zoneinfo import ZoneInfo

fuso_local = ZoneInfo("America/Fortaleza")
db = SQLAlchemy()


def agora():
    return datetime.now(fuso_local)


class Setor(db.Model):
    __tablename__ = 'setores'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    criado_em = db.Column(db.DateTime, default=agora)

    # Sem cascade: um setor com ativos não pode ser apagado (checado no service)
    ativos = db.relationship('Ativo', backref='setor', lazy=True)


class Ativo(db.Model):
    __tablename__ = 'ativos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    patrimonio = db.Column(db.String(50))
    localizacao = db.Column(db.String(150))
    status = db.Column(db.String(30), default='Ativo')
    observacoes = db.Column(db.Text, default='')
    criado_em = db.Column(db.DateTime, default=agora)
    # nullable no banco para não quebrar ativos antigos; obrigatório no formulário
    setor_id = db.Column(db.Integer, db.ForeignKey('setores.id'), index=True)

    configuracoes = db.relationship(
        'Configuracao', backref='ativo', lazy=True, cascade='all, delete-orphan'
    )


class Configuracao(db.Model):
    __tablename__ = 'configuracoes'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    nota = db.Column(db.Text, default='')
    criado_em = db.Column(db.DateTime, default=agora)
    ativo_id = db.Column(db.Integer, db.ForeignKey('ativos.id'), nullable=False)


class Lembrete(db.Model):
    __tablename__ = 'lembretes'

    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    criado_em = db.Column(db.DateTime, default=agora)


class PingHost(db.Model):
    __tablename__ = 'ping_hosts'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    ip = db.Column(db.String(45), nullable=False)

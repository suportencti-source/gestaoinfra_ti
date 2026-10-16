"""Rotas e regras de negócio de Setores."""
from flask import render_template, request, redirect, url_for
from sqlalchemy import func
from database.models import db, Setor, Ativo


def _render(erro=None, nome=''):
    # Uma única query com COUNT agrupado (evita N+1 ao contar ativos por setor)
    setores = (
        db.session.query(Setor, func.count(Ativo.id))
        .outerjoin(Ativo, Ativo.setor_id == Setor.id)
        .group_by(Setor.id)
        .order_by(Setor.nome)
        .all()
    )
    return render_template('setores.html', setores=setores, erro=erro, nome=nome)


def setores():
    """Lista e cria setores."""
    if request.method == 'POST':
        nome = (request.form.get('nome') or '').strip()
        if not nome:
            return _render('Informe o nome do setor.', nome)
        if len(nome) > 100:
            return _render('O nome pode ter no máximo 100 caracteres.', nome)
        if Setor.query.filter(func.lower(Setor.nome) == nome.lower()).first():
            return _render('Este setor já está cadastrado.', nome)
        db.session.add(Setor(nome=nome))
        db.session.commit()
        return redirect(url_for('setores'))
    return _render()


def excluir_setor(setor_id):
    setor = db.get_or_404(Setor, setor_id)
    if setor.ativos:
        return _render('Não é possível excluir um setor que possui ativos vinculados.')
    db.session.delete(setor)
    db.session.commit()
    return redirect(url_for('setores'))


def registrar(app):
    app.add_url_rule('/setores', 'setores', setores, methods=['GET', 'POST'])
    app.add_url_rule('/setores/<int:setor_id>/excluir', 'excluir_setor', excluir_setor, methods=['POST'])

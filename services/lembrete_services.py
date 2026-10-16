"""Rotas de Lembretes e Chamados (placeholder)."""
from flask import render_template, request, redirect, url_for
from database.models import db, Lembrete


def lembretes():
    if request.method == 'POST':
        texto = (request.form.get('texto') or '').strip()
        if texto:
            db.session.add(Lembrete(texto=texto))
            db.session.commit()
        return redirect(url_for('lembretes'))
    lista = Lembrete.query.order_by(Lembrete.criado_em.desc()).all()
    return render_template('lembretes.html', lembretes=lista)


def excluir_lembrete(lembrete_id):
    lembrete = db.get_or_404(Lembrete, lembrete_id)
    db.session.delete(lembrete)
    db.session.commit()
    return redirect(url_for('lembretes'))


def chamados():
    return render_template('chamados.html')


def registrar(app):
    app.add_url_rule('/lembretes', 'lembretes', lembretes, methods=['GET', 'POST'])
    app.add_url_rule('/lembretes/<int:lembrete_id>/excluir', 'excluir_lembrete', excluir_lembrete, methods=['POST'])
    app.add_url_rule('/chamados', 'chamados', chamados, methods=['GET', 'POST'])

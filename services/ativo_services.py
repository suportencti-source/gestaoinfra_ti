"""Rotas e regras de negócio de Ativos, Observações e Configurações."""
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload
from database.models import db, Ativo, Configuracao, Setor
from services.constantes import TIPOS_ATIVO, STATUS_ATIVO

POR_PAGINA = 20


def _like(termo):
    """Escapa %, _ e \\ para o ilike tratar o texto literalmente."""
    esc = termo.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
    return f'%{esc}%'


def _limpar(valor):
    """Remove espaços e converte string vazia em None."""
    return (valor or '').strip() or None


def _validar(form):
    """Valida o formulário de ativo. Retorna (dados, erro)."""
    nome = (form.get('nome') or '').strip()
    tipo = form.get('tipo', '')
    status = form.get('status') or 'Ativo'
    setor_id = form.get('setor_id', type=int)

    if not nome:
        return None, 'Informe o nome do equipamento.'
    if tipo not in TIPOS_ATIVO:
        return None, 'Selecione um tipo válido.'
    if status not in STATUS_ATIVO:
        return None, 'Status inválido.'
    if setor_id is None or db.session.get(Setor, setor_id) is None:
        return None, 'Selecione o setor do ativo.'

    return {
        'nome': nome,
        'tipo': tipo,
        'status': status,
        'setor_id': setor_id,
        'patrimonio': _limpar(form.get('patrimonio')),
        'localizacao': _limpar(form.get('localizacao')),
    }, None


def _render_form(ativo, dados, erro=None):
    setores = Setor.query.order_by(Setor.nome).all()
    return render_template(
        'form_ativo.html', ativo=ativo, dados=dados, erro=erro,
        tipos=TIPOS_ATIVO, status_opcoes=STATUS_ATIVO, setores=setores,
    )


# ---------- CRUD de ativos ----------
def index():
    tipo = request.args.get('tipo')
    if tipo not in TIPOS_ATIVO:
        tipo = None
    setor_id = request.args.get('setor_id', type=int)
    q = (request.args.get('q') or '').strip()
    page = request.args.get('page', 1, type=int)

    # joinedload carrega o setor no mesmo SELECT (evita N+1 na listagem)
    query = Ativo.query.options(joinedload(Ativo.setor))
    if tipo:
        query = query.filter(Ativo.tipo == tipo)
    if setor_id:
        query = query.filter(Ativo.setor_id == setor_id)
    if q:
        termo = _like(q)
        query = query.filter(or_(
            Ativo.nome.ilike(termo, escape='\\'),
            Ativo.patrimonio.ilike(termo, escape='\\'),
            Ativo.localizacao.ilike(termo, escape='\\'),
        ))

    paginacao = query.order_by(Ativo.nome).paginate(page=page, per_page=POR_PAGINA, error_out=False)
    # Cards de estatística refletem o inventário todo, não só a página atual
    por_status = dict(db.session.query(Ativo.status, func.count(Ativo.id)).group_by(Ativo.status).all())

    return render_template(
        'index.html',
        ativos=paginacao.items, paginacao=paginacao, q=q,
        total_geral=sum(por_status.values()),
        total_ativos=por_status.get('Ativo', 0),
        total_manutencao=por_status.get('Em manutenção', 0),
        tipos=TIPOS_ATIVO, tipo_filtro=tipo,
        setores=Setor.query.order_by(Setor.nome).all(), setor_filtro=setor_id,
    )


def novo_ativo():
    if request.method == 'POST':
        dados, erro = _validar(request.form)
        if not erro:
            ativo = Ativo(**dados)
            db.session.add(ativo)
            db.session.commit()
            flash('Ativo salvo.', 'success')
            return redirect(url_for('detalhe_ativo', ativo_id=ativo.id))
        return _render_form(None, request.form, erro)
    return _render_form(None, {})


def detalhe_ativo(ativo_id):
    ativo = db.get_or_404(Ativo, ativo_id)
    return render_template('detalhe_ativo.html', ativo=ativo)


def editar_ativo(ativo_id):
    ativo = db.get_or_404(Ativo, ativo_id)
    if request.method == 'POST':
        dados, erro = _validar(request.form)
        if not erro:
            for campo, valor in dados.items():
                setattr(ativo, campo, valor)
            db.session.commit()
            flash('Ativo salvo.', 'success')
            return redirect(url_for('detalhe_ativo', ativo_id=ativo.id))
        return _render_form(ativo, request.form, erro)
    atual = {c: getattr(ativo, c) for c in ('nome', 'tipo', 'status', 'setor_id', 'patrimonio', 'localizacao')}
    return _render_form(ativo, atual)


def excluir_ativo(ativo_id):
    ativo = db.get_or_404(Ativo, ativo_id)
    db.session.delete(ativo)
    db.session.commit()
    flash('Ativo excluído.', 'success')
    return redirect(url_for('index'))


# ---------- Observações ----------
def salvar_observacao(ativo_id):
    ativo = db.get_or_404(Ativo, ativo_id)
    ativo.observacoes = request.form.get('observacoes', '')
    db.session.commit()
    flash('Observação atualizada.', 'success')
    return redirect(url_for('detalhe_ativo', ativo_id=ativo.id))


# ---------- Configurações ----------
def nova_configuracao(ativo_id):
    ativo = db.get_or_404(Ativo, ativo_id)
    nome = (request.form.get('nome_config') or '').strip()
    if nome:
        db.session.add(Configuracao(
            nome=nome, nota=request.form.get('nota_config', ''), ativo_id=ativo.id
        ))
        db.session.commit()
        flash('Configuração adicionada.', 'success')
    return redirect(url_for('detalhe_ativo', ativo_id=ativo.id))


def excluir_configuracao(config_id):
    config = db.get_or_404(Configuracao, config_id)
    ativo_id = config.ativo_id
    db.session.delete(config)
    db.session.commit()
    flash('Configuração removida.', 'success')
    return redirect(url_for('detalhe_ativo', ativo_id=ativo_id))


def registrar(app):
    r = app.add_url_rule
    r('/', 'index', index)
    r('/ativo/novo', 'novo_ativo', novo_ativo, methods=['GET', 'POST'])
    r('/ativo/<int:ativo_id>', 'detalhe_ativo', detalhe_ativo)
    r('/ativo/<int:ativo_id>/editar', 'editar_ativo', editar_ativo, methods=['GET', 'POST'])
    r('/ativo/<int:ativo_id>/excluir', 'excluir_ativo', excluir_ativo, methods=['POST'])
    r('/ativo/<int:ativo_id>/observacao', 'salvar_observacao', salvar_observacao, methods=['POST'])
    r('/ativo/<int:ativo_id>/configuracao/nova', 'nova_configuracao', nova_configuracao, methods=['POST'])
    r('/configuracao/<int:config_id>/excluir', 'excluir_configuracao', excluir_configuracao, methods=['POST'])
from flask import Flask, render_template, request, redirect, url_for, jsonify
from database.models import db, Ativo, Configuracao, Lembrete, PingHost
import os
import subprocess
import platform
import ipaddress

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'database', 'ativos.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

TIPOS_ATIVO = ["PC", "Projetor", "Monitor", "Catraca", "Servidor", "Switch", "Roteador", "Ap", "Chamados"]


@app.route('/')
def index():
    tipo_filtro = request.args.get('tipo')
    query = Ativo.query
    if tipo_filtro:
        query = query.filter_by(tipo=tipo_filtro)
    ativos = query.order_by(Ativo.nome).all()
    return render_template('index.html', ativos=ativos, tipos=TIPOS_ATIVO, tipo_filtro=tipo_filtro)


@app.route('/ativo/novo', methods=['GET', 'POST'])
def novo_ativo():
    if request.method == 'POST':
        ativo = Ativo(
            nome=request.form['nome'],
            tipo=request.form['tipo'],
            patrimonio=request.form.get('patrimonio'),
            localizacao=request.form.get('localizacao'),
            status=request.form.get('status', 'Ativo')
        )
        db.session.add(ativo)
        db.session.commit()
        return redirect(url_for('detalhe_ativo', ativo_id=ativo.id))
    return render_template('form_ativo.html', tipos=TIPOS_ATIVO, ativo=None)


@app.route('/ativo/<int:ativo_id>')
def detalhe_ativo(ativo_id):
    ativo = db.get_or_404(Ativo, ativo_id)
    return render_template('detalhe_ativo.html', ativo=ativo)


@app.route('/ativo/<int:ativo_id>/editar', methods=['GET', 'POST'])
def editar_ativo(ativo_id):
    ativo = db.get_or_404(Ativo, ativo_id)
    if request.method == 'POST':
        ativo.nome = request.form['nome']
        ativo.tipo = request.form['tipo']
        ativo.patrimonio = request.form.get('patrimonio')
        ativo.localizacao = request.form.get('localizacao')
        ativo.status = request.form.get('status', 'Ativo')
        db.session.commit()
        return redirect(url_for('detalhe_ativo', ativo_id=ativo.id))
    return render_template('form_ativo.html', tipos=TIPOS_ATIVO, ativo=ativo)


@app.route('/ativo/<int:ativo_id>/excluir', methods=['POST'])
def excluir_ativo(ativo_id):
    ativo = db.get_or_404(Ativo, ativo_id)
    db.session.delete(ativo)
    db.session.commit()
    return redirect(url_for('index'))


# ---- Observações (campo simples de texto no ativo) ----
@app.route('/ativo/<int:ativo_id>/observacao', methods=['POST'])
def salvar_observacao(ativo_id):
    ativo = db.get_or_404(Ativo, ativo_id)
    ativo.observacoes = request.form.get('observacoes', '')
    db.session.commit()
    return redirect(url_for('detalhe_ativo', ativo_id=ativo.id))


# ---- Configurações (nome + nota, várias por ativo) ----
@app.route('/ativo/<int:ativo_id>/configuracao/nova', methods=['POST'])
def nova_configuracao(ativo_id):
    ativo = db.get_or_404(Ativo, ativo_id)
    config = Configuracao(
        nome=request.form['nome_config'],
        nota=request.form.get('nota_config', ''),
        ativo_id=ativo.id
    )
    db.session.add(config)
    db.session.commit()
    return redirect(url_for('detalhe_ativo', ativo_id=ativo.id))


@app.route('/configuracao/<int:config_id>/excluir', methods=['POST'])
def excluir_configuracao(config_id):
    config = db.get_or_404(Configuracao, config_id)
    ativo_id = config.ativo_id
    db.session.delete(config)
    db.session.commit()
    return redirect(url_for('detalhe_ativo', ativo_id=ativo_id))


# ---- Lembretes (aba geral, não vinculada a um ativo especifico) ----
@app.route('/lembretes', methods=['GET', 'POST'])
def lembretes():
    if request.method == 'POST':
        lembrete = Lembrete(texto=request.form['texto'])
        db.session.add(lembrete)
        db.session.commit()
        return redirect(url_for('lembretes'))
    lista = Lembrete.query.order_by(Lembrete.criado_em.desc()).all()
    return render_template('lembretes.html', lembretes=lista)


@app.route('/lembretes/<int:lembrete_id>/excluir', methods=['POST'])
def excluir_lembrete(lembrete_id):
    lembrete = db.get_or_404(Lembrete, lembrete_id)
    db.session.delete(lembrete)
    db.session.commit()
    return redirect(url_for('lembretes'))

@app.route('/chamados', methods=['GET', 'POST'])
def chamados():
    return render_template('chamados.html')


# ---- Ping (monitoramento simples de computadores) ----
def executar_ping(ip):
    windows = platform.system().lower() == 'windows'
    
    #cria somente o comando ping
    if windows:
        cmd = ['ping', '-n', '1', '-w', '1000', ip]
    else:
        cmd = ['ping', '-c', '1', '-W', '1', ip]

    #executa o ping conforme o s.o
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, errors='ignore', timeout=5)

    except (subprocess.TimeoutExpired, OSError):
        return False
    
    if r.returncode != 0:
        return False
    
    if windows:
        return 'TTL=' in r.stdout.upper()
    return True


servers = ['10.1.100.3','10.1.100.52']
ts = executar_ping(servers[0])
@app.route('/ping', methods=['GET', 'POST'])

def ping():

    erro = None
    nome = ip = ''

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        ip = request.form.get('ip', '').strip()
    
        try:
            endereco = ipaddress.ip_address(ip)
            if endereco.is_unspecified or endereco.is_multicast:
                raise ValueError
            ip = str(endereco)
        except ValueError:
            erro = 'IP invalido. Exemplo: 192.168.0.10'
        if not erro and not nome:
            erro = 'Informe o nome do computador.'
        if not erro and PingHost.query.filter_by(ip=ip).first():
            erro = 'Este IP ja esta cadastrado.'
        if not erro:
            db.session.add(PingHost(nome=nome, ip=ip))
            db.session.commit()
            return redirect(url_for('ping'))

    hosts = PingHost.query.order_by(PingHost.nome).all()
    
    return render_template('ping.html', hosts=hosts, erro=erro, nome=nome, ip=ip, server=ts)


@app.route('/ping/<int:host_id>/remover', methods=['POST'])
def remover_ping(host_id):
    host = db.get_or_404(PingHost, host_id)
    db.session.delete(host)
    db.session.commit()
    return redirect(url_for('ping'))


@app.route('/ping/<int:host_id>/verificar', methods=['POST'])
def verificar_ping(host_id):
    host = db.get_or_404(PingHost, host_id)
    return jsonify({'id': host.id, 'status': 'UP' if executar_ping(host.ip) else 'DOWN'})

@app.route('/ping/<int:name_srv>/verificar', methods=['POST'])
def verificar_ping_srv(name_srv):
    return executar_ping(name_srv.values())


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

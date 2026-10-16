"""Rotas e lógica de monitoramento por ping."""
import ipaddress
import platform
import subprocess

from flask import render_template, request, redirect, url_for, jsonify
from database.models import db, PingHost

# IPs fixos de servidores (whitelist: só estes podem ser pingados pela rota de servidor)
SERVIDORES = ['10.1.100.3', '10.1.100.52']


def executar_ping(ip):
    """Executa 1 ping e retorna True se o host respondeu."""
    windows = platform.system().lower() == 'windows'
    cmd = ['ping', '-n', '1', '-w', '1000', ip] if windows else ['ping', '-c', '1', '-W', '1', ip]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, errors='ignore', timeout=5)
    except (subprocess.TimeoutExpired, OSError):
        return False
    if r.returncode != 0:
        return False
    return 'TTL=' in r.stdout.upper() if windows else True


def _validar_host(nome, ip):
    """Retorna (ip_normalizado, erro)."""
    try:
        endereco = ipaddress.ip_address(ip)
        if endereco.is_unspecified or endereco.is_multicast:
            raise ValueError
        ip = str(endereco)
    except ValueError:
        return ip, 'IP inválido. Exemplo: 192.168.0.10'
    if not nome:
        return ip, 'Informe o nome do computador.'
    if PingHost.query.filter_by(ip=ip).first():
        return ip, 'Este IP já está cadastrado.'
    return ip, None


def ping():
    erro, nome, ip = None, '', ''
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        ip, erro = _validar_host(nome, request.form.get('ip', '').strip())
        if not erro:
            db.session.add(PingHost(nome=nome, ip=ip))
            db.session.commit()
            return redirect(url_for('ping'))

    hosts = PingHost.query.order_by(PingHost.nome).all()
    # O ping NÃO roda mais no carregamento da página; só sob demanda via POST
    return render_template('ping.html', hosts=hosts, erro=erro, nome=nome, ip=ip, server=SERVIDORES[0])


def remover_ping(host_id):
    host = db.get_or_404(PingHost, host_id)
    db.session.delete(host)
    db.session.commit()
    return redirect(url_for('ping'))


def verificar_ping(host_id):
    host = db.get_or_404(PingHost, host_id)
    return jsonify({'id': host.id, 'status': 'UP' if executar_ping(host.ip) else 'DOWN'})


def verificar_ping_srv(name_srv):
    if name_srv not in SERVIDORES:
        return jsonify({'erro': 'Servidor não cadastrado'}), 404
    return jsonify({'ip': name_srv, 'status': 'UP' if executar_ping(name_srv) else 'DOWN'})


def registrar(app):
    r = app.add_url_rule
    r('/ping', 'ping', ping, methods=['GET', 'POST'])
    r('/ping/<int:host_id>/remover', 'remover_ping', remover_ping, methods=['POST'])
    r('/ping/<int:host_id>/verificar', 'verificar_ping', verificar_ping, methods=['POST'])
    r('/ping/servidor/<name_srv>/verificar', 'verificar_ping_srv', verificar_ping_srv, methods=['POST'])

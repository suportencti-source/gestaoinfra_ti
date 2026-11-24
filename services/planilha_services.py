"""Rotas de visualização das abas da planilha de chamados."""
from flask import render_template, abort, flash
import gspread

from services import google_sheets


def planilhas():
    """Lista as abas disponíveis para seleção."""
    try:
        abas = google_sheets.listar_abas()
    except Exception as erro:  # erro de rede, credencial ou configuração
        flash(f'Não foi possível acessar a planilha: {erro}', 'error')
        abas = []
    return render_template('planilhas.html', abas=abas)


def planilha_aba(nome_aba):
    """Mostra o conteúdo de uma aba específica."""
    try:
        cabecalho, linhas = google_sheets.ler_aba(nome_aba)
    except gspread.WorksheetNotFound:
        abort(404)
    except Exception as erro:
        flash(f'Erro ao ler a aba: {erro}', 'error')
        cabecalho, linhas = [], []
    return render_template(
        'planilha_aba.html', nome_aba=nome_aba, cabecalho=cabecalho, linhas=linhas
    )


def registrar(app):
    app.add_url_rule('/planilhas', 'planilhas', planilhas)
    app.add_url_rule('/planilhas/<path:nome_aba>', 'planilha_aba', planilha_aba)
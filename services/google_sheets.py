
"""Conexão com o Google Sheets e leitura das abas."""
import os
from dotenv import load_dotenv

import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def _cliente():
    """Cria o cliente gspread a partir do arquivo indicado no ambiente."""
    caminho = os.environ['GOOGLE_CREDENTIALS_FILE']
    credenciais = Credentials.from_service_account_file(caminho, scopes=SCOPES)
    return gspread.authorize(credenciais)


def abrir_planilha():
    """Retorna a planilha configurada em GOOGLE_SHEET_ID."""
    return _cliente().open_by_key(os.environ['GOOGLE_SHEET_ID'])


def listar_abas():
    """Retorna os nomes de todas as abas da planilha."""
    return [aba.title for aba in abrir_planilha().worksheets()]


def ler_aba(nome_aba):
    """Retorna (cabecalho, linhas) com todas as células da aba."""
    valores = abrir_planilha().worksheet(nome_aba).get_all_values()
    if not valores:
        return [], []
    return valores[0], valores[1:]
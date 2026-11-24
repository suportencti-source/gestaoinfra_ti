import requests
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

filename = "chamados-506218-0c39934ad478.json"

scopes = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

creds = ServiceAccountCredentials.from_json_keyfile_name(filename= filename, scopes= scopes)
client = gspread.authorize(creds)

nome_planilha = 'suporte_ti-chamados'
id_pasta = "1Znx8F_Ahx-R5wdkMciVJEQverloVKODc"

planilha = filename.openbykey('1F-WdtEesxYYEsSVhlYFF6pVkK_0WoWFTBRcElDFUyvQ')


def mostrar_planilha(planilha):
    worksheet = planilha.sheet1
    dados = planilha.get_all_records()
    df = pd.DataFrame(dados)
# Imprime os dados brutos extraídos diretamente da planilha (lista de dicionários) 
    print(dados)
    print('---') 
# Imprime os dados formatados como um DataFrame (tabela organizada)
    print(df)
    print('---')

if __name__ == '__main__':
    # Ler e exibir os dados
    print('READ')
    mostrar_planilha(planilha=planilha)
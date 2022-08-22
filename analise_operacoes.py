import pandas as pd
from typing import List
from calculadora import *
from pathlib import Path
import plotly.express as px
import plotly.io as pio
pio.renderers.default = "browser"


def converte_tipo_para_int(
    df: pd.DataFrame,
    coluna_str: str,
    ) -> pd.DataFrame:

    conversao = lambda tipo_str: TipoOperacao.converte_op_para_int(
        tipo_str
    )
    return df[coluna_str].apply(conversao)


def pre_processa_df(dados_df: pd.DataFrame, lista_acoes: ListaAcoes) -> pd.DataFrame:
    # Faz a conversão de colunas do df para os objetos correspondentes da interface da calculadora

    formato_data_str = "%Y-%m-%d"

    dados_df['Data da operação'] = pd.to_datetime(
        dados_df['Data da operação'], format=formato_data_str)
    dados_df = dados_df.sort_values('Data da operação', ignore_index=True)
    dados_df['Operação'] = converte_tipo_para_int(
        dados_df, 'Operação'
    )
    retorna_acao = lambda a: lista_acoes.retorna_acao_por_nome(a)
    dados_df['Ação'] = dados_df['Ação'].apply(retorna_acao)

    return dados_df


def cria_df_de_operacoes(dados_df: pd.DataFrame) -> List[Operacao]:
    conversao = lambda e: Operacao(
        e['Data da operação'], e['Operação'], e['Ação'], e['Preço'], e['Quantidade'], e['Taxa de corretagem']
    )
    lista_operacoes = dados_df.apply(conversao, axis=1)
    return lista_operacoes


def agrupa_operacoes_por_mes(df_operacoes: pd.DataFrame) -> List[pd.DataFrame]:
    meses = df_operacoes.apply(lambda e: e.data.month).unique()
    lista_meses = []
    for mes in meses:
        mascara_bin = df_operacoes.apply(lambda e: e.data.month == mes)
        lista_meses.append(df_operacoes[mascara_bin])
    return lista_meses


def main():
    folder_saida = Path('outputs')
    if not folder_saida.exists():
        folder_saida.mkdir(exist_ok=True)

    dados_df = pd.read_csv('stocks-dataset.csv')
    lista_acoes = ListaAcoes(dados_df['Ação'])
    dados_df = pre_processa_df(dados_df, lista_acoes)
    operacoes_df = cria_df_de_operacoes(dados_df)
    lista_operacoes_por_mes = agrupa_operacoes_por_mes(operacoes_df)

    colunas_saida = [
        'Mês', 'Valor total de compra (reais)', 'Valor total de venda (reais)',
        'Rendimento absoluto bruto (reais)', 'Imposto devido (reais)', 'Rendimento absoluto líquido (reais)'
    ]
    valores_saida = []
    meses = []
    rendimento_liquido = []
    for lista_operacoes in lista_operacoes_por_mes:
        meses.append(lista_operacoes.iloc[0].data.month)
        calculadora = CalculadoraImposto(lista_acoes, meses[-1], lista_operacoes)
        imposto_no_mes = calculadora.retorna_imposto()
        ram = calculadora.retorna_ram()
        total_compras = calculadora.retorna_total_compras()
        total_vendas = calculadora.retorna_total_vendas()
        rendimento_liquido.append(ram - imposto_no_mes)
        valores_saida.append([meses[-1], total_compras, total_vendas, ram, imposto_no_mes, rendimento_liquido[-1]])

    # gerando o df de saída
    df_saida = pd.DataFrame(valores_saida, columns=colunas_saida)
    df_saida.to_csv(folder_saida / 'dados_saida.csv', index=False, float_format='%.2f')

    # gerando gráficos interessantes
    fig = px.bar(x=meses, y=rendimento_liquido, labels=dict(x='mês', y='rendimento absoluto líquido'))
    fig.write_image(folder_saida / "rendimento_abosluto_liquido.png")
    return 0

if __name__ == '__main__':
    main()
import numpy as np
import pandas as pd
from typing import List
from calculadora import *
from pathlib import Path
import plotly.graph_objects as go
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


def gera_graficos_evolucao_pm(folder_saida: Path, lista_acoes: ListaAcoes) -> None:
    evolucao_pm = folder_saida / 'evolucao_pm_por_acao'
    evolucao_pm.mkdir(exist_ok=True)
    dicionario_acoes = lista_acoes.retorna_dicionario_acoes()
    fig_geral = go.Figure()
    for acao_chave in dicionario_acoes:
        acao = dicionario_acoes[acao_chave]
        nome_acao = acao.retorna_nome()
        pm =  acao.retorna_historico_pm()

        fig = go.Figure()
        scatter = go.Scatter(x=list(range(len(pm))), y=pm, name=nome_acao,
                       line=dict(dash='dash'))
        fig.add_trace(scatter)
        fig_geral.add_trace(scatter)
        fig.update_layout(title='Evolução do PM de ' + nome_acao, xaxis_title='#operação', yaxis_title='Valor (Reais)')
        fig.update_traces(marker_size=12)
        fig.write_image(evolucao_pm / (nome_acao + ".png"))
    
    fig_geral.update_layout(title='Evolução do PM geral', xaxis_title='#operação', yaxis_title='Valor (Reais)')
    fig_geral.update_traces(marker_size=12)
    fig_geral.write_image(evolucao_pm / ('geral.png'))


def coleta_evolucao_pm_e_pv_de_operacoes(operacoes_por_acao: List[Operacao]) -> tuple[List[float], List[float]]:
    historico_pm = []
    historico_pv = []
    for op in operacoes_por_acao:
        if op.tipo == TipoOperacao.VENDA:
            historico_pm.append(op.retorna_pm_na_operacao())
            historico_pv.append(op.retorna_preco())
    
    return historico_pm, historico_pv


def gera_graficos_evolucao_pm_versus_pv(folder_saida: Path, lista_operacoes_por_acao: List[Operacao]) -> None:
    evolucao_pm_versus_pv = folder_saida / 'pm_versus_pv_por_acao'
    evolucao_pm_versus_pv.mkdir(exist_ok=True)
    for ops in lista_operacoes_por_acao:
        historico_pm, historico_pv = coleta_evolucao_pm_e_pv_de_operacoes(ops)

        nome_acao = ops[0].acao.retorna_nome()
        fig = go.Figure()
        scatter = go.Scatter(x=list(range(len(historico_pm))), y=historico_pm, name='PM',
                       line=dict(dash='dash'))
        fig.add_trace(scatter)
        scatter = go.Scatter(x=list(range(len(historico_pv))), y=historico_pv, name='PV',
                       line=dict(dash='dash'))
        fig.add_trace(scatter)
        fig.update_layout(title='Evolução do PM/PV de ' + nome_acao, xaxis_title='#operação de venda', yaxis_title='Valor (Reais)')
        fig.update_traces(marker_size=12)
        fig.write_image(evolucao_pm_versus_pv / (nome_acao + ".png"))
    

def agrupa_operacoes_por_acao(lista_operacoes: pd.Series, lista_acoes: ListaAcoes) -> List[List[Operacao]]:
    agrupamento = []
    dicionario_acoes = lista_acoes.retorna_dicionario_acoes()
    for acao_chave in dicionario_acoes:
        acao = dicionario_acoes[acao_chave]
        agrupamento.append([])
        for operacao in lista_operacoes:
            if operacao.acao == acao:
                agrupamento[-1].append(operacao)
    
    return agrupamento


def coleta_ra_por_operacao(operacoes_por_acao: List[Operacao]) -> List[float]:
    historico_ra = []
    for op in operacoes_por_acao:
        if op.tipo == TipoOperacao.VENDA:
            historico_ra.append(op.retorna_ra())
    return historico_ra


def gera_graficos_evolucao_ra(folder_saida: Path, lista_operacoes_por_acao: List[Operacao]) -> None:
    evolucao_ra = folder_saida / 'ra_por_venda_por_acao'
    evolucao_ra.mkdir(exist_ok=True)

    for ops in lista_operacoes_por_acao:
        historico_ra = coleta_ra_por_operacao(ops)

        nome_acao = ops[0].acao.retorna_nome()
        fig = go.Figure()
        scatter = go.Scatter(x=list(range(len(historico_ra))), y=historico_ra, name='RA',
                       line=dict(dash='dash'))
        fig.add_trace(scatter)
        fig.update_layout(title='RA por operação de venda de ' + nome_acao, xaxis_title='#operação de venda', yaxis_title='Valor (Reais)')
        fig.update_traces(marker_size=12)
        fig.write_image(evolucao_ra / (nome_acao + ".png"))
    


def gera_graficos(folder_saida: Path, meses: List[int], 
                  rendimento_liquido: List[float],
                  lista_acoes: ListaAcoes,
                  operacoes_df: pd.DataFrame,
                  pa: List[float]) -> None:

    # plot solicitado
    color = np.where(np.array(rendimento_liquido) < 0, 'red', 'green')
    fig = go.Figure()
    fig.add_trace(go.Bar(x=meses, y=rendimento_liquido))
    fig.update_layout(title='Rendimento absoluto líquido por mês (Rendimento Bruto - IR)', xaxis_title='Mês', yaxis_title='Valor (reais)')
    fig.update_traces(marker_color=color)
    fig.write_image(folder_saida / "rendimento_absoluto_liquido.png")

    # lucro (acúmulo do rendimento líquido)
    redimento_liquido_acumulado = np.cumsum(rendimento_liquido)
    color = np.where(np.array(redimento_liquido_acumulado) < 0, 'red', 'green')
    fig = go.Figure()
    fig.add_trace(go.Bar(x=meses, y=redimento_liquido_acumulado))
    fig.update_layout(title='Lucro (Rendimento absoluto líquido cumulativo)', xaxis_title='Mês', yaxis_title='Valor (reais)')
    fig.update_traces(marker_color=color)
    fig.write_image(folder_saida / "lucro.png")

    # evolução de pm por ação
    gera_graficos_evolucao_pm(folder_saida, lista_acoes)

    # relação pm e pc/pv por operação sobre ação
    operacoes_por_acao = agrupa_operacoes_por_acao(operacoes_df, lista_acoes)
    gera_graficos_evolucao_pm_versus_pv(folder_saida, operacoes_por_acao)

    # valores de ra por ação
    gera_graficos_evolucao_ra(folder_saida, operacoes_por_acao)

    # valores do pa por mês
    fig = go.Figure()
    fig.add_trace(go.Bar(x=meses, y=pa))
    fig.update_layout(title='PA (Prejuízo acumulado) em cada mês', xaxis_title='Mês', yaxis_title='Valor (reais)')
    fig.update_traces(marker_color=color)
    fig.write_image(folder_saida / "prejuizo_acumulado_por_mes.png")


def main():
    folder_saida = Path('outputs')
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
    pa = []
    for lista_operacoes in lista_operacoes_por_mes:
        meses.append(lista_operacoes.iloc[0].data.month)
        calculadora = CalculadoraImposto(meses[-1], lista_operacoes)
        imposto_no_mes = calculadora.retorna_imposto()
        ram = calculadora.retorna_ram()
        pa.append(calculadora.retorna_pa())
        total_compras = calculadora.retorna_total_compras()
        total_vendas = calculadora.retorna_total_vendas()
        rendimento_liquido.append(ram - imposto_no_mes)
        valores_saida.append([meses[-1], total_compras, total_vendas, ram, imposto_no_mes, rendimento_liquido[-1]])

    # gerando o df de saída
    df_saida = pd.DataFrame(valores_saida, columns=colunas_saida)
    df_saida.to_csv(folder_saida / 'dados_saida.csv', index=False, float_format='%.2f')

    # gerando gráficos interessantes
    gera_graficos(folder_saida, meses, rendimento_liquido, lista_acoes, operacoes_df, pa)
    
    return 0

if __name__ == '__main__':
    main()
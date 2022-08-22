import pandas as pd
from typing import List
from calculadora import *


def converte_tipo_para_int(
    df: pd.DataFrame,
    coluna_str: str,
    ) -> pd.DataFrame:

    conversao = lambda tipo_str: TipoOperacao.converte_op_para_int(
        tipo_str
    )
    return df[coluna_str].apply(conversao)


def pre_processa_df(dados_df: pd.DataFrame, lista_acoes: ListaAcoes) -> pd.DataFrame:
    # Faz a conversão de colunas do df para os objetos correspondentes da calculadora

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
        e['Data da operação'],
        e['Operação'],
        e['Ação'],
        e['Preço'],
        e['Quantidade'],
        e['Taxa de corretagem']
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
    dados_df = pd.read_csv('stocks-dataset.csv')
    lista_acoes = ListaAcoes(dados_df['Ação'])
    dados_df = pre_processa_df(dados_df, lista_acoes)
    operacoes_df = cria_df_de_operacoes(dados_df)
    lista_operacoes_por_mes = agrupa_operacoes_por_mes(operacoes_df)

    colunas = [
        'Mês', 
        'Valor total de compra (reais)',
        'Valor total de venda (reais)',
        'Rendimento absoluto bruto (reais)',
        'Imposto devido (reais)',
        'Rendimento absoluto líquido (reais)'
    ]
    valores_saida = []
    for lista_operacoes in lista_operacoes_por_mes:
        mes_atual = lista_operacoes.iloc[0].data.month
        calculadora = CalculadoraImposto(lista_acoes, mes_atual, lista_operacoes)
        imposto_no_mes = calculadora.retorna_imposto()
        ram = calculadora.retorna_ram()
        total_compras = calculadora.retorna_total_compras()
        total_vendas = calculadora.retorna_total_vendas()
        rendimento_liquido = ram - imposto_no_mes
        valores_saida.append([mes_atual, total_compras, total_vendas, ram, imposto_no_mes, rendimento_liquido])

    df_saida = pd.DataFrame(valores_saida, columns=colunas)
    df_saida.to_csv('dados_saida.csv', index=False, float_format='%.2f')
    return 0

if __name__ == '__main__':
    main()


# def calc_pm(pm, qm, pc, qc, tc):
#     pm = (pm * qm + pc * qc + tc) / (qm + qc)
#     return pm

# def calc_add_qm(qm, qc):
#     qm = qm + qc
#     return qc

# def calc_sell_qm(qm, qv):
#     qm = qm - qv
#     return qv 

# def calc_ra(pv, pm, qv, tv):
#     ra = (pv - pm) * qv - tv
#     return ra

# from collections import defaultdict
# import pandas as pd
# dados_df = pd.read_csv('stocks-dataset.csv')
# formato_data_str = "%Y-%m-%d"
# dados_df['Data da operação'] = pd.to_datetime(
#         dados_df['Data da operação'], format=formato_data_str)
# dados_df = dados_df.sort_values('Data da operação', ignore_index=True)
# acoes = dados_df['Ação'].unique()

# pm = defaultdict(lambda: defaultdict(lambda: -1))
# qm = defaultdict(lambda: defaultdict(lambda: -1))
# ra = defaultdict(lambda: defaultdict(lambda: []))
# pa_acao = defaultdict(lambda: defaultdict(lambda: 0))
# pa = defaultdict(lambda: 0)
# ram = defaultdict(lambda: defaultdict(lambda: [0, 0]))
# cont_mes = defaultdict(lambda: 0)

# for index, op in dados_df.iterrows():
#     acao = op['Ação']
#     mes = op['Data da operação'].month
#     cont_mes[mes] += 1

#     # sempre calcula o qm
#     # ordenação introduzida no python 3.6 e oficialmente incluida no 3.7
#     def get_value(dict_ref, mes):
#         if dict_ref[mes] < 0:
#             last_moths = list(dict_ref.keys())
#             last_moths.pop(-1)
#             if len(last_moths):
#                 mes = last_moths[-1]
        
#         return dict_ref[mes]

#     # se compra, calcula o pm
#     if op['Operação'] == 'Compra':
#         pm[acao][mes] = calc_pm(
#             get_value(pm[acao], mes),
#             get_value(qm[acao], mes),
#             op['Preço'],
#             op['Quantidade'],
#             op['Taxa de corretagem']
#         )

#         qm[acao][mes] = calc_add_qm(
#             get_value(qm[acao], mes),
#             op['Quantidade']
#         )

#     # se venda, calcupa o ra
#     # TODO: o ra parece ser só do mês; organizar melhor
#     elif op['Operação'] == 'Venda':
#         ra[mes][acao].append(calc_ra(
#             op['Preço'],
#             get_value(pm[acao], mes),
#             op['Quantidade'],
#             op['Taxa de corretagem'])
#         )

#         qm[acao][mes] = calc_sell_qm(
#             get_value(qm[acao], mes),
#             op['Quantidade']
#         )
        
#         # se houve prejuizo na última venda
#         # TODO: o pa parece ser só do mês; organizar melhor (pode ser ui interessa para análises por ação)
#         if ra[mes][acao][-1] < 0:
#             ra_abs = abs(abs(ra[mes][acao][-1]))
#             pa_acao[acao][mes] += ra_abs
#             pa[mes] += abs(ra[mes][acao][-1])
#         # se não houve prejuizo
#         else:
#             ra_abs = abs(abs(ra[mes][acao][-1]))
#             pa_acao[acao][mes] -= min(ra_abs, pa_acao[acao][mes])
#             pa[mes] -= min(ra_abs, pa_acao[acao][mes])
    
#     # TODO: calcular o auferido médio de forma gradativa (para os gráficos)
#     if len(ra[mes][acao]):
#         ram[mes][acao][0] += ra[mes][acao][-1]
#         ram[mes][acao][1] += 1
    
#     print(list(op[['Data da operação', 'Ação', 'Operação']]))
#     print('pm', get_value(pm[acao], mes))
#     print('qm', get_value(qm[acao], mes))
#     print('ra', ra[mes][acao])
#     print('pa_acao', pa_acao[acao][mes])
#     print('pa', pa[mes])

# ram_total = defaultdict(lambda: 0)
# imposto_devido = defaultdict(lambda: 0)
# for mes in ram:
#     count = 0
#     for acao in ram[mes]:
#         ram_total[mes] += ram[mes][acao][0]
#         count += ram[mes][acao][1]
#     ram_total[mes] /= count

#     ram_abs = abs(ram_total[mes])
#     imposto_devido[mes] = \
#         (ram_abs - min(ram_abs, pa[mes])) * 0.15
# print(ram, '\n')
# print(ram_total, '\n')
# print(imposto_devido, '\n')

# rendimento_liquido = []
# for key in ram_total:
#     rendimento_liquido.append(ram_total[key] - imposto_devido[key])

# import plotly.express as px
# #import plotly.io as pio
# #pio.renderers.default = "browser"

# fig = px.bar(x=ram_total.keys(), y=rendimento_liquido, labels=dict(x='mês', y='rendimento absoluto líquido'))
# fig.write_image("fig1.pdf")
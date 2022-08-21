from collections import defaultdict
import pandas as pd
from datetime import datetime

# TODO: tentar leitura da web, se não der certo, tentar ler do arquivo (colocar isso no código)
stocks_df = pd.read_csv('stocks-dataset.csv')
stocks_df['Data da operação'] = stocks_df['Data da operação'].apply(lambda data_op_str: datetime.strptime(data_op_str, "%Y-%m-%d"))
stocks_df = stocks_df.sort_values('Data da operação', ignore_index=True)
acoes = stocks_df['Ação'].unique()

def calc_pm(pm, qm, pc, qc, tc):
    pm = (pm * qm + pc * qc + tc) / (qm + qc)
    return pm

def calc_qm(qm, qc):
    qm = qm + qc
    return qc

def calc_ra(pv, pm, qv, tv):
    ra = (pv - pm) * qv - tv
    return ra


pm = defaultdict(lambda: defaultdict(lambda: 0))
qm = defaultdict(lambda: defaultdict(lambda: 0))
ra = defaultdict(lambda: defaultdict(lambda: []))
pa_acao = defaultdict(lambda: defaultdict(lambda: 0))
pa = defaultdict(lambda: 0)
ram = defaultdict(lambda: defaultdict(lambda: [0, 0]))
cont_mes = defaultdict(lambda: 0)

for index, op in stocks_df.iterrows():
    acao = op['Ação']
    mes = op['Data da operação'].month
    cont_mes[mes] += 1

    # sempre calcula o qm
    # usa valor do mês anterior como inicial
    # com essa estratégia, todo mes esses dados estarão disponíveis no mês anterior
    # não estou considerando mudança de ano (que poderia ser feita com a manipulação de datetimes)
    mes_ref = mes
    if cont_mes[mes] == 1:
        mes_ref = mes - 1 if cont_mes[mes - 1] else mes

    qm[acao][mes] = calc_qm(
        qm[acao][mes_ref],
        op['Quantidade']
    )

    # se compra, calcula o pm
    if op['Operação'] == 'Compra':
        pm[acao][mes] = calc_pm(
            pm[acao][mes_ref],
            qm[acao][mes],
            op['Preço'],
            op['Quantidade'],
            op['Taxa de corretagem']
        )
    # se venda, calcupa o ra
    # TODO: o ra parece ser só do mês; organizar melhor
    elif op['Operação'] == 'Venda':
        ra[mes][acao].append(calc_ra(
            op['Preço'],
            pm[acao][mes],
            op['Quantidade'],
            op['Taxa de corretagem'])
        )

        # se houve prejuizo na última venda
        # TODO: o pa parece ser só do mês; organizar melhor (pode ser ui interessa para análises por ação)
        if ra[mes][acao][-1] < 0:
            pa_acao[acao][mes] += abs(ra[mes][acao][-1])
            pa[mes] += abs(ra[mes][acao][-1])
        # se não houve prejuizo
        else:
            pa_acao[acao][mes] -= min(abs(ra[mes][acao][-1]), pa_acao[acao][mes])
            pa[mes] -= min(abs(ra[mes][acao][-1]), pa_acao[acao][mes])
    
    # TODO: calcular o auferido médio de forma gradativa (para os gráficos)
    if len(ra[mes][acao]):
        ram[mes][acao][0] += ra[mes][acao][-1]
        ram[mes][acao][1] += 1
    
    print(op)
    print('pm', pm[acao][mes])
    print('qm', qm[acao][mes])
    print('ra'), ra[acao][mes]
    print('pa_acao', pa_acao[acao][mes])
    print('pa', pa[mes])

ram_total = defaultdict(lambda: 0)
imposto_devido = defaultdict(lambda: 0)
for mes in ram:
    count = 0
    for acao in ram[mes]:
        ram_total[mes] += ram[mes][acao][0]
        count += ram[mes][acao][1]
    ram_total[mes] /= count

    imposto_devido[mes] = \
        (ram_total[mes] - min(ram_total[mes], pa[mes])) * 0.15
print(ram_total)
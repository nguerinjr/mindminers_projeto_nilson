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

def calc_add_qm(qm, qc):
    qm = qm + qc
    return qc

def calc_sell_qm(qm, qv):
    qm = qm - qv
    return qv

def calc_ra(pv, pm, qv, tv):
    ra = (pv - pm) * qv - tv
    return ra


pm = defaultdict(lambda: defaultdict(lambda: -1))
qm = defaultdict(lambda: defaultdict(lambda: -1))
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
    # ordenação introduzida no python 3.6 e oficialmente incluida no 3.7
    def get_value(dict_ref, mes):
        if dict_ref[mes] < 0:
            last_moths = list(dict_ref.keys())
            last_moths.pop(-1)
            if len(last_moths):
                mes = last_moths[-1]
        
        return dict_ref[mes]

    # se compra, calcula o pm
    if op['Operação'] == 'Compra':
        pm[acao][mes] = calc_pm(
            get_value(pm[acao], mes),
            get_value(qm[acao], mes),
            op['Preço'],
            op['Quantidade'],
            op['Taxa de corretagem']
        )

        qm[acao][mes] = calc_add_qm(
            get_value(qm[acao], mes),
            op['Quantidade']
        )

    # se venda, calcupa o ra
    # TODO: o ra parece ser só do mês; organizar melhor
    elif op['Operação'] == 'Venda':
        ra[mes][acao].append(calc_ra(
            op['Preço'],
            get_value(pm[acao], mes),
            op['Quantidade'],
            op['Taxa de corretagem'])
        )

        qm[acao][mes] = calc_sell_qm(
            get_value(qm[acao], mes),
            op['Quantidade']
        )
        
        # se houve prejuizo na última venda
        # TODO: o pa parece ser só do mês; organizar melhor (pode ser ui interessa para análises por ação)
        if ra[mes][acao][-1] < 0:
            ra_abs = abs(abs(ra[mes][acao][-1]))
            pa_acao[acao][mes] += ra_abs
            pa[mes] += abs(ra[mes][acao][-1])
        # se não houve prejuizo
        else:
            ra_abs = abs(abs(ra[mes][acao][-1]))
            pa_acao[acao][mes] -= min(ra_abs, pa_acao[acao][mes])
            pa[mes] -= min(ra_abs, pa_acao[acao][mes])
    
    # TODO: calcular o auferido médio de forma gradativa (para os gráficos)
    if len(ra[mes][acao]):
        ram[mes][acao][0] += ra[mes][acao][-1]
        ram[mes][acao][1] += 1
    
    print(list(op[['Data da operação', 'Ação', 'Operação']]))
    print('pm', get_value(pm[acao], mes))
    print('qm', get_value(qm[acao], mes))
    print('ra', ra[mes][acao])
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

    ram_abs = abs(ram_total[mes])
    imposto_devido[mes] = \
        (ram_abs - min(ram_abs, pa[mes])) * 0.15
print(ram, '\n')
print(ram_total, '\n')
print(imposto_devido, '\n')
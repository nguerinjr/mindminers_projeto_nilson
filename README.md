# mindminers_projeto_nilson

- A versão utilizada de python para implementar e testar o código foi a 3.10.4.
- há um arquivo requirements.txt com as versões das bibliotecas utilizadas.
- O script principal é o analise_operacoes.py. Nele há uma função main, que acessa a interface da calculadora e gera os plots.
- O arquivo calculadora.py tem a implementação da classe da calculadora.
- Para fins de simplificadade, a declaração de todas as classes usadas pela interface da calculadora estão no arquivo da calculadora.
- Todos os nomes de variáveis e funções são extensos para melhorar a legibilidade do código.
- As saídas são geradas num folder de outputs. O .csv requerido tem o nome "dados_saida.csv".

- Foram gerados gráficos simples com diferentes perspectivas sobre a evolução das operações. São listados abaixo.
- rendimento_absoluto_liquido: (rendimento bruto - IR) para cada mês [solicitado na especificação do projeto]
- prejuizo_acumulado_por_mes: o valor do PA para cada mês;
- lucro: o rendimento absoluto líquido acumulado através dos meses
- evolucao_pm_por_acao: as mudanças do PM de cada ação na medida em que operações de compra foram realizadas; há gráfico com sobreposição de todas as ações
- pm_versus_pv_por_acao: a relação entre o PV e o PM da ação, logo antes da operação de compra (uma forma de observar o RA naquela operação)
- ra_por_venda_por_ação: os valores de todos os RA das vendas para cada ação (uma forma de observar o prejuízo e o lucro, em cada uma das operações)

PS: Esses foram alguns gráficos escolhidos, destacando que o código foi feito de forma que seja fácil coletar várias outras informações sobre a evolução do cenário, se for o caso.
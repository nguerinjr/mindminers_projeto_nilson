from typing import List
import pandas as pd


class TipoOperacao():
    COMPRA: int = 0
    VENDA: int = 1

    @staticmethod
    def converte_op_para_int(nome_op_str: str) -> int:
        if nome_op_str.lower() == 'compra':
            return TipoOperacao.COMPRA
        elif nome_op_str.lower() == 'venda':
            return TipoOperacao.VENDA
        else:
            raise ValueError("Operacação não conhecida!")


class Acao():
    def __init__(self, nome: str) -> None:
        self.nome = nome
        self.pm = 0.
        self.qm = 0.
    
    def atualiza_qm(self, quantidade: int, tipo_op: TipoOperacao) -> None:
        if tipo_op == TipoOperacao.COMPRA:
            self.qm += quantidade
        elif tipo_op == TipoOperacao.VENDA:
            self.qm -= quantidade
        else:
            raise ValueError("Tipo de operacao desconhecida!")
    
    def atualiza_pm(self, preco: float, quantidade: int,
        taxa_corretagem: int) -> None:
        pm = 0
        pm += self.pm * self.qm
        pm += preco * quantidade + taxa_corretagem
        pm /= (self.qm + quantidade)
        self.pm = pm


class ListaAcoes():
    def __init__(self, acoes_serie:pd.Series=None) -> None:
        self.acoes_obj = {}
        if acoes_serie is not None:
            acoes_str = acoes_serie.unique()
            for acao_str in acoes_str:
                self.acoes_obj[acao_str] = Acao(acao_str)
    
    def retorna_acao_por_nome(self, nome_acao: str) -> Acao:
        if nome_acao in self.acoes_obj:
            acao = self.acoes_obj[nome_acao]
        else:
            acao = None

        return acao


class Operacao():
    def __init__(self, data: pd.Timestamp, tipo: TipoOperacao,
        acao: Acao, preco: float, quantidade: int,
        taxa_corretagem: int) -> None:
        self.data = data
        self.tipo = tipo
        self.preco = preco
        self.quantidade = quantidade
        self.taxa_corretagem = taxa_corretagem
        self.acao = acao

        self.ra = None
    
    def retorna_ra(self) -> float:
        self.calcula_ra() # Se não calculou, será calculado antes de retornar
        return self.ra
    
    def retorna_preco(self) -> float:
        return self.preco
    
    def retorna_tipo(self) -> TipoOperacao:
        return self.tipo
    
    def retorna_quantidade(self) -> float:
        return self.quantidade
    
    def calcula_ra(self) -> None:
        if self.ra is None:
            if self.tipo == TipoOperacao.COMPRA:
                self.acao.atualiza_pm(self.preco, self.quantidade, self.taxa_corretagem)
                self.ra = 0. # não há RA em caso de op de compra. Define como zero.
            elif self.tipo == TipoOperacao.VENDA:
                ra = (self.preco - self.acao.pm) * self.quantidade - self.taxa_corretagem
                self.ra = ra
            self.acao.atualiza_qm(self.quantidade, self.tipo)

    
class CalculadoraImposto():
    def __init__(
        self, 
        lista_acoes: List[Acao], 
        mes_atual: int, 
        lista_operacoes: List[Operacao]
        ) -> None:

        self.lista_acoes = lista_acoes
        self.lista_operacoes = lista_operacoes
        self.mes_atual = mes_atual
        self.ram = None
        self.pa = None
        self.total_compra = None
        self.total_venda = None
        self.imposto_devido = None
        self.rendimento_liquido = None

    def retorna_lista_operacoes(self) -> List[Operacao]:
        return self.lista_operacoes

    def retorna_ram(self) -> float:
        self.calcula_ram()
        return self.ram
    
    def retorna_pa(self) -> float:
        self.calcula_pa()
        return self.pa

    def retorna_imposto(self) -> float:
        self.calcula_imposto()
        return self.imposto_devido
    
    def retorna_total_vendas(self) -> float:
        self.calcula_total_venda()
        return self.total_venda

    def retorna_total_compras(self) -> float:
        self.calcula_total_compra()
        return self.total_compra
    
    def retorna_mes_atual(self) -> int:
        return self.mes_atual

    def calcula_pa(self) -> None:
        if self.pa is None:
            pa = 0.
            for operacao in self.lista_operacoes:
                operacao.calcula_ra()
                ra = operacao.retorna_ra()
                if ra < 0:
                    pa += abs(ra)
                else:
                    pa -= min(ra, pa)
            self.pa = pa
        
    def _calcula_total(self, tipo_op_desejado: TipoOperacao) -> float:
        total = 0.
        for operacao in self.lista_operacoes:
                tipo = operacao.retorna_tipo()
                if tipo == tipo_op_desejado:
                    valor_unidade = operacao.retorna_preco()
                    quantidade = operacao.retorna_quantidade()
                    valor = valor_unidade * quantidade
                    total += valor
        return total

    def calcula_total_compra(self) -> None:
        if self.total_compra is None:
            total_compra = self._calcula_total(TipoOperacao.COMPRA)
            self.total_compra = total_compra
    
    def calcula_total_venda(self) -> None:
        if self.total_venda is None:
            total_venda = self._calcula_total(TipoOperacao.VENDA)
            self.total_venda = total_venda

    def calcula_ram(self) -> None:
        if self.ram is None:
            ram = 0.
            for operacao in self.lista_operacoes:
                operacao.calcula_ra()
                ra = operacao.retorna_ra()
                ram += ra
            self.ram = ram
    
    def calcula_imposto(self) -> None:
        self.calcula_ram()
        self.calcula_pa()
        self.imposto_devido = (self.ram - min(self.ram, self.pa)) * 0.15

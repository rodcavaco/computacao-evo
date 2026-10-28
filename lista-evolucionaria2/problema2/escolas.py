import json
from math import dist
from random import randint, sample, random
 
 
class EscolasTurnos:
    def __init__(self, arquivo='q2_turnos.json'):
        self.populacao = []
 
        with open(arquivo, encoding='utf-8') as f:
            dados = json.load(f)
 
        self.escolas = dados['escolas']
        self.total_escolas = len(self.escolas)
 
        # peso de cada par = congestionamento se ficarem no mesmo turno (1 / distância em km)
        self.peso = [[0.0] * self.total_escolas for _ in range(self.total_escolas)]
        for i in range(self.total_escolas):
            for j in range(self.total_escolas):
                if i != j:
                    self.peso[i][j] = 1 / dist(self.escolas[i], self.escolas[j])
 
        self.tamanho_populacao = 60
        self.taxa_de_cruzamento = 0.95
        self.taxa_de_mutacao = 0.03
        self.geracoes_maxima = 500
 
        self.torneio = 4
 
        self.historico = []  # menor congestionamento de cada geração (convergência)
 
    # Indivíduo: vetor binário de 40 posições. 0 = manhã, 1 = tarde.
    def inicializar_populacao(self):
        self.populacao = []
        for i in range(self.tamanho_populacao):
            individuo = [randint(0, 1) for _ in range(self.total_escolas)]
            self.populacao.append(individuo)
 
    # Congestionamento total: soma de 1/distância dos pares no mesmo turno.
    # É um problema de MINIMIZAÇÃO (menor é melhor).
    def fitness(self, individuo):
        total = 0
        for i in range(self.total_escolas):
            for j in range(i + 1, self.total_escolas):
                if individuo[i] == individuo[j]:
                    total += self.peso[i][j]
        return total
 
    def reproducao_da_geracao(self):
        prole = []
        for _ in range(self.tamanho_populacao // 2):
            pai, mae = self.selecao_dos_pais()
 
            if random() < self.taxa_de_cruzamento:
                filho1, filho2 = self.cruzamento(pai, mae)
            else:
                filho1, filho2 = pai[:], mae[:]
 
            self.mutar(filho1)
            self.mutar(filho2)
 
            prole.extend([filho1, filho2])
 
        return prole
 
    def selecao_dos_pais(self):
        candidatos_pai = sample(self.populacao, k=self.torneio)
        candidatos_mae = sample(self.populacao, k=self.torneio)
 
        pai = min(candidatos_pai, key=self.fitness)
        mae = min(candidatos_mae, key=self.fitness)
 
        return pai, mae
 
    def cruzamento(self, pai, mae):
        corte = randint(1, self.total_escolas - 1)
 
        filho1 = pai[:corte] + mae[corte:]
        filho2 = mae[:corte] + pai[corte:]
 
        return filho1, filho2
 
    def mutar(self, filho):
        for gene in range(len(filho)):
            if random() < self.taxa_de_mutacao:
                filho[gene] = 1 - filho[gene]
 
    def selecao_dos_sobreviventes(self, prole):
        melhor = min(self.populacao, key=self.fitness)
        pior_filho = max(prole, key=self.fitness)
 
        prole.remove(pior_filho)
 
        self.populacao = [melhor] + prole
 
    def melhor(self):
        return min(self.populacao, key=self.fitness)
 
    def evolucao(self):
        self.historico = []
        self.inicializar_populacao()
 
        for geracao in range(self.geracoes_maxima):
            prole = self.reproducao_da_geracao()
            self.selecao_dos_sobreviventes(prole)
            self.historico.append(self.fitness(self.melhor()))
 
    def saida(self):
        solucao = self.melhor()
 
        # A solução e a sua complementar (trocar manhã por tarde) são equivalentes.
        # Normaliza para que a escola 1 fique sempre na manhã.
        if solucao[0] == 1:
            solucao = [1 - g for g in solucao]
 
        manha = [i + 1 for i in range(self.total_escolas) if solucao[i] == 0]
        tarde = [i + 1 for i in range(self.total_escolas) if solucao[i] == 1]
 
        print(f'Solução encontrada: {solucao}')
        print(f'Congestionamento total: {self.fitness(solucao):.4f}')
        print('\n=== DIVISÃO DAS ESCOLAS ===')
        print(f'Manhã ({len(manha)} escolas): {manha}')
        print(f'Tarde ({len(tarde)} escolas): {tarde}')
 
    def execucoes_multiplas(self, n=30):
        resultados = []
 
        for k in range(n):
            self.evolucao()
            solucao = self.melhor()
            if solucao[0] == 1:
                solucao = [1 - g for g in solucao]
            resultados.append((self.fitness(solucao), solucao))
            tarde = [i + 1 for i in range(self.total_escolas) if solucao[i] == 1]
            print(f'Execução {k + 1:2d}: {self.fitness(solucao):.4f}  tarde: {tarde}')
 
        valores = [r[0] for r in resultados]
        media = sum(valores) / n
        desvio = (sum((v - media) ** 2 for v in valores) / n) ** 0.5
 
        print('\n=== RESUMO DAS EXECUÇÕES ===')
        print(f'Melhor: {min(valores):.4f}')
        print(f'Pior:   {max(valores):.4f}')
        print(f'Média:  {media:.4f}')
        print(f'Desvio padrão: {desvio:.4f}')
 
        melhor_fit, melhor_sol = min(resultados, key=lambda r: r[0])
        self.populacao = [melhor_sol]
        print('\n=== MELHOR SOLUÇÃO GERAL ===')
        self.saida()
 
 
if __name__ == '__main__':
    EscolasTurnos = EscolasTurnos()
    EscolasTurnos.execucoes_multiplas(30)
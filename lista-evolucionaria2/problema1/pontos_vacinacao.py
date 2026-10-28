import json
from math import dist
from random import randint
from random import sample
from random import random
from random import shuffle


class PontosVacinacao:
    def __init__(self, arquivo='q1_vacinacao.json'):
        self.populacao = []

        with open(arquivo, encoding='utf-8') as f:
            dados = json.load(f)

        self.locais = dados['locais']
        self.total_locais = len(self.locais)
        self.pontos_a_escolher = dados['pontos_a_escolher']

        # matriz de distâncias pré-computada (distância em linha reta, em km)
        self.distancias = [[dist(a, b) for b in self.locais] for a in self.locais]

        self.tamanho_populacao = 50
        self.taxa_de_cruzamento = 0.95
        self.taxa_de_mutacao = 0.2
        self.geracoes_maxima = 300

        self.torneio = 4

    # Indivíduo: lista com os índices (0 a 39) dos locais escolhidos, sem repetição.
    def inicializar_populacao(self):
        for i in range(self.tamanho_populacao):
            individuo = sample(range(self.total_locais), self.pontos_a_escolher)
            self.populacao.append(individuo)

    def fitness(self, individuo):
        total = 0
        for i in range(len(individuo)):
            for j in range(i + 1, len(individuo)):
                total += self.distancias[individuo[i]][individuo[j]]
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

        pai = max(candidatos_pai, key=self.fitness)
        mae = max(candidatos_mae, key=self.fitness)

        return pai, mae

    def cruzamento(self, pai, mae):
        # Genes em comum são mantidos nos dois filhos; os demais são
        # redistribuídos aleatoriamente, sem gerar repetição.
        comuns = set(pai) & set(mae)
        restantes = list((set(pai) | set(mae)) - comuns)
        shuffle(restantes)

        faltam = self.pontos_a_escolher - len(comuns)
        filho1 = list(comuns) + restantes[:faltam]
        filho2 = list(comuns) + restantes[-faltam:] if faltam > 0 else list(comuns)

        return filho1, filho2

    def mutar(self, filho):
        # Troca um local escolhido por um local ainda não escolhido.
        for gene in range(len(filho)):
            if random() < self.taxa_de_mutacao:
                novo = randint(0, self.total_locais - 1)
                while novo in filho:
                    novo = randint(0, self.total_locais - 1)
                filho[gene] = novo

    def selecao_dos_sobreviventes(self, prole):
        melhor = max(self.populacao, key=self.fitness)
        pior_filho = min(prole, key=self.fitness)

        prole.remove(pior_filho)

        self.populacao = [melhor] + prole

    def melhor(self):
        return max(self.populacao, key=self.fitness)

    def evolucao(self):
        self.inicializar_populacao()

        for geracao in range(self.geracoes_maxima):
            prole = self.reproducao_da_geracao()
            self.selecao_dos_sobreviventes(prole)

    def saida(self):
        solucao = sorted(self.melhor())

        print(f'Solução encontrada (índices, base 0): {solucao}')
        print(f'Locais escolhidos (numeração 1 a 40): {[i + 1 for i in solucao]}')
        print(f'Fitness (soma das distâncias): {self.fitness(solucao):.4f} km')

        print('\n=== COORDENADAS DOS PONTOS ESCOLHIDOS ===')
        for i in solucao:
            x, y = self.locais[i]
            print(f'Local {i + 1}: ({x}, {y})')


if __name__ == '__main__':
    PontosVacinacao = PontosVacinacao()
    PontosVacinacao.evolucao()
    PontosVacinacao.saida()
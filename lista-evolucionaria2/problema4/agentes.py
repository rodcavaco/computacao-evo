import json
from math import dist
from random import randint, sample, random

class AgentesSaude:
    def __init__(self, arquivo='q4_territorios.json'):
        self.populacao = []

        with open(arquivo, encoding='utf-8') as f:
            dados = json.load(f)

        self.num_equipes = dados['equipes']
        self.bairros = dados['bairros']
        self.total_bairros = len(self.bairros)
        self.bairros_por_equipe = self.total_bairros // self.num_equipes

        # Matriz de distâncias pré-computada (distância euclidiana)
        self.distancias = [[dist(a, b) for b in self.bairros] for a in self.bairros]

        # Parâmetros do Algoritmo Evolutivo
        self.tamanho_populacao = 200
        self.taxa_de_cruzamento = 0.95
        self.taxa_de_mutacao = 0.3
        self.geracoes_maxima = 600
        self.torneio = 5

        self.cache = {}

    # Indivíduo: Uma PERMUTAÇÃO dos índices dos 24 bairros (0 a 23).
    # A decodificação é implícita: os 6 primeiros são da equipa 1, os próximos 6 da equipa 2, etc.
    def inicializar_populacao(self):
        self.populacao = []
        for _ in range(self.tamanho_populacao):
            individuo = sample(range(self.total_bairros), self.total_bairros)
            self.populacao.append(individuo)

    # Função a ser minimizada: soma das distâncias de todos os pares dentro de cada equipa.
    def fitness(self, individuo):
        chave = tuple(individuo)
        if chave not in self.cache:
            distancia_total = 0
            
            # Avalia cada bloco de bairros como uma equipa isolada
            for i in range(self.num_equipes):
                inicio = i * self.bairros_por_equipe
                fim = inicio + self.bairros_por_equipe
                equipe = individuo[inicio:fim]
                
                # Soma as distâncias entre todos os pares da mesma equipa
                for j in range(len(equipe)):
                    for k in range(j + 1, len(equipe)):
                        distancia_total += self.distancias[equipe[j]][equipe[k]]
                        
            self.cache[chave] = distancia_total
            
        return self.cache[chave]

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

        # Como queremos MINIMIZAR a distância, usamos min()
        pai = min(candidatos_pai, key=self.fitness)
        mae = min(candidatos_mae, key=self.fitness)

        return pai, mae

    # Cruzamento OX (Order Crossover): ideal para permutações pois
    # não duplica nem perde genes (bairros).
    def cruzamento(self, pai, mae):
        a, b = sorted(sample(range(self.total_bairros), 2))

        def ox(p1, p2):
            filho = [None] * self.total_bairros
            filho[a:b] = p1[a:b]
            usados = set(p1[a:b])
            resto = iter([g for g in p2 if g not in usados])
            for i in range(self.total_bairros):
                if filho[i] is None:
                    filho[i] = next(resto)
            return filho

        return ox(pai, mae), ox(mae, pai)

    # Mutação por Troca (Swap): troca dois bairros de lugar na permutação.
    def mutar(self, filho):
        if random() < self.taxa_de_mutacao:
            i, j = sample(range(self.total_bairros), 2)
            filho[i], filho[j] = filho[j], filho[i]

    def selecao_dos_sobreviventes(self, prole):
        melhor = min(self.populacao, key=self.fitness)
        pior_filho = max(prole, key=self.fitness)

        prole.remove(pior_filho)
        # Elitismo: o melhor da geração anterior passa para a próxima
        self.populacao = [melhor] + prole

    def melhor(self):
        return min(self.populacao, key=self.fitness)

    def evolucao(self):
        self.cache = {}
        self.inicializar_populacao()

        for _ in range(self.geracoes_maxima):
            prole = self.reproducao_da_geracao()
            self.selecao_dos_sobreviventes(prole)

    def saida(self):
        melhor_solucao = self.melhor()
        fitness_final = self.fitness(melhor_solucao)

        print(f'Soma das distâncias minimizada: {fitness_final:.4f} km\n')
        print('=== DIVISÃO DAS EQUIPAS ===')
        
        for i in range(self.num_equipes):
            inicio = i * self.bairros_por_equipe
            fim = inicio + self.bairros_por_equipe
            equipe = melhor_solucao[inicio:fim]
            
            # Ajustando de índice 0 (Python) para numeração 1 a 24
            equipe_formatada = sorted([b + 1 for b in equipe])
            print(f'Equipa {i + 1}: Bairros {equipe_formatada}')

if __name__ == '__main__':
    agentes = AgentesSaude()
    agentes.evolucao()
    agentes.saida()
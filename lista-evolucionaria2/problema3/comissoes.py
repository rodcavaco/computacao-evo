import json
from itertools import combinations
from random import randint, sample, random

class ReunioesComissoes:
    def __init__(self, arquivo='q3_comissoes.json'):
        self.populacao = []

        with open(arquivo, encoding='utf-8') as f:
            dados = json.load(f)

        self.total_comissoes = dados['comissoes']

        # Grafo de conflitos: duas comissões são vizinhas se têm um professor em comum.
        self.vizinhos = [set() for _ in range(self.total_comissoes)]
        for comissoes_do_professor in dados['professores']:
            for a, b in combinations(comissoes_do_professor, 2):
                self.vizinhos[a - 1].add(b - 1)
                self.vizinhos[b - 1].add(a - 1)

        self.tamanho_populacao = 200
        self.taxa_de_cruzamento = 0.95
        self.taxa_de_mutacao = 0.8
        self.geracoes_maxima = 500

        self.torneio = 4

        self.cache = {}      # fitness já calculados (acelera bastante)
        self.historico = []  # menor número de horários de cada geração (convergência)

    # Indivíduo: PERMUTAÇÃO das 50 comissões (ordem em que serão coloridas).
    # A permutação é decodificada de forma gulosa: cada comissão recebe o
    # primeiro horário que nenhuma comissão vizinha já colorida esteja usando.
    # Assim todo indivíduo gera uma coloração válida (sem conflitos), e o AE
    # só precisa minimizar o número de horários.
    def inicializar_populacao(self):
        self.populacao = []
        for i in range(self.tamanho_populacao):
            individuo = sample(range(self.total_comissoes), self.total_comissoes)
            self.populacao.append(individuo)

    def decodificar(self, individuo):
        horario = [-1] * self.total_comissoes
        for comissao in individuo:
            usados = {horario[v] for v in self.vizinhos[comissao]}
            h = 0
            while h in usados:
                h += 1
            horario[comissao] = h
        return horario

    # Minimização. O termo principal é o número de horários; o desempate favorece
    # horários bem desiguais (uns bem cheios, outros quase vazios), o que ajuda
    # a eliminar o horário menos usado nas gerações seguintes.
    def fitness(self, individuo):
        chave = tuple(individuo)
        if chave not in self.cache:
            horario = self.decodificar(individuo)
            qtd = max(horario) + 1
            tamanhos = [horario.count(h) for h in range(qtd)]
            n = self.total_comissoes
            self.cache[chave] = n * n * qtd - sum(t * t for t in tamanhos)
        return self.cache[chave]

    def numero_de_horarios(self, individuo):
        return max(self.decodificar(individuo)) + 1

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

    # Cruzamento OX (order crossover): copia um trecho de um pai e completa
    # com os genes que faltam na ordem em que aparecem no outro pai.
    def cruzamento(self, pai, mae):
        a, b = sorted(sample(range(self.total_comissoes), 2))

        def ox(p1, p2):
            filho = [None] * self.total_comissoes
            filho[a:b] = p1[a:b]
            usados = set(p1[a:b])
            resto = iter([g for g in p2 if g not in usados])
            for i in range(self.total_comissoes):
                if filho[i] is None:
                    filho[i] = next(resto)
            return filho

        return ox(pai, mae), ox(mae, pai)

    # Mutação por troca: sorteia duas posições e troca os genes.
    def mutar(self, filho):
        if random() < self.taxa_de_mutacao:
            i, j = sample(range(self.total_comissoes), 2)
            filho[i], filho[j] = filho[j], filho[i]

    def selecao_dos_sobreviventes(self, prole):
        melhor = min(self.populacao, key=self.fitness)
        pior_filho = max(prole, key=self.fitness)

        prole.remove(pior_filho)

        self.populacao = [melhor] + prole

    def melhor(self):
        return min(self.populacao, key=self.fitness)

    def evolucao(self):
        self.historico = []
        self.cache = {}
        self.inicializar_populacao()

        for geracao in range(self.geracoes_maxima):
            prole = self.reproducao_da_geracao()
            self.selecao_dos_sobreviventes(prole)
            self.historico.append(self.numero_de_horarios(self.melhor()))

    def saida(self, individuo=None):
        if individuo is None:
            individuo = self.melhor()

        horario = self.decodificar(individuo)
        qtd = max(horario) + 1

        print(f'Número de horários: {qtd}')
        print('\n=== HORÁRIO DE CADA COMISSÃO ===')
        for h in range(qtd):
            membros = [i + 1 for i in range(self.total_comissoes) if horario[i] == h]
            print(f'Horário {h + 1:2d}: comissões {membros}')

        # confere que nenhuma comissão divide horário com uma vizinha
        conflitos = sum(1 for i in range(self.total_comissoes)
                        for v in self.vizinhos[i] if i < v and horario[i] == horario[v])
        print(f'\nConflitos: {conflitos}')

    def execucoes_multiplas(self, n=30):
        resultados = []

        for k in range(n):
            self.evolucao()
            melhor = self.melhor()
            qtd = self.numero_de_horarios(melhor)
            resultados.append((qtd, melhor))
            print(f'Execução {k + 1:2d}: {qtd} horários', flush=True)

        valores = [r[0] for r in resultados]
        media = sum(valores) / n
        desvio = (sum((v - media) ** 2 for v in valores) / n) ** 0.5

        print('\n=== RESUMO DAS EXECUÇÕES ===')
        print(f'Melhor: {min(valores)} horários')
        print(f'Pior:   {max(valores)} horários')
        print(f'Média:  {media:.2f}')
        print(f'Desvio padrão: {desvio:.2f}')

        print('\n=== MELHOR SOLUÇÃO GERAL ===')
        self.saida(min(resultados, key=lambda r: r[0])[1])


if __name__ == '__main__':
    ReunioesComissoes = ReunioesComissoes()
    ReunioesComissoes.execucoes_multiplas(10)
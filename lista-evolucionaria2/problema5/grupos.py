import json
from random import sample, random

class GruposTurma:
    def __init__(self, arquivo='q5_grupos.json'):
        self.populacao = []

        with open(arquivo, encoding='utf-8') as f:
            dados = json.load(f)

        self.total_alunos = dados['alunos']
        self.num_grupos = dados['grupos']
        self.tamanho_grupo = self.total_alunos // self.num_grupos
        
        # Ajusta os índices das amizades de 1-28 para 0-27
        self.amizades = [(u - 1, v - 1) for u, v in dados['amizades']]

        # Parâmetros do Algoritmo Evolutivo
        self.tamanho_populacao = 200
        self.taxa_de_cruzamento = 0.95
        self.taxa_de_mutacao = 0.8
        self.geracoes_maxima = 500
        self.torneio = 4

        self.cache = {}
        self.historico = []

    # Indivíduo: PERMUTAÇÃO dos 28 alunos.
    # Os primeiros 7 formam o grupo 0, os próximos 7 o grupo 1, etc.
    def inicializar_populacao(self):
        self.populacao = []
        for _ in range(self.tamanho_populacao):
            individuo = sample(range(self.total_alunos), self.total_alunos)
            self.populacao.append(individuo)

    def decodificar(self, individuo):
        # Mapeia cada aluno para o ID do seu grupo (0 a 3)
        grupo_do_aluno = [-1] * self.total_alunos
        for i, aluno in enumerate(individuo):
            grupo_do_aluno[aluno] = i // self.tamanho_grupo
        return grupo_do_aluno

    # Função de Fitness: Conta quantos pares de amigos ficaram em grupos diferentes.
    # Queremos MINIMIZAR este valor.
    def fitness(self, individuo):
        chave = tuple(individuo)
        if chave not in self.cache:
            grupo_do_aluno = self.decodificar(individuo)
            amizades_separadas = 0
            
            for u, v in self.amizades:
                if grupo_do_aluno[u] != grupo_do_aluno[v]:
                    amizades_separadas += 1
                    
            self.cache[chave] = amizades_separadas
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

        pai = min(candidatos_pai, key=self.fitness)
        mae = min(candidatos_mae, key=self.fitness)

        return pai, mae

    # Cruzamento OX (Order Crossover)
    def cruzamento(self, pai, mae):
        a, b = sorted(sample(range(self.total_alunos), 2))

        def ox(p1, p2):
            filho = [None] * self.total_alunos
            filho[a:b] = p1[a:b]
            usados = set(p1[a:b])
            resto = iter([g for g in p2 if g not in usados])
            for i in range(self.total_alunos):
                if filho[i] is None:
                    filho[i] = next(resto)
            return filho

        return ox(pai, mae), ox(mae, pai)

    # Mutação Swap: Troca dois alunos de lugar.
    def mutar(self, filho):
        if random() < self.taxa_de_mutacao:
            i, j = sample(range(self.total_alunos), 2)
            filho[i], filho[j] = filho[j], filho[i]

    def selecao_dos_sobreviventes(self, prole):
        melhor = min(self.populacao, key=self.fitness)
        pior_filho = max(prole, key=self.fitness)

        prole.remove(pior_filho)
        # Elitismo
        self.populacao = [melhor] + prole

    def melhor(self):
        return min(self.populacao, key=self.fitness)

    def evolucao(self):
        self.historico = []
        self.cache = {}
        self.inicializar_populacao()

        for _ in range(self.geracoes_maxima):
            prole = self.reproducao_da_geracao()
            self.selecao_dos_sobreviventes(prole)
            self.historico.append(self.fitness(self.melhor()))

    def saida(self, individuo=None):
        if individuo is None:
            individuo = self.melhor()

        amizades_separadas = self.fitness(individuo)
        
        print(f'Pares de amigos separados (Fitness): {amizades_separadas}')
        print('\n=== DIVISÃO DOS GRUPOS ===')
        
        for i in range(self.num_grupos):
            inicio = i * self.tamanho_grupo
            fim = inicio + self.tamanho_grupo
            grupo = individuo[inicio:fim]
            
            # Formatando para exibição de 1 a 28
            grupo_formatado = sorted([aluno + 1 for aluno in grupo])
            print(f'Grupo {i + 1}: {grupo_formatado}')

    def execucoes_multiplas(self, n=30):
        resultados = []

        for k in range(n):
            self.evolucao()
            melhor = self.melhor()
            fit = self.fitness(melhor)
            resultados.append((fit, melhor))
            print(f'Execução {k + 1:2d}: {fit} amizades separadas', flush=True)

        valores = [r[0] for r in resultados]
        media = sum(valores) / n
        desvio = (sum((v - media) ** 2 for v in valores) / n) ** 0.5

        print('\n=== RESUMO DAS EXECUÇÕES ===')
        print(f'Melhor: {min(valores)} amizades separadas')
        print(f'Pior:   {max(valores)} amizades separadas')
        print(f'Média:  {media:.2f}')
        print(f'Desvio padrão: {desvio:.2f}')

        print('\n=== MELHOR SOLUÇÃO GERAL ===')
        self.saida(min(resultados, key=lambda r: r[0])[1])

if __name__ == '__main__':
    turma = GruposTurma()
    # Executa apenas 1 vez se quiser um teste rápido, ou 30 para avaliação estatística
    turma.execucoes_multiplas(30)
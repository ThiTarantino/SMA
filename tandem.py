"""
Simulador de Rede de Filas em Tandem orientado a eventos (G/G/c/K).
Etapa 2 - Filas em Tandem
"""
import heapq

class LCG:
    def __init__(self, seed, a=1103515245, c=12345, M=2**31):
        self.a, self.c, self.M = a, c, M
        self.x = seed
        self.count = 0

    def next(self):
        self.x = (self.a * self.x + self.c) % self.M
        self.count += 1
        return self.x / self.M   

def U(a, b, r):
    return a + (b - a) * r

def simular_tandem(seed=12345, limite_aleatorios=100000):
    rng = LCG(seed)
    
    ch1_min, ch1_max = 1.0, 5.0
    at1_min, at1_max = 4.0, 5.0
    servidores1 = 2
    capacidade1 = 3
    
    at2_min, at2_max = 1.0, 3.0
    servidores2 = 1
    capacidade2 = 5

    t = 0.0
    n1 = 0  
    n2 = 0  
    
    tempos1 = {i: 0.0 for i in range(capacidade1 + 1)}
    tempos2 = {i: 0.0 for i in range(capacidade2 + 1)}
    
    perdas1 = 0
    perdas2 = 0

    eventos = []
    
    heapq.heappush(eventos, (2.5, 'CHEGADA_EXT', 1))
    
    ultimo_t = 0.0
    parar = False

    while eventos and not parar:
        tempo_prox, tipo, fila_alvo = heapq.heappop(eventos)
        
        delta = tempo_prox - t
        if delta > 0:
            tempos1[n1] += delta
            tempos2[n2] += delta
            t = tempo_prox
            ultimo_t = t

        if tipo == 'CHEGADA_EXT':
            if rng.count < limite_aleatorios:
                tec = U(ch1_min, ch1_max, rng.next())
                heapq.heappush(eventos, (t + tec, 'CHEGADA_EXT', 1))
            
            if n1 < capacidade1:
                n1 += 1
                if n1 <= servidores1:
                    if rng.count < limite_aleatorios:
                        ts1 = U(at1_min, at1_max, rng.next())
                        heapq.heappush(eventos, (t + ts1, 'SAIDA_1', 1))
            else:
                perdas1 += 1

        elif tipo == 'SAIDA_1':
            n1 -= 1
            
            if n1 >= servidores1:
                if rng.count < limite_aleatorios:
                    ts1 = U(at1_min, at1_max, rng.next())
                    heapq.heappush(eventos, (t + ts1, 'SAIDA_1', 1))

            if n2 < capacidade2:
                n2 += 1
                if n2 <= servidores2:
                    if rng.count < limite_aleatorios:
                        ts2 = U(at2_min, at2_max, rng.next())
                        heapq.heappush(eventos, (t + ts2, 'SAIDA_2', 2))
            else:
                perdas2 += 1

        elif tipo == 'SAIDA_2':
            n2 -= 1
            if n2 >= servidores2:
                if rng.count < limite_aleatorios:
                    ts2 = U(at2_min, at2_max, rng.next())
                    heapq.heappush(eventos, (t + ts2, 'SAIDA_2', 2))

        if rng.count >= limite_aleatorios:
            parar = True

    total1 = sum(tempos1.values())
    total2 = sum(tempos2.values())

    return {
        'aleatorios': rng.count,
        'tempo_global': ultimo_t,
        'fila1': {'tempos': tempos1, 'total': total1, 'perdas': perdas1, 'cap': capacidade1},
        'fila2': {'tempos': tempos2, 'total': total2, 'perdas': perdas2, 'cap': capacidade2}
    }

def exibir_relatorio(res):
    print("=" * 65)
    print(" RELATÓRIO DA SIMULAÇÃO - FILAS EM TANDEM (PARTE 2)")
    print("=" * 65)
    print(f"Total de números aleatórios utilizados : {res['aleatorios']}")
    print(f"Tempo global da simulação             : {res['tempo_global']:.4f}")
    print()

    for nome_fila, dados in [("Fila 1 (G/G/2/3)", res['fila1']), ("Fila 2 (G/G/1/5)", res['fila2'])]:
        print(f"*********************************************************")
        print(f" Queue: {nome_fila}")
        print(f" Number of losses: {dados['perdas']}")
        print(f"*********************************************************")
        print(f"   State              Time               Probability")
        
        total = dados['total']
        for i in range(dados['cap'] + 1):
            ti = dados['tempos'][i]
            pi = (ti / total) * 100 if total > 0 else 0
            print(f"   {i:>5}   {ti:>18.4f}   {pi:>17.2f}%")
        print("-" * 57)
        
        # Cálculo da população média (L)
        L = sum(i * (dados['tempos'][i] / total) for i in range(dados['cap'] + 1)) if total > 0 else 0
        print(f" População média (L) = {L:.4f}")
        print("=" * 57)
        print()

if __name__ == '__main__':
    resultado = simular_tandem(seed=12345, limite_aleatorios=100000)
    exibir_relatorio(resultado)
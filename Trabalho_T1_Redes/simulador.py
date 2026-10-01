"""
Simulador de Rede de Filas com Roteamento (Generalizado)
T1 | Avaliação de Aprendizagem
"""
import heapq
import yaml
from collections import defaultdict

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

def carregar_modelo(arquivo):
    with open(arquivo, 'r', encoding='utf-8') as f:
        dados = yaml.safe_load(f)
    
    for fila_id, config in dados['filas'].items():
        if config.get('capacidade') == 'infinito':
            config['capacidade'] = float('inf')
            
        prob_acumulada = 0.0
        rot_acumulado = []
        for rot in config['roteamento']:
            prob_acumulada += rot['probabilidade']
            if abs(prob_acumulada - 1.0) < 1e-6:
                prob_acumulada = 1.0
            rot_acumulado.append((prob_acumulada, rot['destino']))
        config['roteamento_acumulado'] = rot_acumulado
        
    return dados

def simular_rede(modelo, seed=12345, limite_aleatorios=100000):
    rng = LCG(seed)
    filas = modelo['filas']

    t = 0.0
    estado = {f: 0 for f in filas.keys()}
    perdas = {f: 0 for f in filas.keys()}
    tempos = {f: defaultdict(float) for f in filas.keys()}
    
    eventos = []
    event_id = 0 
    
    def agendar(tempo, tipo, fila):
        nonlocal event_id
        heapq.heappush(eventos, (tempo, event_id, tipo, fila))
        event_id += 1

    # Início da simulação com o primeiro cliente na Fila 1
    agendar(modelo['chegada_inicial'], 'CHEGADA_EXT', 1)
    
    while eventos and rng.count < limite_aleatorios:
        tempo_prox, _, tipo, fila = heapq.heappop(eventos)
        
        delta = tempo_prox - t
        if delta > 0:
            for f in filas.keys():
                tempos[f][estado[f]] += delta
            t = tempo_prox

        if tipo == 'CHEGADA_EXT':
            if rng.count < limite_aleatorios:
                tec = U(filas[fila]['chegadas'][0], filas[fila]['chegadas'][1], rng.next())
                agendar(t + tec, 'CHEGADA_EXT', fila)
            
            if estado[fila] < filas[fila]['capacidade']:
                estado[fila] += 1
                if estado[fila] <= filas[fila]['servidores']:
                    if rng.count < limite_aleatorios:
                        ts = U(filas[fila]['atendimento'][0], filas[fila]['atendimento'][1], rng.next())
                        agendar(t + ts, 'SAIDA', fila)
            else:
                perdas[fila] += 1

        elif tipo == 'CHEGADA_INT':
            if estado[fila] < filas[fila]['capacidade']:
                estado[fila] += 1
                if estado[fila] <= filas[fila]['servidores']:
                    if rng.count < limite_aleatorios:
                        ts = U(filas[fila]['atendimento'][0], filas[fila]['atendimento'][1], rng.next())
                        agendar(t + ts, 'SAIDA', fila)
            else:
                perdas[fila] += 1

        elif tipo == 'SAIDA':
            estado[fila] -= 1
            
            if estado[fila] >= filas[fila]['servidores']:
                if rng.count < limite_aleatorios:
                    ts = U(filas[fila]['atendimento'][0], filas[fila]['atendimento'][1], rng.next())
                    agendar(t + ts, 'SAIDA', fila)
                    
            if rng.count < limite_aleatorios:
                r = rng.next()
                destino = 0
                for prob, dest in filas[fila]['roteamento_acumulado']:
                    if r <= prob:
                        destino = dest
                        break
                
                if destino != 0:
                    agendar(t, 'CHEGADA_INT', destino)
                    
    return t, tempos, perdas, rng.count

def exibir_relatorio(t_final, tempos, perdas, cont_aleatorios):
    print("=" * 65)
    print(" RELATÓRIO DA SIMULAÇÃO - REDE DE FILAS (T1)")
    print("=" * 65)
    print(f"Total de números aleatórios utilizados : {cont_aleatorios}")
    print(f"Tempo total de simulação               : {t_final:.4f}\n")

    titulos = {
        1: "Fila 1: G/G/1, chegadas entre 2..4, atendimento entre 1..2",
        2: "Fila 2: G/G/2/5, atendimento entre 4..6",
        3: "Fila 3: G/G/2/10, atendimento entre 5..15"
    }

    for fila_id in sorted(tempos.keys()):
        dados_tempos = tempos[fila_id]
        total = sum(dados_tempos.values())
        
        print(f"Resultado da {titulos[fila_id]}:")
        print(f"Número de perdas: {perdas[fila_id]}")
        print(f"  Estado              Tempo        Probabilidade")
        
        L = 0
        for est in sorted(dados_tempos.keys()):
            ti = dados_tempos[est]
            pi = (ti / total) * 100 if total > 0 else 0
            L += est * (ti / total)
            print(f"  {est:>5}   {ti:>15.4f}   {pi:>16.2f}%")
            
        print(f"População média (L) = {L:.4f}")
        print("-" * 57, "\n")

if __name__ == '__main__':
    modelo_carregado = carregar_modelo('modelo.yml')
    t_final, tempos, perdas, cont_aleatorios = simular_rede(modelo_carregado, seed=12345, limite_aleatorios=100000)
    exibir_relatorio(t_final, tempos, perdas, cont_aleatorios)
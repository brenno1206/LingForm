"""
Módulo responsável pela geração gráfica de grafos dos Autômatos,
utilizando a biblioteca Graphviz para renderização vetorial focada em grafos.
"""

import graphviz

def desenhar_grafo_graphviz(transicoes: list[tuple], estados: list[str], inicial: str, finais: list[str]) -> graphviz.Digraph:
    """
    Constrói a imagem vetorial de um autômato direcionado usando o Graphviz.
    Formata visualmente autoloops, estados iniciais e círculos duplos de estados finais.

    Args:
        transicoes (list[tuple]): Lista de tuplas contendo (origem, símbolo, destino).
        estados (list[str]): Lista com o nome de todos os estados gerados/existentes.
        inicial (str): Nome do estado inicial.
        finais (list[str]): Lista contendo os nomes dos estados finais.

    Returns:
        graphviz.Digraph: O objeto do grafo montado e pronto para renderização no Streamlit.
    """
    dot = graphviz.Digraph(engine='dot')
    # O layout rankdir='LR' projeta o fluxo principal sempre da Esquerda para a Direita
    dot.attr(rankdir='LR', size='8,5')

    # Agrupa múltiplas transições entre dois estados na mesma seta (Ex: a seta "0, 1")
    arestas_agrupadas = {}
    for origem, simbolo, destino in transicoes:
        if (origem, destino) not in arestas_agrupadas:
            arestas_agrupadas[(origem, destino)] = []
        arestas_agrupadas[(origem, destino)].append(simbolo)

    # Renderiza os estados visuais
    for estado in estados:
        # 'doublecircle' forma nativamente os dois anéis dos estados de aceitação
        shape = 'doublecircle' if estado in finais else 'circle'
        label = f">{estado}" if estado == inicial else str(estado)
        cor = '#ffcccb' if estado == "Ratoeira" else '#F5F5DC' # Vermelho p/ ratoeira, Bege p/ o resto
        
        dot.node(str(estado), label=label, shape=shape, style='filled', fillcolor=cor, fontname="Helvetica-Bold")

    # Renderiza as conexões (setas)
    for (origem, destino), simbolos in arestas_agrupadas.items():
        label = ", ".join(sorted(simbolos))
        dot.edge(str(origem), str(destino), label=label, fontcolor='red', fontname="Helvetica-Bold")

    return dot

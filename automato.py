"""
Módulo responsável pela estrutura de dados e algoritmos de Autômatos Finitos.
Contém a lógica de leitura, conversão de AFND para AFD, testes de palavras e exportação.
"""

class Automato:
    """
    Classe que representa e manipula um Autômato Finito.
    Recebe as linhas de um arquivo de texto, constrói o AFND original,
    e automaticamente gera o AFD equivalente completo.
    """

    def __init__(self, linhas_arquivo: list[str]):
        """
        Inicializa o Autômato.
        
        Args:
            linhas_arquivo (list[str]): Lista contendo as linhas do arquivo .txt com a tabela do AFND.
        """
        # 1. Pega os dados das linhas e constrói o AFND
        self.AFND_estados, self.estado_inicial, self.AFND_estados_finais, self.AFND = self._pegar_AFND(linhas_arquivo)
        
        # 2. Converte o AFND para AFD rigorosamente sob o alfabeto {0, 1}
        self.AFD_estados, self.AFD_transicoes, self.AFD_estados_finais = self._AFND_para_AFD()

    def _pegar_AFND(self, lines: list[str]) -> tuple:
        """
        Faz o parse (leitura) das linhas do arquivo e estrutura o AFND.
        
        Args:
            lines (list[str]): Linhas puras do arquivo texto.
            
        Returns:
            tuple: Contém (lista de estados, estado inicial, lista de estados finais, lista de transições).
        """
        # Remove espaços em branco extras e linhas vazias
        lines = [line.strip() for line in lines if line.strip()]

        estados = lines[0].split()
        estado_inicial = lines[1].strip()
        estados_finais = lines[2].split()

        afnd = []
        # A partir da linha 3, extrai a regra (estado_atual, simbolo_lido, estado_destino)
        for line in lines[3:]:
            atual, simbolo, destino = line.split()
            afnd.append((atual, simbolo, destino))

        # Ordena para manter previsibilidade no processamento
        afnd.sort(key=lambda x: (x[0], x[1], x[2]))
        
        return (estados, estado_inicial, estados_finais, afnd)

    def _epsilon_fecho(self, estados: set) -> set:
        """
        Calcula o fecho-epsilon de um conjunto de estados.
        O fecho-epsilon engloba todos os estados alcançáveis consumindo 
        apenas a palavra vazia ('h'), incluindo os próprios estados iniciais.
        
        Args:
            estados (set): Conjunto de estados de origem.
            
        Returns:
            set: Novo conjunto contendo os estados expandidos com transições vazias.
        """
        fecho = set(estados)
        pilha = list(estados)
        
        # Busca em profundidade (DFS) para encontrar todos os caminhos com 'h'
        while pilha:
            estado_atual = pilha.pop()
            for transicao in self.AFND:
                # 'h' representa o movimento vazio
                if transicao[0] == estado_atual and transicao[1] == 'h':
                    if transicao[2] not in fecho:
                        fecho.add(transicao[2])
                        pilha.append(transicao[2])
        return fecho

    def testar_AFND(self, palavra: str) -> bool:
        """
        Verifica se uma palavra é aceita pelo AFND original (com caminhos múltiplos e vazios).
        
        Args:
            palavra (str): A palavra a ser testada (ex: "010").
            
        Returns:
            bool: True se a palavra for aceita, False caso contrário.
        """
        # Se a palavra recebida for 'h', significa palavra vazia (nenhum símbolo lido)
        if palavra == 'h':
            palavra = ''

        # Estado inicial engloba o fecho-epsilon
        estados_atuais = self._epsilon_fecho({self.estado_inicial})

        for simbolo in palavra:
            proximos_estados = set()
            for estado in estados_atuais:
                for transicao in self.AFND:
                    if transicao[0] == estado and transicao[1] == simbolo:
                        proximos_estados.add(transicao[2])
            
            # Aplica o fecho-epsilon aos destinos alcançados
            estados_atuais = self._epsilon_fecho(proximos_estados)
            
            # Se não há mais caminhos possíveis, falha cedo (early exit)
            if not estados_atuais:
                break

        # Verifica se algum dos ramos parou em um estado de aceitação
        for estado in estados_atuais:
            if estado in self.AFND_estados_finais:
                return True
        return False

    def _AFND_para_AFD(self) -> tuple:
        """
        Aplica o Algoritmo de Construção de Subconjuntos para converter o AFND
        em um AFD determinístico completo. O processo agrupa estados e resolve 
        transições vazias.
        
        Returns:
            tuple: Contém (lista de estados do AFD, transições geradas, estados finais do AFD).
        """
        # O alfabeto é rigorosamente fixado conforme exigência do trabalho
        alfabeto = {'0', '1'}
        
        # O estado inicial do AFD é a fusão de tudo alcançável por 'h' da origem
        estado_inicial_set = self._epsilon_fecho({self.estado_inicial})
        nome_estado_inicial = ",".join(sorted(list(estado_inicial_set))) if estado_inicial_set else "Vazio"
        
        estados_afd = [nome_estado_inicial]
        transicoes_afd = []
        estados_finais_afd = []
        
        fila = [estado_inicial_set]
        estados_processados = set()

        # --- ETAPA 1: CONSTRUÇÃO DOS SUBCONJUNTOS ---
        while fila:
            atual_set = fila.pop(0)
            atual_nome = ",".join(sorted(list(atual_set)))
            estados_processados.add(atual_nome)
            
            # Se qualquer sub-estado contido aqui for final no AFND, este super-estado é final no AFD
            if any(sub in self.AFND_estados_finais for sub in atual_set):
                if atual_nome not in estados_finais_afd:
                    estados_finais_afd.append(atual_nome)

            # Avalia as transições para '0' e para '1'
            for simbolo in alfabeto:
                destinos_diretos = set()
                for sub_estado in atual_set:
                    for transicao in self.AFND:
                        if transicao[0] == sub_estado and transicao[1] == simbolo:
                            destinos_diretos.add(transicao[2])
                
                # Se esse símbolo gerou algum destino válido
                if destinos_diretos:
                    # Aplica o fecho-epsilon no destino e une os nomes
                    proximos_estados_set = self._epsilon_fecho(destinos_diretos)
                    proximo_nome = ",".join(sorted(list(proximos_estados_set)))
                    
                    transicoes_afd.append((atual_nome, simbolo, proximo_nome))
                    
                    # Enfileira novo estado composto se for inédito
                    if proximo_nome not in estados_processados and proximo_nome not in [",".join(sorted(list(x))) for x in fila]:
                        fila.append(proximos_estados_set)
                        if proximo_nome not in estados_afd:
                            estados_afd.append(proximo_nome)

        # --- ETAPA 2: COMPLETUDE DO AFD (ESTADO RATOEIRA) ---
        precisa_ratoeira = False
        transicoes_existentes_por_estado = {}
        
        # Mapeia as transições ativas que cada estado recém-criado já possui
        for origem, simbolo, _ in transicoes_afd:
            if origem not in transicoes_existentes_por_estado:
                transicoes_existentes_por_estado[origem] = set()
            transicoes_existentes_por_estado[origem].add(simbolo)

        # Para todo estado do AFD, se faltar caminho para '0' ou '1', redireciona para a "Ratoeira"
        for estado in estados_afd:
            simbolos_presentes = transicoes_existentes_por_estado.get(estado, set())
            simbolos_faltantes = alfabeto - simbolos_presentes
            
            for simbolo_faltante in simbolos_faltantes:
                transicoes_afd.append((estado, simbolo_faltante, "Ratoeira"))
                precisa_ratoeira = True

        # Criação física do estado "Ratoeira" com autoloop em todo o alfabeto
        if precisa_ratoeira:
            estados_afd.append("Ratoeira")
            for simbolo in alfabeto:
                transicoes_afd.append(("Ratoeira", simbolo, "Ratoeira"))

        return (estados_afd, transicoes_afd, estados_finais_afd)

    def testar_AFD(self, palavra: str) -> bool:
        """
        Testa se uma palavra é aceita pelo AFD perfeitamente determinístico.
        
        Args:
            palavra (str): A palavra a ser testada.
            
        Returns:
            bool: True se a palavra for aceita e o autômato parar em estado final.
        """
        # Se a palavra recebida for 'h', significa palavra vazia (nenhum símbolo lido)
        if palavra == 'h':
            palavra = ''

        estado_atual = self.AFD_estados[0]

        for simbolo in palavra:
            for transicao in self.AFD_transicoes:
                if transicao[0] == estado_atual and transicao[1] == simbolo:
                    estado_atual = transicao[2]
                    break
            else:
                # Cai no "else" do for se o loop não for quebrado com 'break'
                return False
        
        # Após ler toda a palavra, o estado final tem que ser de aceitação
        return estado_atual in self.AFD_estados_finais

    def exportar_AFD_txt(self) -> str:
        """
        Gera a string estruturada que representa o AFD no exato mesmo formato do arquivo .txt de entrada.
        
        Returns:
            str: O conteúdo em formato texto pronto para ser gravado e baixado.
        """
        linhas = []
        
        # Linha 0: Todos os estados separados por espaço
        linhas.append(" ".join(self.AFD_estados))
        
        # Linha 1: Estado inicial (é sempre o primeiro da lista no nosso algoritmo)
        linhas.append(self.AFD_estados[0])
        
        # Linha 2: Estados finais separados por espaço
        linhas.append(" ".join(self.AFD_estados_finais))
        
        # Linha 3 em diante: As regras de transição (origem simbolo destino)
        for origem, simbolo, destino in self.AFD_transicoes:
            linhas.append(f"{origem} {simbolo} {destino}")
            
        return "\n".join(linhas)

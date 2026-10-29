"""
Automatos finitos: leitura de um AFND (com movimentos vazios 'h'),
conversao para AFD equivalente (construcao de subconjuntos) e teste de palavras.

Convencoes do trabalho:
  - estados sao letras maiusculas;
  - 'h' representa a palavra vazia (movimento vazio / palavra vazia);
  - o nome de um estado do AFD e a concatenacao, em ordem crescente, das letras
    dos estados do AFND que ele agrupa (ex.: ABF, ABCDF).
"""

VAZIO = "h"


def nome_estado(conjunto) -> str:
    """Nome canonico de um conjunto de estados: letras em ordem crescente."""
    return "".join(sorted(conjunto))


class Automato:
    """Le um AFND e gera automaticamente o AFD equivalente."""

    def __init__(self, linhas: list[str]):
        self._ler_afnd(linhas)
        self._afnd_para_afd()

    # ------------------------------------------------------------------ leitura
    def _ler_afnd(self, linhas: list[str]) -> None:
        """
        Formato:
          linha 1: estados separados por espaco
          linha 2: estado inicial
          linha 3: estados finais separados por espaco
          linha 4+: transicoes 'origem simbolo destino'
        """
        linhas = [l.strip() for l in linhas]
        while linhas and not linhas[0]:          # ignora linhas em branco iniciais
            linhas.pop(0)
        if len(linhas) < 3:
            raise ValueError("arquivo do AFND precisa ter ao menos 3 linhas")

        self.estados = linhas[0].split()
        self.inicial = linhas[1]
        self.finais = set(linhas[2].split())

        # transicoes: (origem, simbolo) -> conjunto de destinos
        self.delta: dict[tuple[str, str], set[str]] = {}
        simbolos = set()
        for linha in linhas[3:]:
            if not linha:
                continue
            origem, simbolo, destino = linha.split()
            self.delta.setdefault((origem, simbolo), set()).add(destino)
            if simbolo != VAZIO:
                simbolos.add(simbolo)

        # o alfabeto e deduzido das transicoes (sem o 'h')
        self.alfabeto = sorted(simbolos)

    # --------------------------------------------------------------- operacoes
    def _fecho_vazio(self, estados) -> frozenset:
        """Todos os estados alcancaveis a partir de 'estados' usando so 'h'."""
        fecho = set(estados)
        pilha = list(estados)
        while pilha:
            e = pilha.pop()
            for d in self.delta.get((e, VAZIO), ()):
                if d not in fecho:
                    fecho.add(d)
                    pilha.append(d)
        return frozenset(fecho)

    def _mover(self, estados, simbolo) -> frozenset:
        """Estados alcancados lendo 'simbolo' (ja aplicando o fecho vazio)."""
        destinos = set()
        for e in estados:
            destinos |= self.delta.get((e, simbolo), set())
        return self._fecho_vazio(destinos)

    # --------------------------------------------------------------- AFND -> AFD
    def _afnd_para_afd(self) -> None:
        """Construcao de subconjuntos. Subconjunto vazio nao vira estado
        (transicoes para ele simplesmente nao existem no AFD gerado)."""
        inicio = self._fecho_vazio({self.inicial})
        self.afd_inicial = nome_estado(inicio)

        nomes = {self.afd_inicial: inicio}      # nome -> conjunto
        self.afd_delta: dict[tuple[str, str], str] = {}
        fila = [inicio]

        while fila:
            atual = fila.pop(0)
            nome_atual = nome_estado(atual)
            for simbolo in self.alfabeto:
                destino = self._mover(atual, simbolo)
                if not destino:
                    continue
                nome_destino = nome_estado(destino)
                self.afd_delta[(nome_atual, simbolo)] = nome_destino
                if nome_destino not in nomes:
                    nomes[nome_destino] = destino
                    fila.append(destino)

        self.afd_estados = sorted(nomes)
        self.afd_finais = sorted(n for n, c in nomes.items() if c & self.finais)

    # ------------------------------------------------------------------- testes
    @staticmethod
    def _normalizar(palavra: str) -> str:
        """'h' representa a palavra vazia, entao nao e simbolo de leitura."""
        return palavra.replace(VAZIO, "")

    def aceita_afnd(self, palavra: str) -> bool:
        """Simulacao direta do AFND (usada para conferir o AFD)."""
        atuais = self._fecho_vazio({self.inicial})
        for simbolo in self._normalizar(palavra):
            atuais = self._mover(atuais, simbolo)
            if not atuais:
                return False
        return bool(atuais & self.finais)

    def aceita_afd(self, palavra: str) -> bool:
        """Executa a palavra no AFD equivalente."""
        estado = self.afd_inicial
        for simbolo in self._normalizar(palavra):
            estado = self.afd_delta.get((estado, simbolo))
            if estado is None:
                return False
        return estado in self.afd_finais

    # ----------------------------------------------------------------- exportar
    def exportar_afd(self) -> str:
        """AFD no mesmo formato do arquivo de entrada (saida_1)."""
        linhas = [
            " ".join(self.afd_estados),
            self.afd_inicial,
            " ".join(self.afd_finais),
        ]
        for (origem, simbolo), destino in sorted(self.afd_delta.items()):
            linhas.append(f"{origem} {simbolo} {destino}")
        return "\n".join(linhas) + "\n"

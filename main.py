"""
Converte um AFND (com movimentos vazios) em AFD equivalente e testa palavras.

Uso:
    python main.py [entrada_1] [entrada_2] [saida_1] [saida_2]

Padrao (sem argumentos): le entrada_1.txt e entrada_2.txt e grava
saida_1.txt (AFD equivalente) e saida_2.txt (aceita/rejeita por palavra).
Os arquivos sao procurados na pasta atual e, se nao estiverem la, na pasta do script.
"""

import os
import sys

from automato import Automato

AQUI = os.path.dirname(os.path.abspath(__file__))


def caminho_entrada(nome: str) -> str:
    """Pasta atual primeiro; senao a pasta do script (ou da subpasta de arquivos)."""
    for base in (os.getcwd(), AQUI, os.path.join(AQUI, "arquivos_de_entrada_e_saida")):
        p = os.path.join(base, nome)
        if os.path.isfile(p):
            return p
    raise FileNotFoundError(f"arquivo nao encontrado: {nome}")


def ler_linhas(caminho: str) -> list[str]:
    with open(caminho, encoding="utf-8-sig") as f:
        return f.read().splitlines()


def main() -> None:
    args = sys.argv[1:]
    ent1 = args[0] if len(args) > 0 else "entrada_1.txt"
    ent2 = args[1] if len(args) > 1 else "entrada_2.txt"
    sai1 = args[2] if len(args) > 2 else "saida_1.txt"
    sai2 = args[3] if len(args) > 3 else "saida_2.txt"

    ent1 = ent1 if os.path.isfile(ent1) else caminho_entrada(ent1)
    ent2 = ent2 if os.path.isfile(ent2) else caminho_entrada(ent2)

    # saidas ficam ao lado das entradas, a menos que o caminho tenha sido informado
    if len(args) < 3:
        sai1 = os.path.join(os.path.dirname(ent1), sai1)
    if len(args) < 4:
        sai2 = os.path.join(os.path.dirname(ent2), sai2)

    auto = Automato(ler_linhas(ent1))

    with open(sai1, "w", encoding="utf-8", newline="") as f:
        f.write(auto.exportar_afd())

    saida = []
    for linha in ler_linhas(ent2):
        palavra = linha.strip()
        if not palavra:
            continue
        saida.append(f"{palavra}\t{'aceita' if auto.aceita_afd(palavra) else 'rejeita'}")
    with open(sai2, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(saida) + "\n")


if __name__ == "__main__":
    main()

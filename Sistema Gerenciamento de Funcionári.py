# Sistema de Gerenciamento de Funcionários por Setor
# Objetivo: Controlar funcionários, permitindo cadastro por setor,
# listagem, busca por nome e cálculo da média salarial.
#
# Entradas: Nome, cargo, setor e salário.
# Saídas: Lista de funcionários, busca por nome e média salarial.

import json
import os
from pathlib import Path

DATA_FILE = Path(__file__).parent / "funcionarios.json"


def carregar_dados():
    """
    Carrega lista de funcionários do arquivo JSON.
    Retorna lista vazia se o arquivo não existir ou estiver inválido.
    """
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # garante que cada salário seja float (caso tenha sido salvo como string)
            for item in data:
                item["salario"] = float(item.get("salario", 0))
            return data
    except Exception:
        return []


def salvar_dados(lista):
    """
    Salva lista de funcionários em JSON.
    """
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(lista, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erro ao salvar dados: {e}")


def parse_salario(salario_str):
    """
    Converte strings de salário em float aceitando formatos:
    - "8.200,00" -> remove '.' como separador de milhares e ',' como decimal
    - "2500,50" -> ',' decimal
    - "2500.50" -> '.' decimal
    - pode conter "R$" e espaços
    Retorna float ou lança ValueError se inválido.
    """
    s = salario_str.strip().replace("R$", "").replace(" ", "")
    # Se contém ambos '.' e ',', assume que '.' é separador de milhares e ',' decimal
    if "." in s and "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        # apenas vírgula -> vírgula é decimal
        if "," in s and "." not in s:
            s = s.replace(",", ".")
        # apenas ponto -> mantém (ponto decimal)
        # nenhum separador -> mantém
    return float(s)


def adicionar_funcionario(lista):
    """
    Função: adiciona um funcionário à lista e salva os dados.
    Entrada: lista (list) de dicionários.
    Processo: solicita nome, cargo, setor e salário e armazena.
    Saída: atualiza lista e arquivo.
    """
    nome = input("Nome do funcionário: ").strip()
    if not nome:
        print("Nome não pode ser vazio.\n")
        return

    cargo = input("Cargo: ").strip()
    setor = input("Setor: ").strip()
    salario_str = input("Salário (ex.: 8.200,00 ou 2500.50): ").strip()

    try:
        salario = parse_salario(salario_str)
    except ValueError:
        print("Erro: salário inválido. Use apenas números, exemplo: 8.200,00 ou 2500.50.\n")
        return

    funcionario = {
        "nome": nome,
        "cargo": cargo,
        "setor": setor,
        "salario": salario
    }
    lista.append(funcionario)
    salvar_dados(lista)
    print(f"\nFuncionário {nome} adicionado com sucesso ao setor {setor}.\n")


def listar_funcionarios(lista):
    """
    Função: exibe todos os funcionários cadastrados.
    """
    if not lista:
        print("Nenhum funcionário cadastrado.\n")
        return

    print("\n--- Lista de Funcionários ---")
    for i, f in enumerate(lista, start=1):
        print(f"{i}. Nome: {f['nome']} | Cargo: {f['cargo']} | Setor: {f['setor']} | Salário: R$ {f['salario']:.2f}")
    print()


def buscar_funcionario(lista):
    """
    Função: busca funcionário por nome (case-insensitive).
    """
    nome_busca = input("Digite o nome do funcionário para buscar: ")
    encontrados = [f for f in lista if f["nome"].strip().lower() == nome_busca.strip().lower()]

    if encontrados:
        print("\nFuncionário(s) encontrado(s):")
        for f in encontrados:
            print(f"Nome: {f['nome']} | Cargo: {f['cargo']} | Setor: {f['setor']} | Salário: R$ {f['salario']:.2f}")
    else:
        print("Funcionário não encontrado.\n")


def calcular_media_salarial(lista):
    """
    Função: calcula média salarial de todos os funcionários.
    """
    if not lista:
        print("Nenhum funcionário cadastrado para cálculo.\n")
        return
    total = sum(f["salario"] for f in lista)
    media = total / len(lista)
    print(f"\nMédia salarial dos funcionários: R$ {media:.2f}\n")


def main():
    """
    Função principal: exibe o menu e chama as funções correspondentes.
    """
    funcionarios = carregar_dados()
    opcao = ""

    while opcao != "5":
        print("=== Sistema de Funcionários por Setor ===")
        print("1 - Adicionar funcionário")
        print("2 - Listar funcionários")
        print("3 - Buscar funcionário por nome")
        print("4 - Calcular média salarial")
        print("5 - Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            adicionar_funcionario(funcionarios)
        if opcao == "2":
            listar_funcionarios(funcionarios)
        if opcao == "3":
            buscar_funcionario(funcionarios)
        if opcao == "4":
            calcular_media_salarial(funcionarios)
        if opcao == "5":
            print("Encerrando o programa.\n")
        if opcao not in ["1", "2", "3", "4", "5"]:
            print("Opção inválida. Tente novamente.\n")


# Execução principal
if __name__ == "__main__":
    main()

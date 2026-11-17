
import json
import os
import re
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
    except (json.JSONDecodeError, TypeError, ValueError, AttributeError) as e:
        # Não descarta o arquivo: o próximo salvamento o sobrescreveria e todos
        # os cadastros seriam perdidos. Guarda uma cópia antes de recomeçar.
        backup = DATA_FILE.with_suffix(".json.corrompido")
        DATA_FILE.replace(backup)
        print(f"Aviso: {DATA_FILE.name} estava inválido ({e}). Uma cópia foi salva em {backup.name}.\n")
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
    Converte strings de salário em float aceitando os formatos brasileiro e americano:
    - "8.200,00" e "8,200.00" -> 8200.0 (o último separador é o decimal)
    - "8.200" e "1.234.567"   -> milhares (grupos de 3 dígitos depois do ponto)
    - "2500,50" e "2500.50"   -> decimal
    - pode conter "R$" e espaços
    Retorna float ou lança ValueError se inválido.
    """
    s = salario_str.strip().replace("R$", "").replace(" ", "")
    if "." in s and "," in s:
        # O separador que aparece por último é o decimal.
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        # "1,234,567" é milhar; "2500,50" é decimal.
        s = s.replace(",", "") if re.fullmatch(r"\d{1,3}(,\d{3}){2,}", s) else s.replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(\.\d{3})+", s):
        # "8.200" e "1.234.567": ponto como separador de milhar.
        s = s.replace(".", "")
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
    if salario <= 0:
        print("Erro: o salário precisa ser maior que zero.\n")
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
    Função: busca funcionário por parte do nome (sem diferenciar maiúsculas).
    """
    nome_busca = input("Digite o nome do funcionário para buscar: ")
    termo = nome_busca.strip().lower()
    if not termo:
        print("Digite ao menos uma letra do nome.\n")
        return
    # Busca parcial: "ana" encontra "Ana Souza" e "Mariana".
    encontrados = [f for f in lista if termo in f["nome"].strip().lower()]

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


def resumo_por_setor(lista):
    """
    Função: agrupa os funcionários por setor e devolve
    [(setor, quantidade, média salarial)], em ordem alfabética de setor.
    Setores que só diferem em maiúsculas ("TI" e "ti") contam como um só, com o
    nome da primeira grafia encontrada. Setor em branco aparece como "Sem setor".
    """
    grupos = {}
    for f in lista:
        setor = f.get("setor", "").strip() or "Sem setor"
        nome, salarios = grupos.setdefault(setor.lower(), (setor, []))
        salarios.append(f["salario"])
    return [(nome, len(s), sum(s) / len(s)) for _, (nome, s) in sorted(grupos.items())]


def exibir_resumo_por_setor(lista):
    """
    Função: mostra quantidade de funcionários e média salarial de cada setor.
    """
    if not lista:
        print("Nenhum funcionário cadastrado.\n")
        return
    print("\n--- Resumo por setor ---")
    for setor, quantidade, media in resumo_por_setor(lista):
        print(f"{setor}: {quantidade} funcionário(s) | média R$ {media:.2f}")
    print()


def escolher_funcionario(lista, acao):
    """
    Mostra a lista numerada e devolve o índice escolhido (0-based), ou None.
    """
    if not lista:
        print("Nenhum funcionário cadastrado.\n")
        return None
    listar_funcionarios(lista)
    escolha = input(f"Número do funcionário para {acao} (Enter para voltar): ").strip()
    if not escolha:
        return None
    if not escolha.isdigit() or not 1 <= int(escolha) <= len(lista):
        print("Número inválido.\n")
        return None
    return int(escolha) - 1


def remover_funcionario(lista):
    """
    Função: remove um funcionário escolhido pelo número da listagem, após confirmação.
    """
    indice = escolher_funcionario(lista, "remover")
    if indice is None:
        return
    nome = lista[indice]["nome"]
    if input(f"Remover {nome}? (s/n): ").strip().lower() != "s":
        print("Remoção cancelada.\n")
        return
    lista.pop(indice)
    salvar_dados(lista)
    print(f"{nome} removido(a).\n")


def editar_funcionario(lista):
    """
    Função: edita um funcionário escolhido pelo número da listagem.
    Enter em branco mantém o valor atual de cada campo.
    """
    indice = escolher_funcionario(lista, "editar")
    if indice is None:
        return
    atual = lista[indice]
    print("Enter mantém o valor atual.")
    novo = dict(atual)
    for campo, rotulo in (("nome", "Nome"), ("cargo", "Cargo"), ("setor", "Setor")):
        valor = input(f"{rotulo} [{atual[campo]}]: ").strip()
        if valor:
            novo[campo] = valor
    salario_str = input(f"Salário [{atual['salario']:.2f}]: ").strip()
    if salario_str:
        try:
            salario = parse_salario(salario_str)
        except ValueError:
            print("Erro: salário inválido. Nada foi alterado.\n")
            return
        if salario <= 0:
            print("Erro: o salário precisa ser maior que zero. Nada foi alterado.\n")
            return
        novo["salario"] = salario
    lista[indice] = novo
    salvar_dados(lista)
    print(f"{novo['nome']} atualizado(a).\n")


OPCOES = [
    ("1", "Adicionar funcionário", adicionar_funcionario),
    ("2", "Listar funcionários", listar_funcionarios),
    ("3", "Buscar funcionário por nome", buscar_funcionario),
    ("4", "Calcular média salarial", calcular_media_salarial),
    ("5", "Remover funcionário", remover_funcionario),
    ("6", "Editar funcionário", editar_funcionario),
    ("7", "Resumo por setor", exibir_resumo_por_setor),
]


def main():
    """
    Função principal: exibe o menu e chama as funções correspondentes.
    """
    funcionarios = carregar_dados()
    acoes = {codigo: funcao for codigo, _, funcao in OPCOES}

    while True:
        print("=== Sistema de Funcionários por Setor ===")
        for codigo, rotulo, _ in OPCOES:
            print(f"{codigo} - {rotulo}")
        print("0 - Sair")

        opcao = input("Escolha uma opção: ").strip()
        if opcao == "0":
            print("Encerrando o programa.\n")
            break
        if opcao in acoes:
            acoes[opcao](funcionarios)
        else:
            print("Opção inválida. Tente novamente.\n")


# Execução principal
if __name__ == "__main__":
    main()

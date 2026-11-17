# Sistema de Gerenciamento de Funcionários

Programa em Python para registrar e organizar os funcionários de uma empresa: nome, cargo, setor e salário, com listagem, busca e média salarial. Os dados ficam salvos num arquivo JSON entre as execuções.

## Funcionalidades

| Menu | O que faz |
|---|---|
| 1. Adicionar funcionário | Cadastra nome, cargo, setor e salário |
| 2. Listar funcionários | Mostra todos os cadastrados |
| 3. Buscar por nome | Busca por parte do nome, sem diferenciar maiúsculas ("ana" encontra "Ana Souza" e "Mariana") |
| 4. Média salarial | Calcula a média dos salários |

O salário aceita os formatos brasileiro e americano: `8.200,00`, `8.200`, `8,200.00`, `2500.50` e `R$ 3.000,00`. Valores zerados ou negativos são recusados.

## Como executar

Requer Python 3.8+, sem dependências.

```sh
python funcionarios.py
```

Os cadastros ficam em `funcionarios.json`, na mesma pasta. Se esse arquivo for corrompido, o programa guarda uma cópia em `funcionarios.json.corrompido` e avisa, em vez de sobrescrevê-lo.

## Testes

```sh
pip install pytest
pytest
```

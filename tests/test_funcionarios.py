import json

import pytest

import funcionarios as f


@pytest.fixture(autouse=True)
def arquivo_temporario(tmp_path, monkeypatch):
    """Cada teste grava num funcionarios.json próprio, numa pasta temporária."""
    monkeypatch.setattr(f, "DATA_FILE", tmp_path / "funcionarios.json")


def responder(monkeypatch, *respostas):
    fila = iter(respostas)
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(fila))


@pytest.mark.parametrize("texto, esperado", [
    ("8.200,00", 8200.0),
    ("8.200", 8200.0),
    ("1.234.567", 1234567.0),
    ("8,200.00", 8200.0),
    ("2500,50", 2500.5),
    ("2500.50", 2500.5),
    ("2.50", 2.5),
    ("R$ 3.000,00", 3000.0),
    ("1500", 1500.0),
])
def test_parse_salario(texto, esperado):
    assert f.parse_salario(texto) == esperado


def test_parse_salario_recusa_texto():
    with pytest.raises(ValueError):
        f.parse_salario("mil reais")


def test_adicionar_salva_no_arquivo(monkeypatch):
    lista = []
    responder(monkeypatch, "Ana Souza", "Dev", "TI", "8.200,00")
    f.adicionar_funcionario(lista)
    assert lista == [{"nome": "Ana Souza", "cargo": "Dev", "setor": "TI", "salario": 8200.0}]
    assert f.carregar_dados() == lista


def test_adicionar_recusa_salario_nao_positivo(monkeypatch):
    lista = []
    responder(monkeypatch, "Ana", "Dev", "TI", "-500")
    f.adicionar_funcionario(lista)
    assert lista == []


def test_busca_parcial_sem_diferenciar_maiusculas(monkeypatch, capsys):
    lista = [
        {"nome": "Ana Souza", "cargo": "Dev", "setor": "TI", "salario": 1.0},
        {"nome": "Mariana Lima", "cargo": "RH", "setor": "RH", "salario": 1.0},
        {"nome": "Bruno", "cargo": "Ops", "setor": "TI", "salario": 1.0},
    ]
    responder(monkeypatch, "ANA")
    f.buscar_funcionario(lista)
    saida = capsys.readouterr().out
    assert "Ana Souza" in saida and "Mariana Lima" in saida and "Bruno" not in saida


def test_media_salarial(capsys):
    f.calcular_media_salarial([{"salario": 1000.0}, {"salario": 3000.0}])
    assert "R$ 2000.00" in capsys.readouterr().out


def test_arquivo_corrompido_e_preservado(capsys):
    f.DATA_FILE.write_text('[{"nome": "Ana"', encoding="utf-8")
    assert f.carregar_dados() == []
    backup = f.DATA_FILE.with_suffix(".json.corrompido")
    assert backup.read_text(encoding="utf-8") == '[{"nome": "Ana"'
    assert not f.DATA_FILE.exists()


def test_salario_salvo_como_texto_e_convertido():
    f.DATA_FILE.write_text(json.dumps([{"nome": "Ana", "cargo": "", "setor": "", "salario": "5000"}]), encoding="utf-8")
    assert f.carregar_dados()[0]["salario"] == 5000.0


def lista_exemplo():
    return [
        {"nome": "Ana", "cargo": "Dev", "setor": "TI", "salario": 5000.0},
        {"nome": "Bruno", "cargo": "Analista", "setor": "RH", "salario": 4000.0},
    ]


def test_remover_com_confirmacao(monkeypatch):
    lista = lista_exemplo()
    responder(monkeypatch, "2", "s")
    f.remover_funcionario(lista)
    assert [x["nome"] for x in lista] == ["Ana"]
    assert f.carregar_dados() == lista


def test_remover_cancelado_ou_numero_invalido_nao_altera(monkeypatch):
    lista = lista_exemplo()
    responder(monkeypatch, "1", "n")
    f.remover_funcionario(lista)
    responder(monkeypatch, "9")
    f.remover_funcionario(lista)
    responder(monkeypatch, "abc")
    f.remover_funcionario(lista)
    assert len(lista) == 2


def test_menu_sai_com_zero(monkeypatch, capsys):
    responder(monkeypatch, "7", "0")
    f.main()
    saida = capsys.readouterr().out
    assert "Opção inválida" in saida and "Encerrando" in saida


def test_editar_mantem_campos_em_branco(monkeypatch):
    lista = lista_exemplo()
    responder(monkeypatch, "1", "", "Tech Lead", "", "6.500,00")
    f.editar_funcionario(lista)
    assert lista[0] == {"nome": "Ana", "cargo": "Tech Lead", "setor": "TI", "salario": 6500.0}
    assert f.carregar_dados() == lista


def test_editar_com_salario_invalido_nao_altera_nada(monkeypatch):
    lista = lista_exemplo()
    responder(monkeypatch, "2", "Bruno Lima", "", "", "-1")
    f.editar_funcionario(lista)
    assert lista == lista_exemplo()

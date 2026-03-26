from app.tools.system_tools import obter_ip, obter_hora_atual
from app.tools.file_tools import criar_pasta_desktop, renomear_arquivo


def test_obter_ip_retorna_sucesso():
    result = obter_ip()
    assert result["success"] is True
    assert "ip" in result["data"]
    assert "hostname" in result["data"]


def test_obter_ip_tem_mensagem():
    result = obter_ip()
    assert "IP local" in result["message"]


def test_obter_hora_retorna_sucesso():
    result = obter_hora_atual()
    assert result["success"] is True
    assert result["data"]["formatted"]


def test_obter_hora_formato_portugues():
    result = obter_hora_atual()
    msg = result["message"]
    dias = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
    assert any(dia in msg for dia in dias)
    assert " de " in msg


def test_criar_pasta_nome_vazio():
    result = criar_pasta_desktop("")
    assert result["success"] is False
    assert "vazio" in result["message"]


def test_criar_pasta_nome_invalido():
    result = criar_pasta_desktop("pasta/invalida")
    assert result["success"] is False
    assert "inválidos" in result["message"]


def test_renomear_nome_invalido():
    result = renomear_arquivo("C:/test.txt", "novo:nome.txt")
    assert result["success"] is False

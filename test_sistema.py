import datetime
from biblioteca_legado import Sistema # ajuste para o nome do seu arquivo principal se for diferente


def setup_sistema_base():
    """Fixture auxiliar para inicializar um sistema com dados padronizados."""
    s = Sistema()
    s.adicionar_livro("L1", "Clean Code", "Robert Martin", "tecnico", 2)
    s.adicionar_livro("L2", "O Hobbit", "Tolkien", "ficcao", 1)
    s.adicionar_usuario("U1", "Ana", "11122233344", "ana@email.com", "comum")
    s.adicionar_usuario("U2", "Bruno", "55566677788", "bruno@email.com", "premium")
    s.adicionar_usuario("U3", "Carla", "99988877766", "carla@email.com", "funcionario")
    return s


def test_emprestimo_sucesso_reduz_estoque_e_incrementa_usuario():
    s = setup_sistema_base()
    resultado = s.emprestar_livro("U1", "L1")

    assert resultado is True
    assert s.livros["L1"].quantidade == 1
    assert s.usuarios["U1"].emprestimos_ativos == 1
    assert len(s.emprestimos) == 1
    assert s.emprestimos[0].esta_ativo() is True


def test_emprestimo_livro_indisponivel():
    s = setup_sistema_base()
    s.emprestar_livro("U1", "L2")  # L2 tem apenas 1 exemplar, agora esgotado
    resultado = s.emprestar_livro("U2", "L2")

    assert resultado is False
    assert s.livros["L2"].quantidade == 0
    assert s.usuarios["U2"].emprestimos_ativos == 0


def test_limite_de_emprestimos_usuario_comum():
    s = setup_sistema_base()
    s.adicionar_livro("L3", "Livro 3", "Autor", "geral", 5)
    s.adicionar_livro("L4", "Livro 4", "Autor", "geral", 5)
    s.adicionar_livro("L5", "Livro 5", "Autor", "geral", 5)

    assert s.emprestar_livro("U1", "L1") is True  # 1o
    assert s.emprestar_livro("U1", "L3") is True  # 2o
    assert s.emprestar_livro("U1", "L4") is True  # 3o
    assert s.emprestar_livro("U1", "L5") is False  # 4o -> deve falhar (limite = 3)


def test_devolucao_no_prazo_sem_multa():
    s = setup_sistema_base()
    s.emprestar_livro("U1", "L1")
    multa = s.devolver_livro("U1", "L1")

    assert multa == 0
    assert s.livros["L1"].quantidade == 2
    assert s.usuarios["U1"].emprestimos_ativos == 0


def test_devolucao_com_atraso_calcula_multa_corretamente():
    s = setup_sistema_base()
    s.emprestar_livro("U1", "L1")

    # Força vencimento no passado (atraso de 5 dias)
    for emp in s.emprestimos:
        if emp.usuario_id == "U1" and emp.livro_id == "L1":
            emp.vencimento = datetime.date.today() - datetime.timedelta(days=5)

    # Usuario Comum tem multa de 2/dia -> 5 * 2 = 10
    multa = s.devolver_livro("U1", "L1")
    assert multa == 10


def test_mascaramento_cpf_lgpd():
    s = setup_sistema_base()
    cpf_mascarado = s.mascarar_cpf("11122233344")
    assert cpf_mascarado == "********3344"
    assert "111222" not in cpf_mascarado


if __name__ == "__main__":
    # Permite rodar com `python test_sistema.py` diretamente
    test_emprestimo_sucesso_reduz_estoque_e_incrementa_usuario()
    test_emprestimo_livro_indisponivel()
    test_limite_de_emprestimos_usuario_comum()
    test_devolucao_no_prazo_sem_multa()
    test_devolucao_com_atraso_calcula_multa_corretamente()
    test_mascaramento_cpf_lgpd()
    print("Todos os testes de caracterizacao passaram com sucesso!")
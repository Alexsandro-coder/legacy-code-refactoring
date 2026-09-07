"""
Suíte de Testes de Caracterização e Regressão Automatizados.

Este arquivo valida a preservação de comportamentos do sistema legado, a eficácia
da refatoração com Guard Clauses (incluindo a correção do bug do usuário inexistente)
e o funcionamento correto de todas as novas extensões (Professor, Reserva FIFO e Relatório Resumido).
"""

import datetime
from services.biblioteca_service import Sistema


def setup_sistema_base() -> Sistema:
    """Fixture auxiliar para inicializar um sistema com acervo e usuários padronizados."""
    s = Sistema()
    s.adicionar_livro("L1", "Clean Code", "Robert Martin", "tecnico", 2)
    s.adicionar_livro("L2", "O Hobbit", "Tolkien", "ficcao", 1)
    s.adicionar_usuario("U1", "Ana", "11122233344", "ana@email.com", "comum")
    s.adicionar_usuario("U2", "Bruno", "55566677788", "bruno@email.com", "premium")
    s.adicionar_usuario("U3", "Carla", "99988877766", "carla@email.com", "funcionario")
    s.adicionar_usuario("U4", "Daniel", "44455566677", "daniel@email.com", "professor")
    return s


def test_emprestimo_sucesso_reduz_estoque_e_incrementa_usuario():
    """Valida se o empréstimo reduz estoque e altera saldo do usuário."""
    s = setup_sistema_base()
    resultado = s.emprestar_livro("U1", "L1")

    assert resultado is True
    assert s.livros["L1"].quantidade == 1
    assert s.usuarios["U1"].emprestimos_ativos == 1
    assert len(s.emprestimos) == 1
    assert s.emprestimos[0].esta_ativo() is True


def test_emprestimo_livro_indisponivel():
    """Valida se tentativa de empréstimo para livro sem estoque é rejeitada."""
    s = setup_sistema_base()
    s.emprestar_livro("U1", "L2")  # L2 tinha apenas 1 exemplar, agora esgotado
    resultado = s.emprestar_livro("U2", "L2")

    assert resultado is False
    assert s.livros["L2"].quantidade == 0
    assert s.usuarios["U2"].emprestimos_ativos == 0


def test_correcao_bug_usuario_inexistente():
    """
    Testa a correção do bug do sistema legado (Parte 1 - Item C).
    Garante que tentar emprestar para usuário inexistente não lança exceção/KeyError
    e retorna False graciosamente via Guard Clause.
    """
    s = setup_sistema_base()
    resultado = s.emprestar_livro("U999", "L1")  # U999 não existe

    assert resultado is False
    assert s.livros["L1"].quantidade == 2  # Estoque permanece intacto


def test_limite_de_emprestimos_usuario_comum():
    """Valida se usuário comum é limitado a exatamente 3 empréstimos simultâneos."""
    s = setup_sistema_base()
    s.adicionar_livro("L3", "Livro 3", "Autor", "geral", 5)
    s.adicionar_livro("L4", "Livro 4", "Autor", "geral", 5)
    s.adicionar_livro("L5", "Livro 5", "Autor", "geral", 5)

    assert s.emprestar_livro("U1", "L1") is True  # 1º
    assert s.emprestar_livro("U1", "L3") is True  # 2º
    assert s.emprestar_livro("U1", "L4") is True  # 3º
    assert s.emprestar_livro("U1", "L5") is False  # 4º -> Deve falhar (limite = 3)


def test_extensao_professor_regras_especificas():
    """
    Extensão 1: Valida as regras do novo perfil Professor.
    Limite: 15 empréstimos | Prazo: 60 dias | Multa por atraso: R$ 0.
    """
    s = setup_sistema_base()
    prof = s.usuarios["U4"]

    assert prof.limite_emprestimos() == 15
    assert prof.prazo_dias() == 60
    assert prof.calcular_multa(10) == 0  # Isento de multa


def test_devolucao_no_prazo_sem_multa():
    """Valida devolução no prazo sem cobrança de multa."""
    s = setup_sistema_base()
    s.emprestar_livro("U1", "L1")
    multa = s.devolver_livro("U1", "L1")

    assert multa == 0
    assert s.livros["L1"].quantidade == 2
    assert s.usuarios["U1"].emprestimos_ativos == 0


def test_devolucao_com_atraso_calcula_multa_corretamente():
    """Valida o cálculo de multa por atraso para perfil Comum (R$ 2/dia)."""
    s = setup_sistema_base()
    s.emprestar_livro("U1", "L1")

    # Força vencimento no passado (5 dias de atraso)
    for emp in s.emprestimos:
        if emp.usuario_id == "U1" and emp.livro_id == "L1":
            emp.vencimento = datetime.date.today() - datetime.timedelta(days=5)

    # Multa = 5 dias * R$ 2 = R$ 10
    multa = s.devolver_livro("U1", "L1")
    assert multa == 10


def test_extensao_reserva_fila_fifo():
    """
    Extensão 3: Valida a regra de reservas e a fila de espera FIFO.
    Garante que reserva só é aceita se estoque = 0 e desempilha na ordem correta.
    """
    s = setup_sistema_base()

    # Tentativa de reserva em livro disponível deve falhar
    assert s.reservar_livro("U2", "L2") is False

    # Esgota o estoque de L2
    s.emprestar_livro("U1", "L2")  # L2 fica com qtd = 0

    # Agora Bruno (U2) e Daniel (U4) reservam L2
    assert s.reservar_livro("U2", "L2") is True
    assert s.reservar_livro("U4", "L2") is True

    # Tentativa duplicada do mesmo usuário deve ser rejeitada
    assert s.reservar_livro("U2", "L2") is False

    # Fila deve conter U2 primeiro e U4 em seguida
    assert s.livros["L2"].reservas == ["U2", "U4"]

    # Ao devolver L2, o próximo da fila (U2) deve ser removido da espera
    s.devolver_livro("U1", "L2")
    assert s.livros["L2"].reservas == ["U4"]


def test_extensao_relatorio_resumido():
    """Extensão 2: Valida a agregação de totais do relatório resumido."""
    s = setup_sistema_base()
    s.emprestar_livro("U1", "L1")

    resumo = s.relatorio_resumido()

    assert resumo["total_titulos"] == 2
    assert resumo["total_exemplares"] == 3
    assert resumo["total_emprestados"] == 1
    assert resumo["total_atrasados"] == 0


def test_mascaramento_cpf_lgpd():
    """Valida se os logs e relatórios mascaram os dados sensíveis de CPF."""
    s = setup_sistema_base()
    cpf_mascarado = s.mascarar_cpf("11122233344")

    assert cpf_mascarado == "********3344"
    assert "111222" not in cpf_mascarado


if __name__ == "__main__":
    # Permite executar com `python test_sistema.py`
    test_emprestimo_sucesso_reduz_estoque_e_incrementa_usuario()
    test_emprestimo_livro_indisponivel()
    test_correcao_bug_usuario_inexistente()
    test_limite_de_emprestimos_usuario_comum()
    test_extensao_professor_regras_especificas()
    test_devolucao_no_prazo_sem_multa()
    test_devolucao_com_atraso_calcula_multa_corretamente()
    test_extensao_reserva_fila_fifo()
    test_extensao_relatorio_resumido()
    test_mascaramento_cpf_lgpd()
    print("Todos os 10 testes de caracterizacao e extensao passaram com 100% de sucesso!")
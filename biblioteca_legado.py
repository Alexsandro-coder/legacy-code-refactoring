"""
Sistema de Gestão de Biblioteca - Ponto de Entrada Principal (Main).

Este arquivo importa os modelos e serviços modularizados e executa a demonstração
dos 8 cenários operacionais para validação do comportamento do sistema.

Módulos Utilizados:
- `models.livro`: Entidade Livro e fila FIFO de reservas.
- `models.usuario`: Polimorfismo de Usuários (Comum, Premium, Funcionario, Professor).
- `models.emprestimo`: Transações e prazos de empréstimo.
- `services.biblioteca_service`: Regras de negócio e orquestração do sistema.
- `reports.relatorio_service`: Formatação de relatórios analíticos e resumidos.
"""

import datetime
from models.livro import Livro
from models.usuario import Usuario, Comum, Premium, Funcionario, Professor, TIPOS_USUARIOS, criar_usuario
from models.emprestimo import Emprestimo
from services.biblioteca_service import Sistema


def executar_demonstracao():
    """Executa a simulação completa dos 8 cenários operacionais da biblioteca."""
    s = Sistema()

    # --- Cadastro de livros ---
    s.adicionar_livro("L1", "Clean Code", "Robert Martin", "tecnico", 2)
    s.adicionar_livro("L2", "O Hobbit", "Tolkien", "ficcao", 1)
    s.adicionar_livro("L3", "SICP", "Abelson", "tecnico", 3)

    # --- Cadastro de usuarios (um de cada tipo, incluindo o novo tipo Professor) ---
    s.adicionar_usuario("U1", "Ana", "11122233344", "ana@email.com", "comum")
    s.adicionar_usuario("U2", "Bruno", "55566677788", "bruno@email.com", "premium")
    s.adicionar_usuario("U3", "Carla", "99988877766", "carla@email.com", "funcionario")
    s.adicionar_usuario("U4", "Daniel", "44455566677", "daniel@email.com", "professor")

    print("========== CENARIO 1: emprestimos normais ==========")
    s.emprestar_livro("U1", "L1")
    s.emprestar_livro("U2", "L2")
    s.emprestar_livro("U3", "L3")

    print()
    print("========== CENARIO 2: livro esgotado ==========")
    s.emprestar_livro("U1", "L2")

    print()
    print("========== CENARIO 3: limite de emprestimos (comum = 3) ==========")
    s.adicionar_livro("L4", "Livro Extra 1", "Autor", "geral", 5)
    s.adicionar_livro("L5", "Livro Extra 2", "Autor", "geral", 5)
    s.adicionar_livro("L6", "Livro Extra 3", "Autor", "geral", 5)
    s.emprestar_livro("U1", "L4")
    s.emprestar_livro("U1", "L5")
    s.emprestar_livro("U1", "L6")

    print()
    print("========== CENARIO 4: devolucao no prazo (sem multa) ==========")
    s.devolver_livro("U1", "L1")

    print()
    print("========== CENARIO 5: devolucao com ATRASO e multa por tipo ==========")
    for _e in s.emprestimos:
        if _e.usuario_id == "U1" and _e.livro_id == "L4":
            _e.vencimento = datetime.date.today() - datetime.timedelta(days=5)
    s.devolver_livro("U1", "L4")

    for _e in s.emprestimos:
        if _e.usuario_id == "U2" and _e.livro_id == "L2":
            _e.vencimento = datetime.date.today() - datetime.timedelta(days=10)
    s.devolver_livro("U2", "L2")

    for _e in s.emprestimos:
        if _e.usuario_id == "U3" and _e.livro_id == "L3":
            _e.vencimento = datetime.date.today() - datetime.timedelta(days=20)
    s.devolver_livro("U3", "L3")

    print()
    print("========== CENARIO 6: relatorio final ==========")
    s.relatorio()

    print()
    print("========== CENARIO 7: relatorio resumido ==========")
    s.relatorio_resumido()

    print()
    print("========== CENARIO 8: fila de reserva FIFO ==========")
    # L2 está disponível agora (foi devolvido no cenário 5)
    # 1. Ana pega L2 novamente -> L2 fica esgotado (qtd = 0)
    s.emprestar_livro("U1", "L2")
    # 2. Bruno e Daniel tentam pegar L2 esgotado -> falha
    s.emprestar_livro("U2", "L2")
    s.emprestar_livro("U4", "L2")
    # 3. Ambos entram na fila de reserva (ordem FIFO: U2 primeiro, U4 depois)
    s.reservar_livro("U2", "L2")
    s.reservar_livro("U4", "L2")
    # 4. Ana devolve L2 -> o log avisa que o próximo contemplado é U2!
    s.devolver_livro("U1", "L2")


if __name__ == "__main__":
    executar_demonstracao()
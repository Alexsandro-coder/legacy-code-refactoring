"""
Módulo do Modelo de Domínio: Emprestimo.

Princípios aplicados (Boas Práticas):
- SRP (Single Responsibility Principle): Representa apenas o registro e estado
  temporal de um empréstimo realizado (vencimento e devolução).
"""

import datetime


class Emprestimo:
    """
    Representa a transação de um empréstimo de livro para um usuário.
    
    Atributos:
        usuario_id (str): ID do usuário tomador.
        livro_id (str): ID do livro emprestado.
        vencimento (datetime.date): Data estipulada para a devolução.
        devolvido (bool): Status indicando se o livro já foi devolvido.
    """

    def __init__(self, usuario_id: str, livro_id: str, vencimento: datetime.date):
        self.usuario_id = usuario_id
        self.livro_id = livro_id
        self.vencimento = vencimento
        self.devolvido = False

    def esta_ativo(self) -> bool:
        """Verifica se o empréstimo ainda está em aberto (não devolvido)."""
        return not self.devolvido

    def finalizar(self) -> None:
        """Marca o empréstimo como concluído/devolvido."""
        self.devolvido = True

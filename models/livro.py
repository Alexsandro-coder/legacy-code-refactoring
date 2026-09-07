"""
Módulo do Modelo de Domínio: Livro.

Princípios aplicados (Boas Práticas):
- SRP (Single Responsibility Principle): A classe `Livro` é responsável APENAS
  por gerenciar seu próprio estado (estoque disponível, dados cadastrais e a
  fila de espera/reserva FIFO).
- Extensão 3 (Reserva): Implementação da lista de espera sequencial (FIFO).
"""

class Livro:
    """
    Representa um livro no acervo da biblioteca.
    
    Atributos:
        livro_id (str): Identificador único do livro (ex: 'L1').
        titulo (str): Título do livro.
        autor (str): Autor do livro.
        categoria (str): Categoria ou gênero (ex: 'tecnico', 'ficcao').
        quantidade (int): Quantidade de exemplares atualmente disponíveis para empréstimo.
        qtd_total (int): Quantidade total de exemplares cadastrados no acervo.
        reservas (list): Fila FIFO (First In, First Out) contendo os IDs dos usuários aguardando.
    """

    def __init__(self, livro_id: str, titulo: str, autor: str, categoria: str, quantidade: int):
        self.livro_id = livro_id
        self.titulo = titulo
        self.autor = autor
        self.categoria = categoria
        self.quantidade = quantidade
        self.qtd_total = quantidade  # Guarda o total original para controle de estoque
        self.reservas = []  # Fila FIFO de usuários aguardando o exemplar quando a quantidade é 0

    def esta_disponivel(self) -> bool:
        """Verifica se há pelo menos um exemplar disponível para empréstimo."""
        return self.quantidade > 0

    def emprestar(self) -> None:
        """Decrementa a quantidade de exemplares disponíveis."""
        if self.esta_disponivel():
            self.quantidade -= 1

    def devolver(self) -> None:
        """Incrementa a quantidade de exemplares disponíveis ao ser devolvido."""
        self.quantidade += 1

    def adicionar_reserva(self, usuario_id: str) -> bool:
        """
        Adiciona um usuário à fila de reserva do livro (Extensão 3).
        Evita duplicação caso o mesmo usuário tente reservar mais de uma vez.
        """
        if usuario_id in self.reservas:
            return False  # Usuário já está na fila
        self.reservas.append(usuario_id)
        return True

    def tem_reservas(self) -> bool:
        """Verifica se há usuários aguardando na fila de reserva."""
        return len(self.reservas) > 0

    def proximo_da_reserva(self) -> str | None:
        """
        Remove e retorna o próximo usuário da fila de espera (FIFO - First In, First Out).
        Retorna None se a fila estiver vazia.
        """
        if self.tem_reservas():
            return self.reservas.pop(0)  # Remove o primeiro da fila
        return None

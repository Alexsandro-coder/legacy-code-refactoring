"""
Módulo do Modelo de Domínio: Usuários e Tipos de Perfil.

Princípios aplicados (Boas Práticas):
- OCP (Open/Closed Principle - Aula 6): A classe `Usuario` define o contrato base.
  Para adicionar um novo perfil de usuário (como o perfil `Professor` na Extensão 1),
  criamos uma nova subclasse herdando de `Usuario` sem modificar as regras de negócio existentes.
- Polimorfismo: Cada tipo de usuário sobrescreve os métodos de regra (`limite_emprestimos`, 
  `prazo_dias`, `calcular_multa`) com seu próprio comportamento específico.
- Factory Pattern (Padrão Criacional): A função `criar_usuario` desacopla a criação
  das subclasses do código cliente.
"""

from abc import ABC, abstractmethod


class Usuario(ABC):
    """
    Classe Abstrata Base para representar um Usuário do sistema da biblioteca.
    
    Atributos:
        usuario_id (str): Identificador único do usuário (ex: 'U1').
        nome (str): Nome completo.
        cpf (str): CPF cadastrado.
        email (str): E-mail de contato.
        emprestimos_ativos (int): Contador de empréstimos atualmente em aberto.
        bloqueado (bool): Status de bloqueio do usuário.
    """

    def __init__(self, usuario_id: str, nome: str, cpf: str, email: str):
        self.usuario_id = usuario_id
        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.emprestimos_ativos = 0
        self.bloqueado = False

    @abstractmethod
    def limite_emprestimos(self) -> int:
        """Retorna o número máximo de empréstimos simultâneos permitidos."""
        pass

    @abstractmethod
    def prazo_dias(self) -> int:
        """Retorna o prazo em dias para a devolução de livros."""
        pass

    @abstractmethod
    def calcular_multa(self, dias_atraso: int) -> float:
        """Calcula o valor da multa com base nos dias de atraso."""
        pass


class Comum(Usuario):
    """Perfil Usuário Comum: limite de 3 empréstimos, prazo de 7 dias, multa de R$ 2/dia."""

    def limite_emprestimos(self) -> int:
        return 3

    def prazo_dias(self) -> int:
        return 7

    def calcular_multa(self, dias_atraso: int) -> float:
        return 2 * dias_atraso


class Premium(Usuario):
    """Perfil Usuário Premium: limite de 5 empréstimos, prazo de 14 dias, multa de R$ 1/dia."""

    def limite_emprestimos(self) -> int:
        return 5

    def prazo_dias(self) -> int:
        return 14

    def calcular_multa(self, dias_atraso: int) -> float:
        return 1 * dias_atraso


class Funcionario(Usuario):
    """Perfil Funcionário: limite de 10 empréstimos, prazo de 30 dias, isento de multa (R$ 0)."""

    def limite_emprestimos(self) -> int:
        return 10

    def prazo_dias(self) -> int:
        return 30

    def calcular_multa(self, dias_atraso: int) -> float:
        return 0


class Professor(Usuario):
    """
    Extensão 1 - Novo tipo de usuário: Professor (Testa o Princípio OCP).
    Regras: limite de 15 empréstimos, prazo de 60 dias, multa de R$ 0/dia (isento).
    """

    def limite_emprestimos(self) -> int:
        return 15

    def prazo_dias(self) -> int:
        return 60

    def calcular_multa(self, dias_atraso: int) -> float:
        return 0


# Mapeamento extensível de tipos cadastráveis para a fábrica (Factory Pattern)
TIPOS_USUARIOS = {
    "comum": Comum,
    "premium": Premium,
    "funcionario": Funcionario,
    "professor": Professor,
}


def criar_usuario(usuario_id: str, nome: str, cpf: str, email: str, tipo: str) -> Usuario | None:
    """
    Fábrica simples (Factory Method) para instanciar subclasse correta de Usuario.
    Retorna None se o tipo informado não for reconhecido.
    """
    classe = TIPOS_USUARIOS.get(tipo.lower())
    if not classe:
        return None
    return classe(usuario_id, nome, cpf, email)

"""
Módulo do Serviço de Relatórios (Analítico e Resumido).

Princípios aplicados (Boas Práticas):
- SRP (Single Responsibility Principle - Aula 6 / Extensão 2): Isolamos a responsabilidade
  de geração e formatação de relatórios em um serviço dedicado, sem poluir a classe principal
  de negócio da biblioteca (`Sistema` / `BibliotecaService`).
- LGPD: O mascaramento de CPF é aplicado ao gerar as saídas visuais do relatório.
"""

import datetime
from config.logger import obter_logger

logger = obter_logger("RELATORIO_SERVICE")


class RelatorioService:
    """Serviço responsável por gerar e formatar relatórios da biblioteca."""

    @staticmethod
    def mascarar_cpf(cpf: str) -> str:
        """
        Mascara os primeiros dígitos do CPF para proteção de privacidade (LGPD).
        Exemplo: '11122233344' -> '********3344'
        """
        if not cpf or len(cpf) < 4:
            return "****"
        return f"********{cpf[-4:]}"

    @classmethod
    def gerar_relatorio_analitico(cls, livros: dict, usuarios: dict) -> None:
        """
        Gera o relatório completo detalhando o status de cada livro no acervo
        e o número de empréstimos ativos por usuário.
        """
        logger.info("=== RELATORIO DA BIBLIOTECA ===")
        for livro in livros.values():
            logger.info(f"Livro: {livro.titulo} | Disponivel: {livro.quantidade}/{livro.qtd_total}")
        for usuario in usuarios.values():
            cpf_mascarado = cls.mascarar_cpf(usuario.cpf)
            logger.info(f"Usuario: {usuario.nome} CPF: {cpf_mascarado} | Emprestimos: {usuario.emprestimos_ativos}")

    @classmethod
    def gerar_relatorio_resumido(cls, livros: dict, emprestimos: list) -> dict:
        """
        Extensão 2 - Novo formato de relatório: Relatório Resumido.
        Exibe agregações e estatísticas gerais em tempo real (totais de títulos,
        exemplares, empréstimos ativos e atrasos).
        """
        hoje = datetime.date.today()

        total_titulos = len(livros)
        total_exemplares = sum(livro.qtd_total for livro in livros.values())
        total_emprestados = sum(1 for e in emprestimos if e.esta_ativo())
        total_atrasados = sum(1 for e in emprestimos if e.esta_ativo() and e.vencimento < hoje)

        logger.info("=== RELATORIO RESUMIDO DA BIBLIOTECA ===")
        logger.info(f"Total de titulos cadastrados: {total_titulos}")
        logger.info(f"Total de exemplares no acervo: {total_exemplares}")
        logger.info(f"Total de exemplares emprestados: {total_emprestados}")
        logger.info(f"Total de emprestimos em atraso: {total_atrasados}")

        return {
            "total_titulos": total_titulos,
            "total_exemplares": total_exemplares,
            "total_emprestados": total_emprestados,
            "total_atrasados": total_atrasados,
        }

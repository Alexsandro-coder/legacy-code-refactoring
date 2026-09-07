"""
Módulo de Serviço Principal: Orquestração do Sistema da Biblioteca.

Princípios aplicados (Boas Práticas):
- Guard Clauses (Aula 4): Tratamento antecipado de validações e erros. O fluxo principal
  fica no nível 0 de indentação, eliminando aninhamentos excessivos ("setas para a direita").
- Correção do Bug Escondido (Parte 1 - Item C): Validação rigorosa da existência de usuário
  e livro antes de tentar acessar atributos ou registrar empréstimos (evitando KeyError ou AttributeError).
- Logging com LGPD (Aula 5): Substituição de prints por logger nativo e mascaramento de CPF.
- SRP (Aula 6): Delegação da geração de relatórios para `RelatorioService`.
"""

import datetime
from config.logger import obter_logger
from models.livro import Livro
from models.usuario import criar_usuario
from models.emprestimo import Emprestimo
from reports.relatorio_service import RelatorioService

logger = obter_logger("SISTEMA_BIBLIOTECA")


class Sistema:
    """
    Classe de orquestração do sistema da biblioteca.
    Gerencia o cadastro de acervo, usuários, operações de empréstimo,
    devolução, reserva e relatórios.
    """

    def __init__(self):
        self.livros = {}        # Dicionário mapeando livro_id -> instância de Livro
        self.usuarios = {}      # Dicionário mapeando usuario_id -> instância de Usuario
        self.emprestimos = []   # Lista contendo todas as instâncias de Emprestimo

    def mascarar_cpf(self, cpf: str) -> str:
        """Método utilitário para mascarar CPF (LGPD). Delegado ao RelatorioService."""
        return RelatorioService.mascarar_cpf(cpf)

    def adicionar_livro(self, livro_id: str, titulo: str, autor: str, categoria: str, quantidade: int) -> None:
        """Cadastra um novo livro no acervo."""
        self.livros[livro_id] = Livro(livro_id, titulo, autor, categoria, quantidade)

    def adicionar_usuario(self, usuario_id: str, nome: str, cpf: str, email: str, tipo: str) -> bool:
        """Cadastra um novo usuário utilizando o Factory Pattern (`criar_usuario`)."""
        usuario = criar_usuario(usuario_id, nome, cpf, email, tipo)
        if not usuario:
            logger.warning(f"Tipo de usuario '{tipo}' invalido ao cadastrar usuario {usuario_id}.")
            return False
        self.usuarios[usuario_id] = usuario
        return True

    def emprestar_livro(self, usuario_id: str, livro_id: str) -> bool:
        """
        Realiza o empréstimo de um livro para um usuário.
        
        Refatorado com Guard Clauses (Aula 4):
        Todas as condições de falha/rejeição retornam antecipadamente (`return False`),
        mantendo o caminho feliz no nível 0 de indentação.
        """
        # Guard Clause 1: Valida se usuário existe (Corrige o bug do código legado!)
        if usuario_id not in self.usuarios:
            logger.warning("Usuario nao encontrado")
            return False

        usuario = self.usuarios[usuario_id]

        # Guard Clause 2: Valida se livro existe no acervo
        if livro_id not in self.livros:
            logger.warning("Livro nao encontrado")
            return False

        livro = self.livros[livro_id]

        # Log seguro em compliance com a LGPD (mascarando CPF)
        cpf_mascarado = self.mascarar_cpf(usuario.cpf)
        logger.info(f"Processando emprestimo: usuario {usuario_id} CPF {cpf_mascarado} livro {livro_id}")

        # Guard Clause 3: Valida se usuário está bloqueado
        if usuario.bloqueado:
            logger.warning("Usuario bloqueado")
            return False

        # Guard Clause 4: Valida limite de empréstimos do perfil (Polimorfismo / OCP)
        if usuario.emprestimos_ativos >= usuario.limite_emprestimos():
            logger.warning("Limite de emprestimos atingido")
            return False

        # Guard Clause 5: Valida estoque disponível do livro
        if not livro.esta_disponivel():
            logger.warning("Livro indisponivel")
            return False

        # --- CAMINHO FELIZ (Nível 0) ---
        livro.emprestar()
        usuario.emprestimos_ativos += 1

        vencimento = datetime.date.today() + datetime.timedelta(days=usuario.prazo_dias())
        novo_emprestimo = Emprestimo(usuario_id, livro_id, vencimento)
        self.emprestimos.append(novo_emprestimo)

        logger.info(f"Emprestimo realizado com sucesso. Vencimento: {vencimento}")
        return True

    def devolver_livro(self, usuario_id: str, livro_id: str) -> float:
        """
        Processa a devolução de um livro emprestado e calcula multas por atraso.
        Retorna 0 para devolução no prazo, valor da multa se houver atraso, ou -1 em caso de erro.
        """
        # Guard Clause 1: Valida se usuário existe
        if usuario_id not in self.usuarios:
            logger.warning("Usuario nao encontrado")
            return -1

        usuario = self.usuarios[usuario_id]
        cpf_mascarado = self.mascarar_cpf(usuario.cpf)
        logger.info(f"Processando devolucao: usuario {usuario_id} CPF {cpf_mascarado} livro {livro_id}")

        # Busca o empréstimo ativo correspondente
        for emprestimo in self.emprestimos:
            if emprestimo.usuario_id == usuario_id and emprestimo.livro_id == livro_id and emprestimo.esta_ativo():
                emprestimo.finalizar()

                livro = self.livros[livro_id]
                livro.devolver()
                usuario.emprestimos_ativos -= 1

                # Encaixe da Fila de Reserva (Extensão 3)
                if livro.tem_reservas():
                    proximo_usuario = livro.proximo_da_reserva()
                    logger.info(f"Livro {livro_id} liberado da fila! Proximo usuario contemplado: {proximo_usuario}")

                hoje = datetime.date.today()
                if hoje > emprestimo.vencimento:
                    dias_atraso = (hoje - emprestimo.vencimento).days
                    multa = usuario.calcular_multa(dias_atraso)
                    logger.info(f"Devolucao com atraso. Multa: {multa}")
                    return multa
                else:
                    logger.info("Devolucao OK no prazo")
                    return 0

        logger.warning("Emprestimo nao encontrado")
        return -1

    def reservar_livro(self, usuario_id: str, livro_id: str) -> bool:
        """
        Extensão 3 - Nova regra de negócio: Reserva de livros indisponíveis.
        Adiciona o usuário à fila FIFO de espera se o livro existir e estiver esgotado.
        """
        # Guard Clause 1: Valida existência do usuário
        if usuario_id not in self.usuarios:
            logger.warning("Usuario nao encontrado")
            return False

        # Guard Clause 2: Valida existência do livro
        if livro_id not in self.livros:
            logger.warning("Livro nao encontrado")
            return False

        livro = self.livros[livro_id]

        # Guard Clause 3: Não permite reserva se ainda houver estoque (deve emprestar direto)
        if livro.esta_disponivel():
            logger.warning(f"Livro {livro_id} ainda possui exemplares disponiveis. Faca o emprestimo direto.")
            return False

        # Adiciona o usuário na fila FIFO de reservas do livro
        sucesso = livro.adicionar_reserva(usuario_id)
        if not sucesso:
            logger.warning(f"Usuario {usuario_id} ja possui reserva para o livro {livro_id}")
            return False

        logger.info(f"Reserva realizada com sucesso: usuario {usuario_id} entrou na fila do livro {livro_id}")
        return True

    def relatorio(self) -> None:
        """Gera o relatório analítico (Delega para o RelatorioService - SRP)."""
        RelatorioService.gerar_relatorio_analitico(self.livros, self.usuarios)

    def relatorio_resumido(self) -> dict:
        """Extensão 2 - Relatório Resumido (Delega para o RelatorioService - SRP)."""
        return RelatorioService.gerar_relatorio_resumido(self.livros, self.emprestimos)

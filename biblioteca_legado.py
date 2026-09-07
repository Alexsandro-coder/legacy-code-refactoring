import datetime
import logging

logger = logging.getLogger("BIBLIOTECA")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
))
logger.addHandler(handler)


class Livro:
    def __init__(self, livro_id, titulo, autor, categoria, quantidade):
        self.livro_id = livro_id
        self.titulo = titulo
        self.autor = autor
        self.categoria = categoria
        self.quantidade = quantidade
        self.qtd_total = quantidade
        self.reservas = []  # Fila FIFO de usuarios aguardando o exemplar

    def esta_disponivel(self):
        return self.quantidade > 0

    def emprestar(self):
        self.quantidade -= 1

    def devolver(self):
        self.quantidade += 1

    def adicionar_reserva(self, usuario_id):
        if usuario_id in self.reservas:
            return False
        self.reservas.append(usuario_id)
        return True

    def tem_reservas(self):
        return len(self.reservas) > 0

    def proximo_da_reserva(self):
        if self.tem_reservas():
            return self.reservas.pop(0)
        return None


class Usuario:
    def __init__(self, usuario_id, nome, cpf, email):
        self.usuario_id = usuario_id
        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.emprestimos_ativos = 0
        self.bloqueado = False

    def limite_emprestimos(self):
        raise NotImplementedError

    def prazo_dias(self):
        raise NotImplementedError

    def calcular_multa(self, dias_atraso):
        raise NotImplementedError


class Comum(Usuario):
    def limite_emprestimos(self):
        return 3

    def prazo_dias(self):
        return 7

    def calcular_multa(self, dias_atraso):
        return 2 * dias_atraso


class Premium(Usuario):
    def limite_emprestimos(self):
        return 5

    def prazo_dias(self):
        return 14

    def calcular_multa(self, dias_atraso):
        return 1 * dias_atraso


class Funcionario(Usuario):
    def limite_emprestimos(self):
        return 10

    def prazo_dias(self):
        return 30

    def calcular_multa(self, dias_atraso):
        return 0


class Professor(Usuario):
    def limite_emprestimos(self):
        return 15

    def prazo_dias(self):
        return 60

    def calcular_multa(self, dias_atraso):
        return 0


TIPOS_USUARIOS = {
    "comum": Comum,
    "premium": Premium,
    "funcionario": Funcionario,
    "professor": Professor,
}


def criar_usuario(usuario_id, nome, cpf, email, tipo):
    classe = TIPOS_USUARIOS.get(tipo)
    if not classe:
        return None
    return classe(usuario_id, nome, cpf, email)


class Emprestimo:
    def __init__(self, usuario_id, livro_id, vencimento):
        self.usuario_id = usuario_id
        self.livro_id = livro_id
        self.vencimento = vencimento
        self.devolvido = False

    def esta_ativo(self):
        return not self.devolvido

    def finalizar(self):
        self.devolvido = True


class Sistema:
    def __init__(self):
        self.livros = {}
        self.usuarios = {}
        self.emprestimos = []

    def adicionar_livro(self, livro_id, titulo, autor, categoria, quantidade):
        self.livros[livro_id] = Livro(livro_id, titulo, autor, categoria, quantidade)

    def adicionar_usuario(self, usuario_id, nome, cpf, email, tipo):
        usuario = criar_usuario(usuario_id, nome, cpf, email, tipo)
        if usuario:
            self.usuarios[usuario_id] = usuario

    def mascarar_cpf(self, cpf):
        return f"********{cpf[-4:]}"

    def emprestar_livro(self, usuario_id, livro_id):
        if usuario_id not in self.usuarios:
            logger.warning("Usuario nao encontrado")
            return False

        usuario = self.usuarios[usuario_id]

        if livro_id not in self.livros:
            logger.warning("Livro nao encontrado")
            return False

        livro = self.livros[livro_id]

        logger.info(f"Processando emprestimo: usuario {usuario_id} CPF {self.mascarar_cpf(usuario.cpf)} livro {livro_id}")

        if usuario.bloqueado:
            logger.warning("Usuario bloqueado")
            return False

        if usuario.emprestimos_ativos >= usuario.limite_emprestimos():
            logger.warning("Limite de emprestimos atingido")
            return False

        if not livro.esta_disponivel():
            logger.warning("Livro indisponivel")
            return False

        livro.emprestar()
        usuario.emprestimos_ativos += 1

        vencimento = datetime.date.today() + datetime.timedelta(days=usuario.prazo_dias())
        novo_emprestimo = Emprestimo(usuario_id, livro_id, vencimento)
        self.emprestimos.append(novo_emprestimo)

        logger.info(f"Emprestimo realizado com sucesso. Vencimento: {vencimento}")
        return True

    def devolver_livro(self, usuario_id, livro_id):
        if usuario_id not in self.usuarios:
            logger.warning("Usuario nao encontrado")
            return -1

        usuario = self.usuarios[usuario_id]
        logger.info(f"Processando devolucao: usuario {usuario_id} CPF {self.mascarar_cpf(usuario.cpf)} livro {livro_id}")

        for emprestimo in self.emprestimos:
            if emprestimo.usuario_id == usuario_id and emprestimo.livro_id == livro_id and emprestimo.esta_ativo():
                emprestimo.finalizar()

                livro = self.livros[livro_id]
                livro.devolver()
                usuario.emprestimos_ativos -= 1

                # Encaixe da Fila de Reserva na Devolução
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

    def reservar_livro(self, usuario_id, livro_id):
        """Encaixe do metodo de reserva no Sistema"""
        if usuario_id not in self.usuarios:
            logger.warning("Usuario nao encontrado")
            return False

        if livro_id not in self.livros:
            logger.warning("Livro nao encontrado")
            return False

        livro = self.livros[livro_id]

        if livro.esta_disponivel():
            logger.warning(f"Livro {livro_id} ainda possui exemplares disponiveis. Faca o emprestimo direto.")
            return False

        sucesso = livro.adicionar_reserva(usuario_id)
        if not sucesso:
            logger.warning(f"Usuario {usuario_id} ja possui reserva para o livro {livro_id}")
            return False

        logger.info(f"Reserva realizada com sucesso: usuario {usuario_id} entrou na fila do livro {livro_id}")
        return True

    def relatorio(self):
        logger.info("=== RELATORIO DA BIBLIOTECA ===")
        for livro in self.livros.values():
            logger.info(f"Livro: {livro.titulo} | Disponivel: {livro.quantidade}/{livro.qtd_total}")
        for usuario in self.usuarios.values():
            logger.info(f"Usuario: {usuario.nome} CPF: {self.mascarar_cpf(usuario.cpf)} | Emprestimos: {usuario.emprestimos_ativos}")

    def relatorio_resumido(self):
        hoje = datetime.date.today()

        total_titulos = len(self.livros)
        total_exemplares = sum(livro.qtd_total for livro in self.livros.values())
        total_emprestados = sum(1 for e in self.emprestimos if e.esta_ativo())
        total_atrasados = sum(1 for e in self.emprestimos if e.esta_ativo() and e.vencimento < hoje)

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


if __name__ == "__main__":
    s = Sistema()

    # --- Cadastro de livros ---
    s.adicionar_livro("L1", "Clean Code", "Robert Martin", "tecnico", 2)
    s.adicionar_livro("L2", "O Hobbit", "Tolkien", "ficcao", 1)
    s.adicionar_livro("L3", "SICP", "Abelson", "tecnico", 3)

    # --- Cadastro de usuarios (um de cada tipo) ---
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
    import datetime as _dt

    for _e in s.emprestimos:
        if _e.usuario_id == "U1" and _e.livro_id == "L4":
            _e.vencimento = _dt.date.today() - _dt.timedelta(days=5)
    s.devolver_livro("U1", "L4")

    for _e in s.emprestimos:
        if _e.usuario_id == "U2" and _e.livro_id == "L2":
            _e.vencimento = _dt.date.today() - _dt.timedelta(days=10)
    s.devolver_livro("U2", "L2")

    for _e in s.emprestimos:
        if _e.usuario_id == "U3" and _e.livro_id == "L3":
            _e.vencimento = _dt.date.today() - _dt.timedelta(days=20)
    s.devolver_livro("U3", "L3")

    print()
    print("========== CENARIO 6: relatorio final ==========")
    s.relatorio()

    print()
    print("========== CENARIO 7: relatorio resumido ==========")
    s.relatorio_resumido()

    print()
    print("========== CENARIO 8: fila de reserva FIFO ==========")
    # L2 esta disponivel agora (foi devolvido no cenario 5)
    # 1. Ana pega L2 novamente -> L2 fica esgotado (qtd = 0)
    s.emprestar_livro("U1", "L2")
    # 2. Bruno e Daniel tentam pegar L2 esgotado -> falha
    s.emprestar_livro("U2", "L2")
    s.emprestar_livro("U4", "L2")
    # 3. Ambos entram na fila de reserva (ordem: U2 primeiro, U4 depois)
    s.reservar_livro("U2", "L2")
    s.reservar_livro("U4", "L2")
    # 4. Ana devolve L2 -> o log deve avisar que o proximo contemplado eh U2!
    s.devolver_livro("U1", "L2")
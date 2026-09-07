import datetime

LIMITES_EMPRESTIMO = {"comum": 3, "premium": 5, "funcionario": 10}
PADRAO_LIMITE_EMPRESTIMO = 1
PRAZOS_EMPRESTIMO = {"comum": 7, "premium": 14, "funcionario": 30}
PADRAO_PRAZOS_EMPRESTIMO = 3
MULTAS_EMPRESTIMOS = {"comum": 2, "premium": 1, "funcionario": 0}
PADRAO_MULTAS_EMPRESTIMO = 3

class Sistema:
    def __init__(self):
        self.livros = {}
        self.usuarios = {}
        self.emprestimos = []

    def adicionar_livro(self, livro_id, titulo, autor, categoria, quantidade):
        self.livros[livro_id] = {"titulo": titulo, "autor": autor, "categoria": categoria, "qtd": quantidade, "qtd_total": quantidade}

    def adicionar_usuario(self, usuario_id, nome, cpf, email, tipo):
        self.usuarios[usuario_id] = {"nome": nome, "cpf": cpf, "email": email, "tipo": tipo, "emprestimos_ativos": 0,
                      "bloqueado": False}

    def mascarar_cpf(self, cpf):
        return f"********{cpf[-4:]}"

    def emprestar_livro(self, usuario_id, livro_id):
        if usuario_id not in self.usuarios:
            print("Usuario nao encontrado")
            return False

        tipo = self.usuarios[usuario_id]["tipo"]
        limite_livros = LIMITES_EMPRESTIMO.get(tipo, PADRAO_LIMITE_EMPRESTIMO)
        prazo_dias = PRAZOS_EMPRESTIMO.get(tipo, PADRAO_PRAZOS_EMPRESTIMO)

        print(f"Processando emprestimo: usuario {usuario_id} CPF {self.mascarar_cpf(self.usuarios[usuario_id]['cpf'])} livro {livro_id}")

        if livro_id not in self.livros:
            print("Livro nao encontrado")
            return False

        if self.usuarios[usuario_id]["bloqueado"]:
            print("Usuario bloqueado")
            return False

        if self.livros[livro_id]["qtd"] <= 0:
            print("Livro indisponivel")
            return False

        if self.usuarios[usuario_id]["emprestimos_ativos"] >= limite_livros:
            print("Limite de emprestimos atingido")
            return False
        try:
            self.livros[livro_id]["qtd"] = self.livros[livro_id]["qtd"] - 1
            self.usuarios[usuario_id]["emprestimos_ativos"] = self.usuarios[usuario_id]["emprestimos_ativos"] + 1
            vencimento = datetime.date.today() + datetime.timedelta(days=prazo_dias)
            self.emprestimos.append(
                {"usuario": usuario_id, "livro": livro_id, "vencimento": vencimento, "devolvido": False})
            print("Emprestimo OK para " + self.usuarios[usuario_id]["nome"] + " email " + self.usuarios[usuario_id][
                "email"] + " vence em " + str(vencimento))
            return True
        except:
            return False

    def devolver_livro(self, usuario_id, livro_id):
        for emprestimo in self.emprestimos:
            if emprestimo["usuario"] == usuario_id and emprestimo["livro"] == livro_id and emprestimo["devolvido"] == False:
                print(f"Processando devolucao: usuario {usuario_id} CPF {self.mascarar_cpf(self.usuarios[usuario_id]['cpf'])} livro {livro_id}")
                emprestimo["devolvido"] = True
                self.livros[livro_id]["qtd"] = self.livros[livro_id]["qtd"] + 1
                self.usuarios[usuario_id]["emprestimos_ativos"] = self.usuarios[usuario_id]["emprestimos_ativos"] - 1
                # calculo de multa
                tipo = self.usuarios[usuario_id]["tipo"]
                hoje = datetime.date.today()

                if hoje > emprestimo["vencimento"]:
                    dias_atraso = (hoje - emprestimo["vencimento"]).days
                    multa = MULTAS_EMPRESTIMOS.get(tipo, PADRAO_MULTAS_EMPRESTIMO) * dias_atraso
                    print("Devolucao com atraso. Multa: " + str(multa))
                    return multa
                else:
                    print("Devolucao OK no prazo")
                    return 0
        print("Emprestimo nao encontrado")
        return -1

    def relatorio(self):
        print("=== RELATORIO DA BIBLIOTECA ===")
        for livro_id in self.livros:
            print("Livro: " + self.livros[livro_id]["titulo"] + " | Disponivel: " + str(self.livros[livro_id]["qtd"]) + "/" + str(
                self.livros[livro_id]["qtd_total"]))
        for usuario_id in self.usuarios:
            print("Usuario: " + self.usuarios[usuario_id]["nome"] + " CPF: " + self.mascarar_cpf(self.usuarios[usuario_id]['cpf']) + " | Emprestimos: " + str(
                self.usuarios[usuario_id]["emprestimos_ativos"]))


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

    print("========== CENARIO 1: emprestimos normais ==========")
    s.emprestar_livro("U1", "L1")  # comum pega tecnico -> prazo 7 dias
    s.emprestar_livro("U2", "L2")  # premium pega ficcao -> prazo 14 dias
    s.emprestar_livro("U3", "L3")  # funcionario pega tecnico -> prazo 30 dias

    print()
    print("========== CENARIO 2: livro esgotado ==========")
    # L2 so tinha 1 exemplar, ja emprestado para U2
    s.emprestar_livro("U1", "L2")  # deve falhar: indisponivel

    print()
    print("========== CENARIO 3: limite de emprestimos (comum = 3) ==========")
    # Ana (comum) ja tem L1. Vamos testar o limite.
    s.adicionar_livro("L4", "Livro Extra 1", "Autor", "geral", 5)
    s.adicionar_livro("L5", "Livro Extra 2", "Autor", "geral", 5)
    s.adicionar_livro("L6", "Livro Extra 3", "Autor", "geral", 5)
    s.emprestar_livro("U1", "L4")  # 2o emprestimo de Ana -> OK
    s.emprestar_livro("U1", "L5")  # 3o emprestimo de Ana -> OK
    s.emprestar_livro("U1", "L6")  # 4o emprestimo -> deve falhar (limite 3)

    print()
    print("========== CENARIO 4: devolucao no prazo (sem multa) ==========")
    s.devolver_livro("U1", "L1")  # devolvido no prazo -> multa 0

    print()
    print("========== CENARIO 5: devolucao com ATRASO e multa por tipo ==========")
    # Para demonstrar multa, forcamos o vencimento de alguns emprestimos para o passado.
    # (Na pratica isso aconteceria com o tempo, aqui será apenas uma simulação)
    import datetime as _dt

    # Ana (comum): multa de 2/dia. Atraso de 5 dias -> multa 10
    for _e in s.emprestimos:
        if _e["usuario"] == "U1" and _e["livro"] == "L4":
            _e["vencimento"] = _dt.date.today() - _dt.timedelta(days=5)
    s.devolver_livro("U1", "L4")  # esperado: multa 10

    # Bruno (premium): multa de 1/dia. Atraso de 10 dias -> multa 10
    for _e in s.emprestimos:
        if _e["usuario"] == "U2" and _e["livro"] == "L2":
            _e["vencimento"] = _dt.date.today() - _dt.timedelta(days=10)
    s.devolver_livro("U2", "L2")  # esperado: multa 10

    # Carla (funcionario): multa 0/dia. Mesmo com atraso -> multa 0
    for _e in s.emprestimos:
        if _e["usuario"] == "U3" and _e["livro"] == "L3":
            _e["vencimento"] = _dt.date.today() - _dt.timedelta(days=20)
    s.devolver_livro("U3", "L3")  # esperado: multa 0 (funcionario nao paga)

    print()
    print("========== CENARIO 6: relatorio final ==========")
    s.relatorio()
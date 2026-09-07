# Relatório de Refatoração e Extensão - AV1
**Disciplina:** Treinamento de Boas Práticas para o Desenvolvimento de Software  
**Avaliação:** Mapeamento do Código Legado, Refatoração (Parte 1), Extensões (Parte 2) e Relatório (Parte 3)  
**Data:** 08/09/2026  

---

## 1. Mapeamento e Lista dos Problemas Encontrados (Categorias A - E)

- **A. Qualidade e Code Smells:** Uso de atributos e variáveis obscuros de uma única letra (`self.d`, `self.u`, `self.emp`, `id_u`, `id_l`, `t`, `a`), números mágicos de prazos e multas soltos no código (`3`, `5`, `10`, `7`, `14`, `30`, `2`, `1`), e duplicação da estrutura `if/elif` do tipo de usuário repetida 3 vezes (`emprestar` e `devolver`).
- **B. Nomenclatura e Funções Pequenas:** A função `emprestar` era um método gigante monolítico manipulando dicionários primitivos, validações, cálculos de datas, alteração de estoque e formatação de saídas em um único bloco.
- **C. Aninhamento e Tratamento de Erros:** Estrutura em "seta para a direita" com 5 níveis de `if` aninhados em `emprestar`, acompanhada por um bloco `try: ... except: pass` engolindo exceções silenciosamente, e um bug crítico de ordem de execução.
- **D. Logging e Princípios (LGPD):** Impressão de mensagens operacionais via `print()` e vazamento direto de dados pessoais sensíveis (CPF completo e E-mail) sem mascaramento, violando a LGPD.
- **E. SOLID (SRP & OCP):** A classe `Sistema` violava o **SRP** (acumulava persistência em dicionários, regras de negócio, cálculo de multas e formatação de relatórios) e o **OCP** (adicionar um novo perfil exigia alterar `if/elif` em múltiplos lugares).

---

## 2. Justificativas das Decisões de Refatoração

- **Categoria A (Code Smells):** Substituímos estruturas genéricas por objetos de domínio ricos (`Livro`, `Usuario`, `Emprestimo`) e encapsulamos constantes numéricas em métodos polimórficos dos perfis de usuário (aplicando o princípio DRY).
- **Categoria B (Nomenclatura e Funções Pequenas):** Decompomos o método monolítico em métodos pequenos com nomes intencionais (`esta_disponivel`, `limite_emprestimos`, `prazo_dias`, `calcular_multa`), delegando responsabilidades às próprias entidades.
- **Categoria C (Aninhamento e Tratamento de Erros):** Refatoramos com *Guard Clauses* para validar todas as condições de falha antecipadamente com retornos rápidos no nível 0 de indentação (`return False`), eliminando o aninhamento e o `except: pass`.
- **Categoria D (Logging e LGPD):** Substituímos o `print()` pelo `logging.Logger` padronizado e criamos a função `mascarar_cpf` (`********3344`), garantindo conformidade com a LGPD e rastreabilidade por níveis (`INFO` / `WARNING`).
- **Categoria E (SOLID):** Aplicamos o **OCP** através de herança polimórfica (`Comum`, `Premium`, `Funcionario`, `Professor`), permitindo criar novos perfis sem alterar a regra de empréstimo; e aplicamos o **SRP** delegando os relatórios ao `RelatorioService`.

---

## 3. Bug Escondido Encontrado e Corrigido (Parte 1 - C)

- **Qual era o bug?**  
  Ao chamar `emprestar(id_u, id_l)` informando um `id_u` de usuário que **não existe** no sistema (ex: `"U999"`), a aplicação sofria um erro fatal de execução (`KeyError: 'U999'`) e encerrava o programa abruptamente.

- **Por que acontecia no código legado?**  
  No código original, a primeira linha da função `emprestar` executava o print de log:
  ```python
  print("Processando emprestimo: usuario " + id_u + " CPF " + self.u[id_u]["cpf"] + " livro " + id_l)
  ```
  O acesso `self.u[id_u]["cpf"]` ocorria **ANTES** da validação `if id_u in self.u:` (que estava na linha seguinte). Como a verificação de existência do usuário vinha depois da tentativa de leitura da chave no dicionário `self.u`, a consulta a um usuário inexistente gerava um `KeyError` no `print` antes mesmo de alcançar o teste condicional.

- **Como foi corrigido na refatoração?**  
  Com a aplicação de *Guard Clauses*, invertemos a ordem e colocamos a validação de existência como a primeira linha executável do método:
  ```python
  if usuario_id not in self.usuarios:
      logger.warning("Usuario nao encontrado")
      return False
  ```
  Somente após a confirmação de que o usuário existe no sistema é que o objeto `usuario` é obtido e seu CPF mascarado é lido com total segurança, garantindo que o caminho feliz permaneça no nível 0 e sem riscos de exceção.

# Sistema de Gestão de Biblioteca (Refatoração & POO)

Projeto de refatoração e evolução de um sistema legado de biblioteca acadêmica, aplicando Programação Orientada a Objetos (POO), princípios SOLID (SRP e OCP), privacidade de dados (LGPD), rastreabilidade via `logging` e testes de caracterização.

---

## 📌 Funcionalidades Principais

- **Polimorfismo e Categorias de Usuários (OCP):**
  - Tipos suportados: `Comum`, `Premium`, `Funcionario` e `Professor`.
  - Cada perfil encapsula suas próprias regras de limite de empréstimos, prazos de devolução e taxas de multa por atraso.
- **Ciclo de Empréstimos e Devoluções:**
  - Validações defensivas (*Guard Clauses*) para status de usuário, limites e disponibilidade de acervo.
  - Cálculo automático de multas diárias em caso de atraso na devolução.
- **Fila de Reserva FIFO:**
  - Gerenciamento de lista de espera sequencial (*First In, First Out*) para livros com estoque esgotado.
  - Liberação e notificação imediata do próximo usuário da fila no momento da devolução.
- **Relatórios Gerenciais:**
  - Listagem analítica completa do acervo e situação cadastral dos usuários.
  - Relatório resumido com agregações em tempo real (total de títulos, total de exemplares, empréstimos ativos e empréstimos em atraso).
- **Segurança e Observabilidade:**
  - Anonimização de dados sensíveis (LGPD) com mascaramento de CPF (`********XXXX`).
  - Uso de logger nativo customizado (`logging.Logger`) categorizando fluxos operacionais em `INFO` e `WARNING`.

---

## 🏗️ Arquitetura e Padrões Aplicados

- **SRP (Single Responsibility Principle):** Cada classe possui responsabilidade estrita no domínio (`Livro` cuida do acervo e sua fila de espera; `Usuario` do seu perfil e regras; `Emprestimo` do registro temporal; `Sistema` da orquestração).
- **OCP (Open/Closed Principle):** A introdução de novos perfis de leitor (ex.: `Professor`) é realizada via herança sem modificar as regras de negócio existentes.
- **Factory Pattern:** A função `criar_usuario` desacopla a instanciação das subclasses da camada de regras do sistema.

---

## 📁 Estrutura de Arquivos

- `biblioteca_legado.py`: Código principal contendo as classes de domínio, regras de negócio e cenários de execução.
- `test_sistema.py`: Testes de caracterização automatizados para validação de regressão.
- `README.md`: Documentação operacional do projeto.

---

## ⚙️ Como Executar

### 1. Execução dos Cenários de Demonstração
Para rodar a simulação completa dos 8 cenários operacionais:

```bash
python biblioteca_legado.py
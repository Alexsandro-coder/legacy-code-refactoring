"""
Módulo de Configuração de Logging Centralizado.

Este módulo centraliza a criação e a formatação dos logs do sistema.
Utilizamos a biblioteca padrão `logging` em vez de mensagens com `print()`.

Benefícios da abordagem (Boas Práticas / Aula 5):
1. Permite níveis de severidade (INFO, WARNING, ERROR).
2. Adiciona data, hora e identificador do módulo para facilitar rastreabilidade.
3. Não imprime dados sensíveis dos usuários (respeitando a LGPD).
"""

import logging

def obter_logger(nome: str = "BIBLIOTECA") -> logging.Logger:
    """
    Retorna uma instância configurada do Logger nativo do Python.
    Evita duplicação de handlers se a função for chamada mais de uma vez.
    """
    logger = logging.getLogger(nome)
    logger.setLevel(logging.INFO)

    # Se o logger já tiver handlers associados, não adiciona novos para evitar logs duplicados
    if not logger.handlers:
        handler = logging.StreamHandler()
        # Formato padronizado: Data/Hora [NÍVEL] Módulo: Mensagem
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

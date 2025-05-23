"""
Módulo de utilitários para logging no Data Sentinel.
"""

import logging
import os

def setup_logger(name, level='INFO'):
    """
    Configura um logger com o nível especificado.
    
    Args:
        name (str): Nome do logger
        level (str): Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        logging.Logger: Logger configurado
    """
    # Converte o nível de string para constante do logging
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO
    
    # Configura o logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # Verifica se o logger já tem handlers para evitar duplicação
    if not logger.handlers:
        # Cria um handler para console
        handler = logging.StreamHandler()
        handler.setLevel(numeric_level)
        
        # Define o formato do log
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        # Adiciona o handler ao logger
        logger.addHandler(handler)
    
    return logger

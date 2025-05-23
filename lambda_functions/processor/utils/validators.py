"""
Módulo de utilitários para validação de eventos no Data Sentinel.
"""

import logging
import os

from utils.logger import setup_logger

# Configuração de logging
logger = setup_logger(__name__, os.environ.get('LOG_LEVEL', 'INFO'))

def validate_event(event):
    """
    Valida o evento recebido pela função Lambda.
    
    Args:
        event (dict): Evento a ser validado
        
    Returns:
        bool: True se o evento é válido
        
    Raises:
        ValueError: Se o evento não contém os campos obrigatórios
    """
    logger.debug(f"Validando evento: {event}")
    
    # Verifica se o evento contém os campos obrigatórios
    required_fields = ['file_key', 'requester_email']
    
    for field in required_fields:
        if field not in event:
            error_message = f"Campo obrigatório ausente no evento: {field}"
            logger.error(error_message)
            raise ValueError(error_message)
    
    # Validações específicas
    if not event['file_key'].endswith('.csv'):
        error_message = "O arquivo deve ter extensão .csv"
        logger.error(error_message)
        raise ValueError(error_message)
    
    if '@' not in event['requester_email']:
        error_message = "E-mail do solicitante inválido"
        logger.error(error_message)
        raise ValueError(error_message)
    
    logger.info("Evento validado com sucesso")
    return True

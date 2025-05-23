"""
Lambda Function para notificação de resultados de auditoria via e-mail.
"""

import os
import json
import logging
from datetime import datetime

# Importação dos módulos internos
from email_formatter import EmailFormatter
from dynamodb_reader import DynamoDBReader
from utils.logger import setup_logger

# Configuração de ambiente
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'data-sentinel-audit-results')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

# Configuração de logging
logger = setup_logger(__name__, LOG_LEVEL)

def lambda_handler(event, context):
    """
    Função principal que processa eventos de notificação.
    
    Args:
        event: Evento que acionou a função Lambda (mensagem do SNS)
        context: Contexto de execução da Lambda
        
    Returns:
        dict: Resposta da função Lambda
    """
    logger.info("Iniciando processamento de notificação")
    logger.debug(f"Evento recebido: {json.dumps(event)}")
    
    try:
        # Extração da mensagem do SNS
        if 'Records' in event and len(event['Records']) > 0:
            sns_message = event['Records'][0]['Sns']['Message']
            notification_data = json.loads(sns_message)
        else:
            # Caso a função seja chamada diretamente, sem passar pelo SNS
            notification_data = event
        
        logger.debug(f"Dados de notificação: {json.dumps(notification_data)}")
        
        # Extração de informações da notificação
        audit_id = notification_data.get('audit_id')
        requester_email = notification_data.get('requester_email')
        summary = notification_data.get('summary', {})
        timestamp = notification_data.get('timestamp')
        
        # Validação dos dados
        if not audit_id or not requester_email:
            raise ValueError("Dados de notificação incompletos")
        
        # Inicialização dos handlers
        dynamodb_reader = DynamoDBReader(DYNAMODB_TABLE)
        email_formatter = EmailFormatter()
        
        # Obtenção dos detalhes completos da auditoria, se necessário
        if not summary:
            audit_data = dynamodb_reader.get_audit_result(audit_id, timestamp)
            if not audit_data:
                raise ValueError(f"Auditoria {audit_id} não encontrada")
            summary = audit_data.get('sensitive_data_count', {})
        
        # Formatação do e-mail
        email_content = email_formatter.format_audit_notification({
            'audit_id': audit_id,
            'requester_email': requester_email,
            'summary': summary,
            'timestamp': timestamp
        })
        
        # Envio do e-mail (já realizado pelo SNS)
        logger.info(f"Notificação processada com sucesso para {requester_email}")
        
        # Retorno da resposta
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Notificação processada com sucesso',
                'audit_id': audit_id,
                'requester_email': requester_email
            })
        }
        
    except Exception as e:
        logger.error(f"Erro durante o processamento da notificação: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Erro durante o processamento da notificação: {str(e)}'
            })
        }

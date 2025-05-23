"""
Data Sentinel - Processor Lambda Function

Esta função Lambda é responsável por processar arquivos CSV enviados para auditoria,
identificar dados sensíveis usando StackSpot IA (Quick Commands), armazenar os resultados
no DynamoDB e disparar notificações via SNS.
"""

import os
import json
import uuid
import logging
from datetime import datetime

# Importação dos módulos internos
from stackspot_integration import StackSpotIntegration
from .data_analyzer import DataAnalyzer
from s3_handler import S3Handler
from dynamodb_handler import DynamoDBHandler
from sns_publisher import SNSPublisher
from utils.logger import setup_logger
from utils.validators import validate_event

# Configuração de ambiente
S3_BUCKET = os.environ.get('S3_BUCKET', 'data-sentinel-storage')
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'data-sentinel-audit-results')
SNS_TOPIC = os.environ.get('SNS_TOPIC', 'data-sentinel-notifications')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

# Configuração de logging
logger = setup_logger(__name__, LOG_LEVEL)

def lambda_handler(event, context):
    """
    Função principal que processa o evento de upload de arquivo CSV.
    
    Args:
        event: Evento que acionou a função Lambda
        context: Contexto de execução da Lambda
        
    Returns:
        dict: Resposta da função Lambda
    """
    logger.info("Iniciando processamento de auditoria")
    logger.debug(f"Evento recebido: {json.dumps(event)}")
    
    try:
        # Validação do evento
        validate_event(event)
        
        # Extração de informações do evento
        file_key = event.get('file_key')
        requester_email = event.get('requester_email')
        file_name = file_key.split('/')[-1]
        
        # Geração de ID único para a auditoria
        audit_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Inicialização dos handlers
        s3_handler = S3Handler(S3_BUCKET)
        dynamodb_handler = DynamoDBHandler(DYNAMODB_TABLE)
        sns_publisher = SNSPublisher(SNS_TOPIC)
        
        # Download do arquivo do S3
        local_file_path = f"/tmp/{file_name}"
        s3_handler.download_file(file_key, local_file_path)
        logger.info(f"Arquivo {file_name} baixado para análise")
        
        # Inicialização da integração com StackSpot IA
        stackspot_integration = StackSpotIntegration()
        
        # Análise de dados sensíveis
        data_analyzer = DataAnalyzer(stackspot_integration)
        analysis_result = data_analyzer.analyze_csv(local_file_path)
        logger.info(f"Análise concluída: {len(analysis_result['sensitive_data'])} dados sensíveis encontrados")
        
        # Mascaramento de dados sensíveis para armazenamento
        masked_data = data_analyzer.mask_sensitive_data(analysis_result['sensitive_data'])
        
        # Preparação dos dados para armazenamento no DynamoDB
        audit_data = {
            'audit_id': audit_id,
            'timestamp': timestamp,
            'requester_email': requester_email,
            'file_name': file_name,
            's3_path': file_key,
            'sensitive_data_count': analysis_result['summary'],
            'sensitive_data_details': masked_data,
            'status': 'COMPLETED',
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        # Armazenamento dos resultados no DynamoDB
        dynamodb_handler.save_audit_result(audit_data)
        logger.info(f"Resultados da auditoria {audit_id} salvos no DynamoDB")
        
        # Publicação de notificação no SNS
        notification_message = {
            'audit_id': audit_id,
            'requester_email': requester_email,
            'summary': analysis_result['summary'],
            'timestamp': timestamp
        }
        
        sns_publisher.publish_notification(
            message=json.dumps(notification_message),
            subject=f"Resultado da Auditoria de Dados Sensíveis - {audit_id}"
        )
        logger.info(f"Notificação enviada para o tópico SNS")
        
        # Retorno da resposta
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Auditoria concluída com sucesso',
                'audit_id': audit_id,
                'summary': analysis_result['summary']
            })
        }
        
    except Exception as e:
        logger.error(f"Erro durante o processamento: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Erro durante o processamento: {str(e)}'
            })
        }

"""
Leitor de dados do DynamoDB para o Data Sentinel.
"""

import boto3
import logging
import os
import json
from botocore.exceptions import ClientError
from decimal import Decimal

from lambda_functions.notifier.utils.logger import setup_logger

# Configuração de logging
logger = setup_logger(__name__, os.environ.get('LOG_LEVEL', 'INFO'))

# Helper class para serialização de números decimais no DynamoDB
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

class DynamoDBReader:
    """
    Classe responsável pela leitura de dados do Amazon DynamoDB.
    """
    
    def __init__(self, table_name):
        """
        Inicializa o leitor de DynamoDB.
        
        Args:
            table_name (str): Nome da tabela DynamoDB
        """
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
        logger.info(f"Inicializando DynamoDBReader para a tabela: {table_name}")
        
    def get_audit_result(self, audit_id, timestamp=None):
        """
        Obtém os resultados de uma auditoria.
        
        Args:
            audit_id (str): ID da auditoria
            timestamp (str, optional): Timestamp da auditoria
            
        Returns:
            dict: Dados da auditoria
        """
        logger.info(f"Obtendo resultados da auditoria {audit_id} do DynamoDB")
        
        try:
            # Define a chave para consulta
            key = {'audit_id': audit_id}
            if timestamp:
                key['timestamp'] = timestamp
                
            # Consulta o item na tabela
            response = self.table.get_item(Key=key)
            
            # Verifica se o item foi encontrado
            if 'Item' not in response:
                logger.warning(f"Auditoria {audit_id} não encontrada")
                return None
                
            # Converte os números decimais para float
            item = json.loads(json.dumps(response['Item'], cls=DecimalEncoder))
            
            logger.info(f"Resultados da auditoria obtidos com sucesso")
            return item
            
        except ClientError as e:
            logger.error(f"Erro ao obter resultados da auditoria do DynamoDB: {str(e)}", exc_info=True)
            raise
            
    def list_audits_by_requester(self, requester_email, limit=10):
        """
        Lista auditorias por solicitante.
        
        Args:
            requester_email (str): E-mail do solicitante
            limit (int, optional): Limite de resultados
            
        Returns:
            list: Lista de auditorias
        """
        logger.info(f"Listando auditorias para o solicitante {requester_email}")
        
        try:
            # Cria um índice secundário global para requester_email
            # Nota: Este índice deve ser criado previamente na tabela
            
            # Consulta o índice
            response = self.table.query(
                IndexName='RequesterEmailIndex',
                KeyConditionExpression=boto3.dynamodb.conditions.Key('requester_email').eq(requester_email),
                Limit=limit,
                ScanIndexForward=False  # Ordem decrescente por timestamp
            )
            
            # Converte os números decimais para float
            items = json.loads(json.dumps(response.get('Items', []), cls=DecimalEncoder))
            
            logger.info(f"Encontradas {len(items)} auditorias")
            return items
            
        except ClientError as e:
            logger.error(f"Erro ao listar auditorias no DynamoDB: {str(e)}", exc_info=True)
            raise

import boto3
import logging
import os
import json
from botocore.exceptions import ClientError
from decimal import Decimal
from datetime import datetime
from dotenv import load_dotenv
from lambda_functions.notifier.utils.logger import setup_logger

load_dotenv()

logger = setup_logger(__name__, os.environ.get('LOG_LEVEL', 'INFO'))

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

class DynamoDBHandler:
    """ Classe responsável pelas operações no Amazon DynamoDB. """

    def __init__(self, table_name):
        """ Inicializa o manipulador de DynamoDB. """
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
        logger.info(f"Inicializando DynamoDBHandler para a tabela: {table_name}")

    def save_audit_result(self, audit_data):
        """ Salva os resultados da auditoria no DynamoDB. """
        logger.info(f"Salvando resultados da auditoria {audit_data.get('audit_id')} no DynamoDB")
        try:
            item = json.loads(json.dumps(audit_data), parse_float=Decimal)
            self.table.put_item(Item=item)
            logger.info(f"Resultados da auditoria salvos com sucesso")
            return audit_data.get('audit_id')
        except ClientError as e:
            logger.error(f"Erro ao salvar resultados da auditoria no DynamoDB: {str(e)}", exc_info=True)
            raise

    def get_audit_result(self, audit_id, timestamp=None):
        """ Obtém os resultados de uma auditoria. """
        logger.info(f"Obtendo resultados da auditoria {audit_id} do DynamoDB")
        try:
            key = {'audit_id': audit_id}
            if timestamp:
                key['timestamp'] = timestamp
            response = self.table.get_item(Key=key)
            if 'Item' not in response:
                logger.warning(f"Auditoria {audit_id} não encontrada")
                return None
            item = json.loads(json.dumps(response['Item'], cls=DecimalEncoder))
            logger.info(f"Resultados da auditoria obtidos com sucesso")
            return item
        except ClientError as e:
            logger.error(f"Erro ao obter resultados da auditoria do DynamoDB: {str(e)}", exc_info=True)
            raise

    def update_audit_status(self, audit_id, status, timestamp=None):
        """ Atualiza o status de uma auditoria. """
        logger.info(f"Atualizando status da auditoria {audit_id} para {status}")
        try:
            key = {'audit_id': audit_id}
            if timestamp:
                key['timestamp'] = timestamp
            update_expression = "SET #status = :status, updated_at = :updated_at"
            expression_attribute_names = {'#status': 'status'}
            expression_attribute_values = {
                ':status': status,
                ':updated_at': Decimal(str(datetime.utcnow().timestamp()))
            }
            self.table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values
            )
            logger.info(f"Status da auditoria atualizado com sucesso")
            return True
        except ClientError as e:
            logger.error(f"Erro ao atualizar status da auditoria no DynamoDB: {str(e)}", exc_info=True)
            raise

    def list_audits_by_requester(self, requester_email, limit=10):
        """ Lista auditorias por solicitante. """
        logger.info(f"Listando auditorias para o solicitante {requester_email}")
        try:
            response = self.table.query(
                IndexName='RequesterEmailIndex',
                KeyConditionExpression=boto3.dynamodb.conditions.Key('requester_email').eq(requester_email),
                Limit=limit,
                ScanIndexForward=False
            )
            items = json.loads(json.dumps(response.get('Items', []), cls=DecimalEncoder))
            logger.info(f"Encontradas {len(items)} auditorias")
            return items
        except ClientError as e:
            logger.error(f"Erro ao listar auditorias no DynamoDB: {str(e)}", exc_info=True)
            raise

    def delete_audit(self, audit_id, timestamp=None):
        """ Remove uma auditoria do DynamoDB. """
        logger.info(f"Removendo auditoria {audit_id} do DynamoDB")
        try:
            key = {'audit_id': audit_id}
            if timestamp:
                key['timestamp'] = timestamp
            self.table.delete_item(Key=key)
            logger.info(f"Auditoria removida com sucesso")
            return True
        except ClientError as e:
            logger.error(f"Erro ao remover auditoria do DynamoDB: {str(e)}", exc_info=True)
            raise
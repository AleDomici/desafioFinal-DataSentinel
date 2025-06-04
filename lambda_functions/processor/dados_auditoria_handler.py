import boto3
import os
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv
from lambda_functions.notifier.utils.logger import setup_logger
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

logger = setup_logger(__name__)
load_dotenv()
DYNAMODB_TABLE_RESULT = os.environ.get('DYNAMODB_TABLE_RESULT', 'dados-auditoria')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('dados-auditoria')

class DadosAuditoriaHandler:
    def __init__(self, table_name):
        self.table_name = table_name
        self.dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        self.table = self.dynamodb.Table(self.table_name)

    def list_audits_by_requester(self, email):
        # Supondo que requester_email não é chave primária, use scan + filtro
        response = self.table.scan(
            FilterExpression=Key('requester_email').eq(email)
        )
        return response.get('Items', [])

    def get_latest_audit_by_email(email):
        response = table.query(
            IndexName='requester_email-index',  # Nome do seu GSI
            KeyConditionExpression=Key('requester_email').eq(email),
            ScanIndexForward=False,  # Ordena decrescente
            Limit=1
        )
        items = response.get('Items', [])
        return items[0] if items else None

    # Exemplo de uso
    if __name__ == "__main__":
        latest_audit = get_latest_audit_by_email('datamaskingzup@gmail.com')
        print(latest_audit)

    def delete_audit(self, hash_key, range_key):
        logger.info(f"Removendo auditoria {hash_key} ({range_key}) do DynamoDB")
        try:
            key = {'HASH': hash_key, 'RANGE': range_key}
            self.table.delete_item(Key=key)
            logger.info("Auditoria removida com sucesso")
            return True
        except ClientError as e:
            logger.error(f"Erro ao remover auditoria do DynamoDB: {str(e)}", exc_info=True)
            raise

# handler = DadosAuditoriaHandler(DYNAMODB_TABLE_RESULT)
# audits = handler.list_audits_by_requester('email@exemplo.com')
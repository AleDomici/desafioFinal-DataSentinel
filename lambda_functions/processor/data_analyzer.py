import boto3
import os
from dotenv import load_dotenv

class DataAnalyzer:
    """Classe responsável pela análise de dados sensíveis."""

    def __init__(self, stackspot_client):
        """Inicializa o analisador de dados."""
        # Carregar variáveis de ambiente do arquivo .env
        load_dotenv()

        self.stackspot_client = stackspot_client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')  # Padrão para 'us-east-1' se não for especificado
        )

    def download_csv_from_s3(self, bucket_name, object_key, download_path):
        """Faz o download de um arquivo CSV do S3."""
        self.s3_client.download_file(bucket_name, object_key, download_path)

    def analyze_csv(self, bucket_name, object_key):
        """Analisa um arquivo CSV em busca de dados sensíveis.

        Args:
            bucket_name: Nome do bucket S3.
            object_key: Chave do objeto no S3.

        Returns:
            dict: Resultados da análise.
        """
        download_path = '/tmp/temporary_file.csv'
        self.download_csv_from_s3(bucket_name, object_key, download_path)
        
        with open(download_path, 'r') as file:
            csv_data = file.read()
        
        # Supondo que stackspot_client tem um método analyze_data
        results = self.stackspot_client.analyze_data(csv_data)
        return results

    def mask_sensitive_data(self, data):
        """Mascara dados sensíveis para exibição segura.

        Args:
            data: Dados sensíveis a serem mascarados.

        Returns:
            dict: Dados mascarados.
        """
        # Supondo que stackspot_client tem um método mask_data
        masked_data = self.stackspot_client.mask_data(data)
        return masked_data
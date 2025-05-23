# Estrutura de Código para as Funções Lambda

## Visão Geral

Este documento descreve a estrutura de código para as duas funções Lambda que compõem o Data Sentinel:
1. `data_sentinel_processor`: Responsável pelo processamento e análise de dados sensíveis
2. `data_sentinel_notifier`: Responsável pelo envio de notificações aos solicitantes

## Estrutura de Diretórios

```
data_sentinel/
├── lambda_functions/
│   ├── processor/
│   │   ├── main.py                 # Ponto de entrada da função Lambda
│   │   ├── requirements.txt        # Dependências
│   │   ├── stackspot_integration.py # Integração com StackSpot IA
│   │   ├── data_analyzer.py        # Análise de dados sensíveis
│   │   ├── s3_handler.py           # Manipulação de arquivos no S3
│   │   ├── dynamodb_handler.py     # Operações no DynamoDB
│   │   ├── sns_publisher.py        # Publicação de mensagens no SNS
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py           # Configuração de logs
│   │       └── validators.py       # Validadores de entrada
│   │
│   └── notifier/
│       ├── main.py                 # Ponto de entrada da função Lambda
│       ├── requirements.txt        # Dependências
│       ├── email_formatter.py      # Formatação de e-mails
│       ├── dynamodb_reader.py      # Leitura de dados do DynamoDB
│       └── utils/
│           ├── __init__.py
│           └── logger.py           # Configuração de logs
│
└── tests/
    ├── processor/
    │   ├── test_main.py
    │   ├── test_stackspot_integration.py
    │   ├── test_data_analyzer.py
    │   ├── test_s3_handler.py
    │   └── test_dynamodb_handler.py
    │
    └── notifier/
        ├── test_main.py
        ├── test_email_formatter.py
        └── test_dynamodb_reader.py
```

## Detalhamento dos Módulos

### Lambda Function: Processor

#### main.py
```python
def lambda_handler(event, context):
    """
    Função principal que processa o evento de upload de arquivo CSV.
    
    Args:
        event: Evento que acionou a função Lambda
        context: Contexto de execução da Lambda
        
    Returns:
        dict: Resposta da função Lambda
    """

    pass
```

#### stackspot_integration.py
```python
class StackSpotIntegration:
    """
    Classe responsável pela integração com StackSpot IA usando Quick Commands.
    """
    
    def __init__(self, config):
        """Inicializa a integração com StackSpot."""
        pass
        
    def analyze_sensitive_data(self, file_path):
        """
        Analisa dados sensíveis em um arquivo CSV usando StackSpot IA.
        
        Args:
            file_path: Caminho do arquivo a ser analisado
            
        Returns:
            dict: Resultados da análise
        """
        pass
```

#### data_analyzer.py
```python
class DataAnalyzer:
    """
    Classe responsável pela análise de dados sensíveis.
    """
    
    def __init__(self, stackspot_client):
        """Inicializa o analisador de dados."""
        self.stackspot_client = stackspot_client
        
    def analyze_csv(self, file_path):
        """
        Analisa um arquivo CSV em busca de dados sensíveis.
        
        Args:
            file_path: Caminho do arquivo CSV
            
        Returns:
            dict: Resultados da análise
        """
        pass
        
    def mask_sensitive_data(self, data):
        """
        Mascara dados sensíveis para exibição segura.
        
        Args:
            data: Dados sensíveis a serem mascarados
            
        Returns:
            dict: Dados mascarados
        """
        pass
```

#### s3_handler.py
```python
class S3Handler:
    """
    Classe responsável pela manipulação de arquivos no S3.
    """
    
    def __init__(self, bucket_name):
        """Inicializa o manipulador de S3."""
        self.bucket_name = bucket_name
        
    def upload_file(self, file_path, s3_key):
        """
        Faz upload de um arquivo para o S3.
        
        Args:
            file_path: Caminho do arquivo local
            s3_key: Chave do objeto no S3
            
        Returns:
            str: URL do arquivo no S3
        """
        pass
        
    def download_file(self, s3_key, local_path):
        """
        Faz download de um arquivo do S3.
        
        Args:
            s3_key: Chave do objeto no S3
            local_path: Caminho local para salvar o arquivo
            
        Returns:
            str: Caminho local do arquivo baixado
        """
        pass
```

#### dynamodb_handler.py
```python
class DynamoDBHandler:
    """
    Classe responsável pelas operações no DynamoDB.
    """
    
    def __init__(self, table_name):
        """Inicializa o manipulador de DynamoDB."""
        self.table_name = table_name
        
    def save_audit_result(self, audit_data):
        """
        Salva os resultados da auditoria no DynamoDB.
        
        Args:
            audit_data: Dados da auditoria
            
        Returns:
            str: ID da auditoria
        """
        pass
        
    def get_audit_result(self, audit_id):
        """
        Obtém os resultados de uma auditoria.
        
        Args:
            audit_id: ID da auditoria
            
        Returns:
            dict: Dados da auditoria
        """
        pass
```

#### sns_publisher.py
```python
class SNSPublisher:
    """
    Classe responsável pela publicação de mensagens no SNS.
    """
    
    def __init__(self, topic_arn):
        """Inicializa o publicador de SNS."""
        self.topic_arn = topic_arn
        
    def publish_notification(self, message, subject):
        """
        Publica uma notificação no tópico SNS.
        
        Args:
            message: Mensagem a ser publicada
            subject: Assunto da mensagem
            
        Returns:
            str: ID da mensagem publicada
        """
        pass
```

### Lambda Function: Notifier

#### main.py
```python
def lambda_handler(event, context):
    """
    Função principal que processa eventos de notificação.
    
    Args:
        event: Evento que acionou a função Lambda
        context: Contexto de execução da Lambda
        
    Returns:
        dict: Resposta da função Lambda
    """
    # Implementação do fluxo de notificação
    pass
```

#### email_formatter.py
```python
class EmailFormatter:
    """
    Classe responsável pela formatação de e-mails.
    """
    
    def format_audit_notification(self, audit_data):
        """
        Formata uma notificação de auditoria para envio por e-mail.
        
        Args:
            audit_data: Dados da auditoria
            
        Returns:
            dict: Mensagem formatada para e-mail
        """
        pass
```

#### dynamodb_reader.py
```python
class DynamoDBReader:
    """
    Classe responsável pela leitura de dados do DynamoDB.
    """
    
    def __init__(self, table_name):
        """Inicializa o leitor de DynamoDB."""
        self.table_name = table_name
        
    def get_audit_result(self, audit_id):
        """
        Obtém os resultados de uma auditoria.
        
        Args:
            audit_id: ID da auditoria
            
        Returns:
            dict: Dados da auditoria
        """
        pass
```

## Integração com StackSpot IA

A integração com StackSpot IA é realizada através do módulo `stackspot_integration.py`, que utiliza o recurso Quick Commands para identificar dados sensíveis. A implementação seguirá as melhores práticas recomendadas pela documentação do StackSpot.

### Exemplo de Uso do Quick Commands

```python
from stackspot import QuickCommands

def analyze_with_stackspot(file_path):
    # Inicializa o cliente StackSpot
    quick_commands = QuickCommands()
    
    # Executa o comando de análise de dados sensíveis
    result = quick_commands.execute(
        command="analyze-sensitive-data",
        args={"file": file_path}
    )
    
    return result
```

## Tratamento de Erros

Todas as classes e funções implementarão tratamento de erros adequado, com logs detalhados para facilitar a depuração. Os erros serão categorizados em:

1. **Erros de Validação**: Problemas com os dados de entrada
2. **Erros de Integração**: Falhas na comunicação com serviços externos
3. **Erros de Processamento**: Falhas durante o processamento dos dados
4. **Erros de Sistema**: Falhas de infraestrutura ou ambiente

## Testes

Os testes unitários e de integração serão implementados para todas as classes e funções, garantindo a qualidade e confiabilidade do código. Serão utilizados mocks para simular os serviços AWS e a integração com StackSpot IA.

## Dependências

### Processor Lambda

```
boto3==1.26.0
stackspot-sdk==1.0.0
pandas==1.5.3
python-dotenv==1.0.0
```

### Notifier Lambda

```
boto3==1.26.0
python-dotenv==1.0.0
```

## Configuração de Ambiente

As configurações sensíveis, como nomes de buckets, tabelas e tópicos SNS, serão armazenadas como variáveis de ambiente nas funções Lambda, seguindo as melhores práticas de segurança.

```python
# Exemplo de configuração de ambiente
import os

S3_BUCKET = os.environ.get('S3_BUCKET')
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE')
SNS_TOPIC = os.environ.get('SNS_TOPIC')
```

## Considerações de Segurança

1. Todos os dados sensíveis serão mascarados antes de serem armazenados ou transmitidos
2. As permissões das funções Lambda seguirão o princípio do menor privilégio
3. A comunicação entre os serviços será criptografada
4. Os logs não conterão informações sensíveis
5. A autenticação para acesso aos detalhes da auditoria será implementada usando JWT

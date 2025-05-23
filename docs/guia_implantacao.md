# Guia de Implantação do Data Sentinel

## Visão Geral

Este documento fornece instruções detalhadas para a implantação do Data Sentinel, uma solução de auditoria automatizada para identificação de dados sensíveis não mascarados em arquivos CSV, utilizando AWS e StackSpot IA.

## Pré-requisitos

1. Conta AWS com permissões para criar:
   - Funções Lambda
   - Buckets S3
   - Tabelas DynamoDB
   - Tópicos SNS
   - Roles IAM

2. AWS CLI configurada localmente
3. Python 3.9 ou superior
4. StackSpot CLI instalada e configurada

## Estrutura do Projeto

```
data_sentinel/
├── docs/
│   ├── arquitetura.md
│   └── estrutura_codigo.md
├── lambda_functions/
│   ├── processor/
│   │   ├── main.py
│   │   ├── stackspot_integration.py
│   │   ├── data_analyzer.py
│   │   ├── s3_handler.py
│   │   ├── dynamodb_handler.py
│   │   ├── sns_publisher.py
│   │   └── utils/
│   │       ├── logger.py
│   │       └── validators.py
│   └── notifier/
│       ├── main.py
│       ├── email_formatter.py
│       ├── dynamodb_reader.py
│       └── utils/
│           └── logger.py
└── templates/
    └── cloudformation.yaml
```

## Passos para Implantação

### 1. Configuração do Ambiente AWS

#### 1.1. Criar Bucket S3

```bash
aws s3api create-bucket --bucket data-sentinel-storage --region us-east-1
```

#### 1.2. Criar Tabela DynamoDB

```bash
aws dynamodb create-table \
    --table-name data-sentinel-audit-results \
    --attribute-definitions \
        AttributeName=audit_id,AttributeType=S \
        AttributeName=timestamp,AttributeType=S \
        AttributeName=requester_email,AttributeType=S \
    --key-schema \
        AttributeName=audit_id,KeyType=HASH \
        AttributeName=timestamp,KeyType=RANGE \
    --global-secondary-indexes \
        "[{\"IndexName\": \"RequesterEmailIndex\",\"KeySchema\": [{\"AttributeName\": \"requester_email\",\"KeyType\": \"HASH\"},{\"AttributeName\": \"timestamp\",\"KeyType\": \"RANGE\"}],\"Projection\": {\"ProjectionType\": \"ALL\"},\"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5,\"WriteCapacityUnits\": 5}}]" \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region us-east-1
```

#### 1.3. Criar Tópico SNS

```bash
aws sns create-topic --name data-sentinel-notifications --region us-east-1
```

### 2. Preparação das Funções Lambda

#### 2.1. Função Processor

1. Navegue até o diretório da função Processor:

```bash
cd data_sentinel/lambda_functions/processor
```

2. Instale as dependências:

```bash
pip install -r requirements.txt -t .
```

3. Crie um arquivo ZIP para implantação:

```bash
zip -r ../processor.zip .
```

#### 2.2. Função Notifier

1. Navegue até o diretório da função Notifier:

```bash
cd data_sentinel/lambda_functions/notifier
```

2. Instale as dependências:

```bash
pip install -r requirements.txt -t .
```

3. Crie um arquivo ZIP para implantação:

```bash
zip -r ../notifier.zip .
```

### 3. Implantação das Funções Lambda

#### 3.1. Criar Role IAM para as Funções Lambda

```bash
# Crie um arquivo de política de confiança
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Crie a role
aws iam create-role --role-name data-sentinel-lambda-role --assume-role-policy-document file://trust-policy.json

# Anexe as políticas necessárias
aws iam attach-role-policy --role-name data-sentinel-lambda-role --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
aws iam attach-role-policy --role-name data-sentinel-lambda-role --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
aws iam attach-role-policy --role-name data-sentinel-lambda-role --policy-arn arn:aws:iam::aws:policy/AmazonSNSFullAccess
aws iam attach-role-policy --role-name data-sentinel-lambda-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

#### 3.2. Criar Função Lambda Processor

```bash
aws lambda create-function \
    --function-name data-sentinel-processor \
    --runtime python3.9 \
    --handler main.lambda_handler \
    --role arn:aws:iam::<ACCOUNT_ID>:role/data-sentinel-lambda-role \
    --zip-file fileb://data_sentinel/lambda_functions/processor.zip \
    --environment Variables="{S3_BUCKET=data-sentinel-storage,DYNAMODB_TABLE=data-sentinel-audit-results,SNS_TOPIC=arn:aws:sns:us-east-1:<ACCOUNT_ID>:data-sentinel-notifications}" \
    --timeout 30 \
    --memory-size 256 \
    --region us-east-1
```

#### 3.3. Criar Função Lambda Notifier

```bash
aws lambda create-function \
    --function-name data-sentinel-notifier \
    --runtime python3.9 \
    --handler main.lambda_handler \
    --role arn:aws:iam::<ACCOUNT_ID>:role/data-sentinel-lambda-role \
    --zip-file fileb://data_sentinel/lambda_functions/notifier.zip \
    --environment Variables="{DYNAMODB_TABLE=data-sentinel-audit-results}" \
    --timeout 30 \
    --memory-size 256 \
    --region us-east-1
```

#### 3.4. Configurar Trigger SNS para a Função Notifier

```bash
aws lambda add-permission \
    --function-name data-sentinel-notifier \
    --statement-id sns-trigger \
    --action lambda:InvokeFunction \
    --principal sns.amazonaws.com \
    --source-arn arn:aws:sns:us-east-1:<ACCOUNT_ID>:data-sentinel-notifications \
    --region us-east-1

aws sns subscribe \
    --topic-arn arn:aws:sns:us-east-1:<ACCOUNT_ID>:data-sentinel-notifications \
    --protocol lambda \
    --notification-endpoint arn:aws:lambda:us-east-1:<ACCOUNT_ID>:function:data-sentinel-notifier \
    --region us-east-1
```

### 4. Configuração do StackSpot IA

1. Instale a CLI do StackSpot:

```bash
pip install stackspot-cli
```

2. Configure a CLI com suas credenciais:

```bash
stackspot config set api-key <YOUR_STACKSPOT_API_KEY>
```

3. Verifique a instalação:

```bash
stackspot --version
```

### 5. Teste da Solução

#### 5.1. Criar um Arquivo CSV de Teste

```bash
cat > test.csv << EOF
id,nome,email,cpf,telefone
1,João Silva,joao@email.com,123.456.789-00,(11) 98765-4321
2,Maria Santos,maria@email.com,987.654.321-00,(21) 91234-5678
3,Pedro Oliveira,pedro@email.com,111.222.333-44,(31) 92345-6789
EOF
```

#### 5.2. Fazer Upload do Arquivo para o S3

```bash
aws s3 cp test.csv s3://data-sentinel-storage/uploads/test.csv
```

#### 5.3. Invocar a Função Lambda Processor

```bash
aws lambda invoke \
    --function-name data-sentinel-processor \
    --payload '{"file_key": "uploads/test.csv", "requester_email": "seu-email@exemplo.com"}' \
    response.json
```

#### 5.4. Verificar os Resultados

1. Verifique o e-mail de notificação
2. Consulte os resultados no DynamoDB:

```bash
aws dynamodb scan --table-name data-sentinel-audit-results
```

## Integração com Aplicações Existentes

Para integrar o Data Sentinel com aplicações existentes, você pode:

1. Invocar a função Lambda Processor diretamente via AWS SDK
2. Configurar um trigger S3 para invocar a função automaticamente quando um arquivo for carregado
3. Criar uma API REST usando API Gateway para expor a funcionalidade

## Considerações de Segurança

1. Certifique-se de que as permissões IAM sigam o princípio do menor privilégio
2. Ative a criptografia em repouso para o bucket S3 e a tabela DynamoDB
3. Configure políticas de ciclo de vida para gerenciar a retenção de dados
4. Implemente autenticação JWT para acesso aos detalhes da auditoria
5. Monitore os logs do CloudWatch para detectar atividades suspeitas

## Solução de Problemas

### Logs do CloudWatch

Para visualizar os logs das funções Lambda:

```bash
aws logs get-log-events \
    --log-group-name /aws/lambda/data-sentinel-processor \
    --log-stream-name <LOG_STREAM_NAME>
```

### Erros Comuns

1. **Erro de permissão**: Verifique se a role IAM tem todas as permissões necessárias
2. **Timeout**: Aumente o timeout da função Lambda se necessário
3. **Erro de integração com StackSpot**: Verifique se a API key está configurada corretamente
4. **Erro de formato de arquivo**: Certifique-se de que o arquivo CSV está no formato correto

## Próximos Passos

1. Implementar uma interface web para upload de arquivos e visualização de resultados
2. Adicionar suporte para mais tipos de arquivos (Excel, JSON, etc.)
3. Implementar mascaramento automático de dados sensíveis
4. Configurar alertas de segurança para notificar administradores sobre violações de compliance

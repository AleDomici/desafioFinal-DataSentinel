# Estrutura de Código do Data Sentinel

## Visão Geral

Este documento descreve a estrutura de código do projeto Data Sentinel, detalhando tanto as funções Lambda quanto a aplicação FastAPI (`app.py`) que serve como interface para interação.

## Estrutura de Diretórios Principal

```
data_sentinel/
├── .gitignore                  # Arquivo de configuração do Git para ignorar arquivos
├── app.py                      # Aplicação FastAPI para endpoints REST
├── README.md                   # Documentação principal do projeto
├── docs/
│   ├── arquitetura.md
│   ├── estrutura_codigo.md     # Este arquivo
│   ├── guia_implantacao.md
│   └── FLUXOGRAMADESAFIOFINALSQUAD2.drawio.png # Imagem do diagrama
├── lambda_functions/
│   ├── processor/              # Código da Lambda de processamento
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   ├── data_analyzer.py
│   │   ├── dynamodb_handler.py
│   │   ├── s3_handler.py
│   │   └── utils/
│   │       ├── logger.py
│   │       └── validators.py
│   └── notifier/               # Código da Lambda de notificação
│       ├── main.py
│       ├── requirements.txt
│       ├── dynamodb_reader.py
│       ├── email_formatter.py
│       └── utils/
│           └── logger.py
└── tests/                      # Testes unitários e de integração (estrutura exemplo)
    ├── processor/
    └── notifier/
```

*(Nota: Os módulos `stackspot_integration.py` e `sns_publisher.py` mencionados anteriormente na documentação não estão presentes na estrutura atual do diretório `processor`.)*

## Aplicação FastAPI (`app.py`)

A aplicação `app.py` utiliza o framework FastAPI para expor endpoints REST que permitem a interação com o sistema Data Sentinel. Ela é responsável por receber uploads de arquivos, consultar auditorias e, potencialmente, gerenciar dados.

### Principais Funcionalidades:

*   **Upload de Arquivos (`POST /arquivos`):**
    *   Recebe um arquivo CSV e um e-mail do solicitante via formulário.
    *   Valida se o arquivo é CSV e se o tamanho não excede 5MB.
    *   Valida o formato do e-mail utilizando a biblioteca `email-validator`.
    *   Salva o arquivo temporariamente.
    *   Realiza o upload do arquivo para o bucket S3 configurado usando `S3Handler`.
    *   Registra os metadados da auditoria (incluindo `audit_id`, `timestamp`, `requester_email`, `file_name`, `s3_path`, `status='PENDING'`) no DynamoDB usando `DynamoDBHandler`.
    *   Retorna uma mensagem de sucesso.
*   **Consulta de Auditorias (`GET /dados-sensiveis`):**
    *   Recebe um e-mail como parâmetro de query.
    *   Utiliza `DynamoDBHandler` para buscar todas as auditorias associadas ao e-mail fornecido.
    *   Retorna a lista de auditorias encontradas.
*   **Deleção de Auditorias (`DELETE /dados-sensiveis`):**
    *   *(Implementação atual parece ser para teste/limpeza, buscando por um e-mail fixo "example@domain.com")*
    *   Busca auditorias associadas ao e-mail fixo.
    *   Utiliza `DynamoDBHandler` para deletar cada auditoria encontrada.
    *   Retorna uma mensagem de sucesso.

### Dependências e Configuração:

*   Utiliza `FastAPI`, `UploadFile`, `File`, `Form`, `HTTPException`, `Query`.
*   Integra os handlers `DynamoDBHandler` e `S3Handler` da pasta `lambda_functions/processor`.
*   Utiliza o `setup_logger` de `lambda_functions/processor/utils/logger.py`.
*   Carrega variáveis de ambiente usando `python-dotenv` (espera um arquivo `.env`).
*   Requer as variáveis de ambiente `DYNAMODB_TABLE` e `S3_BUCKET`.

## Detalhamento dos Módulos Lambda

### Lambda Function: Processor (`lambda_functions/processor`)

Responsável pelo processamento principal da auditoria.

*   **`main.py`**: Ponto de entrada da função Lambda. Orquestra a chamada aos outros módulos para baixar o arquivo do S3 (se aplicável, dependendo do trigger), analisar dados, interagir com StackSpot (se implementado) e salvar resultados.
*   **`data_analyzer.py`**: Contém a lógica para análise do arquivo CSV e identificação/mascaramento de dados sensíveis (potencialmente usando StackSpot).
*   **`dynamodb_handler.py`**: Classe para interagir com a tabela DynamoDB (salvar, obter, listar, deletar registros de auditoria). Inclui a funcionalidade de criar a tabela automaticamente se ela não existir.
*   **`s3_handler.py`**: Classe para realizar operações no S3 (upload, download de arquivos).
*   **`utils/logger.py`**: Configuração padronizada do logger para a função.
*   **`utils/validators.py`**: Funções utilitárias para validações diversas (ex: validação de e-mail, formato de dados).
*   **`requirements.txt`**: Lista as dependências Python específicas desta função.

### Lambda Function: Notifier (`lambda_functions/notifier`)

Responsável por notificar os usuários sobre os resultados da auditoria.

*   **`main.py`**: Ponto de entrada da função Lambda. Recebe o evento (ex: do DynamoDB Stream ou SNS), busca os detalhes da auditoria e envia a notificação.
*   **`dynamodb_reader.py`**: Classe específica para leitura de dados da tabela DynamoDB (embora `DynamoDBHandler` no processor também tenha métodos de leitura, esta pode ser uma versão simplificada ou específica para o notifier).
*   **`email_formatter.py`**: Classe para formatar o conteúdo da notificação por e-mail com base nos dados da auditoria.
*   **`utils/logger.py`**: Configuração padronizada do logger para a função.
*   **`requirements.txt`**: Lista as dependências Python específicas desta função.

## Integração com StackSpot IA

A integração com StackSpot IA, mencionada na documentação de arquitetura, seria implementada principalmente dentro do `data_analyzer.py` na função `processor`. Utilizaria Quick Commands para identificar os padrões de dados sensíveis no arquivo CSV processado.

## Configuração de Ambiente (`.env`)

O projeto utiliza a biblioteca `python-dotenv` para carregar variáveis de ambiente, indicando a expectativa de um arquivo `.env` na raiz do projeto ou no diretório de execução. No entanto, **este arquivo `.env` não está presente no repositório**. As variáveis de ambiente esperadas, com base no código (`app.py` e possivelmente nas Lambdas), são:

*   `DYNAMODB_TABLE`: Nome da tabela DynamoDB onde os resultados da auditoria são armazenados.
*   `S3_BUCKET`: Nome do bucket S3 usado para armazenar os arquivos CSV originais.
*   `SNS_TOPIC` (Potencialmente): ARN do tópico SNS usado para disparar a função `notifier` (se a arquitetura usar SNS entre as Lambdas).

É crucial criar um arquivo `.env` localmente ou configurar essas variáveis diretamente no ambiente de execução (ex: configurações da Lambda na AWS) para o correto funcionamento da aplicação e das funções.

## Tratamento de Erros e Logging

Ambas as funções Lambda e a aplicação FastAPI utilizam um logger configurado através dos módulos `utils/logger.py`. O tratamento de erros é implementado nos endpoints da API (`app.py`) e deve ser robusto dentro das funções Lambda para capturar exceções durante o processamento, interações com AWS ou StackSpot.

## Testes

A pasta `tests/` sugere a intenção de incluir testes unitários e de integração, que são fundamentais para garantir a qualidade e a confiabilidade do código. Recomenda-se o uso de mocks para simular serviços AWS e interações externas durante os testes.

## Considerações de Segurança

*   Gerenciamento seguro de credenciais AWS.
*   Configuração de permissões IAM com o princípio do menor privilégio para as Lambdas e a aplicação.
*   Validação rigorosa das entradas (arquivos, e-mails).
*   Mascaramento de dados sensíveis nos logs e resultados armazenados.
*   Uso de HTTPS para os endpoints da API.


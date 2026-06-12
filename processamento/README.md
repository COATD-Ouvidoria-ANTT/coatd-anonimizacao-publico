# Pasta Processamento - Documentação Técnica

## Visão Geral

A pasta `processamento` é o núcleo operacional do projeto de anonimização de dados. Ela contém toda a lógica necessária para transformar dados brutos coletados da plataforma de ouvidoria em dados prontos para a etapa de rotulação de texto. Essa rotulação servirá para o fine-tuning (treinamento especializado) do nosso modelo NER (Inteligência Artificial que reconhece nomes, empresas e endereços).

O fluxo desta pasta segue o seguinte padrão: dados brutos são ingeridos, passam por processamento automático utilizando expressões regulares e modelos de Processamento de Linguagem Natural, geram um relatório em um arquivo PDF e por fim enviam dados para a próxima etapa, a rotulagem do modelo.

## Estrutura de Diretórios

```         
processamento/
├── .env                           # Arquivo de variáveis de ambiente
├── docker-compose.yml             # Configuração do container Docker
├── data/                          # Diretório de armazenamento de dados
│   ├── raw/                       # Dados brutos (entrada)
│   └── processed/                 # Dados processados (intermediários)
├── scripts/                       # Scripts de processamento
│   └── qmd/                       # Documentos Quarto Markdown
│       └── tratamento_falabr.qmd  # Script principal de tratamento
└── outputs/                       # Resultados finais
    └── pdf/                       # Arquivos PDF gerados
```

## Funcionalidade de Cada Componente

### 1. Arquivo `docker-compose.yml` (Orquestração em Container)

Define o ambiente containerizado onde o processamento é executado. Configurações principais:

- **Serviço**: `motor-processamento`
- **Imagem**: `motor-anonimizacao-base` (imagem Docker personalizada com todas as dependências)
- **Container**: `pipeline-processamento`
- **Variáveis de Ambiente**: Carregadas do arquivo `.env`
- **Volumes Montados**:
  - ABNT, rme e \_quarto.yml da raiz do projeto
  - Pastas data, scripts e outputs do processamento
- **Diretório de Trabalho**: `/app` dentro do container
- **Comando de Execução**: Renderiza o documento Quarto e move os PDFs gerados

### 2. Diretório `data/` (Gerenciamento de Dados)

#### Subpasta `raw/`

Armazena os dados brutos obtidos diretamente da API de ouvidoria. Tipicamente incluem: - ID das Manifestações registradas na ouvidoria

#### Subpasta `processed/`

Armazena dados intermediários resultantes das etapas de processamento. Estes arquivos são gerados durante a execução do script e servem como ponto de transição entre dados brutos e o relatório final.

### 3. Diretório `scripts/qmd/` (Lógica de Processamento)

#### Arquivo `tratamento_falabr.qmd`

Este é o arquivo central que orquestra todo o processo de anonimização. É um documento Quarto Markdown, que combina código Python com documentação técnica estruturada.

**Funções Principais**:

1.  **Importação de Bibliotecas**:
    - pandas: manipulação de dados estruturados
    - spacy: processamento de linguagem natural
    - requests: requisições HTTP para APIs
    - regex (re): expressões regulares para identificação de padrões
    - torch e transformers: modelos de deep learning
2.  **Autenticação e Ingestão de Dados**:
    - Utiliza o TOKEN_API_OUVIDORIA do arquivo .env
    - Consome dados da API de ouvidoria em lotes
3.  **Identificação de Entidades Sensíveis**:
    - Aplica expressões regulares para padrões específicos (CPF, CNPJ, etc)
4.  **Anonimização de Dados**:
    - Substitui informações identificáveis por marcadores genéricos (ex: \[ANONIMIZADO\])
    - Mantém a estrutura e contexto dos dados
    - Garante que dados relacionados entre si sejam consistentemente anonimizados
5.  **Fatiamento do Texto (Chunking)**:
    - Fatiamento do texto utilizando o modelo `pt_core_news_lg`.
6.  **Geração de Relatório**:
    - Compila estatísticas do processamento
    - Cria visualizações dos dados tratados
    - Exporta o resultado como PDF

### 4. Diretório `outputs/pdf/` (Resultados)

Armazena os arquivos PDF gerados após o processamento. Estes documentos contêm:

- Relatório estruturado com os dados gerados pelo pipeline
- Gráficos e visualizações de análise
- Metadados sobre o processamento realizado
- Estatísticas sobre entidades mascaradas

## Como Utilizar

### Pré-requisitos

- Docker instalado e em execução
- Docker Compose instalado
- Acesso à rede (para consumir a API de ouvidoria)
- Arquivo `.env` devidamente configurado com token válido

### Executando o Processamento

1.  **Crie o arquivo `.env`**: Na raiz da pasta `processamento`/, crie um arquivo vazio chamado `.env`. Abra-o em um editor de texto, adicione a varíavel `TOKEN_API_OUVIDORIA`. Se atente ao tipo de arquivo, ele não pode possuir nenhum tipo, sendo apenas `.env`. 

  - Exemplo Correto: `.env`
  - Exemplo Incorreto: `.env.txt`

- Abra-o em um editor de texto, adicione a varíavel `TOKEN_API_OUVIDORIA` e adicione o seu token de acesso da API após o `=`, assim como no exemplo abaixo.

``` bash
TOKEN_API_OUVIDORIA=insira_seu_token_valido_aqui
```

2.  **Navegue até o diretório processamento**:

``` bash
cd processamento
```

3.  **Inicie o container Docker**:

``` bash
docker-compose up
```

O Docker Compose irá: - Montar todos os volumes - Executar o comando de renderização do Quarto - Gerar o arquivo PDF em `outputs/pdf/`

4.  **Acompanhe o progresso**: O terminal exibirá os logs do processamento em tempo real (download de lotes, aplicação de RegEx/NER e chunking do texto). Aguarde até que o terminal indique que o comando foi finalizado com sucesso.

5.  **Verifique os resultados**: Os arquivos PDF processados estarão disponíveis em `outputs/pdf/`.

## Fluxo de Dados

```         
API Ouvidoria (Dados Brutos)
        ↓
Autenticação Segura [Token do .env]
        ↓
Coleta e Importação de Dados
        ↓
Identificação de Padrões (Regex)
        ↓
Divisão do Texto em Partes Menores (Chunking)
        ↓
Exportação para Pasta rme/ (Rotulação do Texto)
        ↓
Salvamento de backup dos dados na pasta data/processed/
        ↓
Geração do Relatório Final em PDF
```

## Dependências Externas

As seguintes bibliotecas Python são utilizadas (especificadas em `requirements.txt`):

- **pandas**: Manipulação e transformação de dados tabulares
- **requests**: Requisições HTTP para APIs externas
- **spacy**: Processamento de linguagem natural e extração de entidades
- **transformers**: Acesso a modelos de deep learning pré-treinados
- **torch**: Framework de machine learning (backend do transformers)
- **regex (re)**: Expressões regulares para padrões customizados
- **plotly, matplotlib, seaborn**: Visualizações de dados
- **python-dotenv**: Carregamento de variáveis de ambiente

## Tratamento de Erros Comuns

### Erro: "Token inválido ou expirado"

- Verifique se o TOKEN_API_OUVIDORIA no `.env` é válido e não expirou
- Solicite um novo token ao administrador do sistema

### Erro: "Imagem Docker não encontrada"

- Execute: `docker build -t motor-anonimizacao-base .` na pasta raiz do projeto antes de executar a etapa `processamento/`.

### Processamento muito lento

- Aumente recursos alocados ao Docker (CPU/memória)

## Próximas Etapas do Projeto

Após o processamento nesta pasta, os dados preparados para rotulação serão exportados para a pasta `rme/`. A próxima etapa consiste nos seguintes tópicos:

- Rotulação Manual de Entidades (RME)
- Preparação da base anotada para futuro fine-tuning do modelo

## Contato e Suporte

Para dúvidas sobre o funcionamento desta pasta ou reportar problemas, consulte a documentação adicional nas pastas irmãs ou contacte o time de desenvolvimento da COATD.
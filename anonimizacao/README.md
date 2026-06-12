# Pasta Pipeline de Anonimização - Documentação Técnica

## Visão Geral

Esta pasta contém o pipeline principal e definitivo de processamento e anonimização de dados da Ouvidoria da ANTT. É o motor que consolida todas as etapas do projeto em um fluxo contínuo, unindo regras lógicas à Inteligência Artificial.

O objetivo deste pipeline é garantir a conformidade com a Lei Geral de Proteção de Dados (LGPD), ofuscando Informações Pessoais Identificáveis (PII) sem perder o contexto analítico das manifestações. Para garantir a segurança absoluta das informações, **todo o processamento é executado de forma estritamente local (*on-premises*)**, sem qualquer envio de dados para servidores externos ou serviços de LLM em nuvem.

O pipeline utiliza uma abordagem híbrida de alta eficiência:

1.  **Camada Estática (Regex):** Rápida e determinística, remove padrões fixos como CPFs, e-mails e placas de veículos.
2.  **Camada Estocástica (Deep Learning / NER):** O modelo treinado nas etapas anteriores analisa o contexto da frase para encontrar nomes próprios, empresas e endereços que não possuem formato fixo.

## Estrutura de Diretórios

```         
anonimizacao/
├── data/                                   # Diretório de armazenamento de dados
│   ├── raw/                                # Dados de entrada
│   │   └── txt/                            # Diretório de dados textuais
│   │       └── ids_manifestacoes.txt       # IDs extraídos da API do Fala.BR
│   └── processed/                          # Dados de saída (Anonimizados)
│       ├── csv/                            # Exportação em texto delimitado
│       │   └── data_anonimizado.csv        # Arquivo final com texto anonimizado
│       └── xlsx/                           # Exportação para planilhas
│           └── data_anonimizado.xlsx       # Arquivo final com texto anonimizado
├── outputs/                                # Resultados visuais e gerenciais
│   └── pdf/                                # Arquivos do Relatório de Treinamento
│       └── relatorio_pipeline.pdf          # Relatório gerado com métricas de ofuscação
└── scripts/                                # Lógica de processamento
    └── qmd/                                # Documentos Quarto Markdown
        └── pipeline_anonimizacao.qmd       # Script central que orquestra todo o fluxo
```

------------------------------------------------------------------------

## Funcionalidade de Cada Etapa do Processamento

O script central (`pipeline_anonimizacao.qmd`) é dividido em blocos lógicos executados sequencialmente:

### 1. Extração de Dados (API Fala.BR)

O sistema se autentica na API do Fala.BR utilizando credenciais seguras e realiza a ingestão das manifestações do dia. O processo primeiro coleta as chaves identificadoras (`IdManifestacao`) e depois busca o teor textual de cada registro, montando a base de trabalho bruta.

### 2. Diagnóstico e Limpeza Prévia

Realiza uma análise exploratória rápida para verificar se há dados nulos ou erros de formatação. Remove espaços em branco excessivos e caracteres de pontuação duplicados que poderiam confundir a Inteligência Artificial.

### 3. Aplicação de Expressões Regulares (Regex)

Varre o texto em busca de padrões matematicamente definíveis. Se encontrar um e-mail, um link, um CPF, CNPJ, RG, CEP, Telefone ou Placa Veicular, o sistema aplica imediatamente a máscara `[ANONIMIZADO]`.

### 4. Segmentação de Sentenças (*Chunking*)

Modelos de Inteligência Artificial baseados em Transformers (como o BERT) possuem um limite de leitura (geralmente 512 *tokens/subwords* por vez). Para que textos muito longos não sejam cortados pela metade, o pipeline usa o `spaCy` para dividir a manifestação de forma inteligente, quebrando-a no final de cada frase (ponto final), sem perder o contexto gramatical.

### 5. Inferência do Modelo NER (Inteligência Artificial)

As frases cortadas são enviadas para o nosso modelo treinado localmente (`model-best`). O modelo lê a frase, compreende o contexto e identifica nomes de pessoas, empresas e localidades, substituindo-os pelas tags de proteção correspondentes (ex: `[NOME]`, `[EMPRESA]`).

### 6. Recomposição e Exportação

O script junta todas as frases anonimizadas de volta em seus textos originais completos. Em seguida, exporta a base final e limpa para formatos acessíveis (`.csv` e `.xlsx`), além de gerar gráficos mostrando o volume de dados sensíveis bloqueados no dia.

------------------------------------------------------------------------

## Fluxo de Dados

```         
API Fala.BR (Dados Brutos)
        ↓
Ingestão Local Segura [Token .env]
        ↓
Camada Estática: Limpeza + Regex (Ofuscação de CPF, CNPJ, E-mail, etc.)
        ↓
Chunking: Divisão inteligente do texto em blocos menores
        ↓
Camada Estocástica: IA / Modelo NER (Ofuscação de Nomes, Empresas, etc.)
        ↓
Reconstrução das manifestações tratadas
        ↓
Exportação Final (.csv, .xlsx e relatório em .pdf)
```

------------------------------------------------------------------------

## Como Executar o Pipeline

**Pré-requisitos:**

- Certifique-se de que o modelo treinado (`model-best`) gerado na etapa anterior está corretamente posicionado na pasta `ner/models/v1_modelo_inicial/`. O modelo não foi copiado para a pasta `anonimização/` devido a questão do tamnho do arquivo, normalmente modelos são arquivos pesados, então para não ocupar um espaço desnecessário o modelo foi mantido na pasta `ner/models/` e apontado como um volume durante a criação do container.

- Tenha o arquivo `.env` na raiz do projeto contendo o `TOKEN_API_OUVIDORIA` válido. Caso tenha treinado o modelo, esse arquivo já foi criado previamente na pasta `processamento/`, apenas copie para a raiz da pasta `anonimizacao/`. Em caso de não ter percorrido a ordem cronológica das pastas, siga o processo do próximo item.

- Crie o arquivo `.env`: Na raiz da pasta `anonimizacao/`, crie um arquivo vazio chamado `.env`, se atente ao tipo de arquivo, ele não pode possuir nenhum tipo, sendo apenas `.env`.

  - Exemplo Correto: `.env`
  - Exemplo Incorreto: `.env.txt`

- Abra-o em um editor de texto, adicione a varíavel `TOKEN_API_OUVIDORIA` e adicione o seu token de acesso da API após o `=`, assim como no exemplo abaixo.

``` bash
TOKEN_API_OUVIDORIA=insira_seu_token_valido_aqui
```

1.  **Navegue até a pasta do pipeline:** Abra o seu terminal e acesse a pasta correspondente:

``` bash
cd anonimizacao
```

2.  **Inicie o container Docker**:

``` bash
docker-compose up
```

1.  **Verifique as Saídas:** Após a conclusão, os dados limpos e prontos para uso seguro pela equipe estarão disponíveis em `data/processed/xlsx/` e `data/processed/csv/` (Separador ";"). Por fim, o relatório de impacto estará na pasta `outputs/pdf/`.

------------------------------------------------------------------------

## Dependências Externas

As seguintes bibliotecas e ferramentas formam a base operacional deste pipeline:

- **pandas & matplotlib/seaborn:** Utilizados para a manipulação dos dados tabulares e geração dos gráficos de volumetria de anonimização.
- **requests & python-dotenv:** Responsáveis pela comunicação segura com a API do Fala.BR e gerenciamento do token de acesso.
- **regex (re):** Motor de expressões regulares para a aplicação da camada estática de ofuscação de padrões fixos.
- **spaCy** Arquitetura central responsável pelo fatiamento sintático (*chunking*) e pela execução do nosso modelo de Inteligência Artificial (NER).
- **torch** Bibliotecas base (*backend*) de Deep Learning que fornecem a aceleração matemática necessária para rodar redes neurais locais.

------------------------------------------------------------------------

## Tratamento de Erros Comuns

### Erro de Conexão com o Fala.BR (Status Code diferente de 200)

- **Causa:** O token da API expirou, a URL da CGU está passando por instabilidades ou o limite de requisições foi atingido.
- **Solução:** Verifique a validade do seu `TOKEN_API_OUVIDORIA` no arquivo `.env`. Se o token for válido, tente rodar a extração novamente após alguns minutos.

### Erro de Memória (Out of Memory - OOM)

- **Causa:** O *garbage collector* (`gc.collect()`) não conseguiu liberar a memória RAM a tempo entre o processamento de lotes pesados da rede neural.
- **Solução:** Reduza o tamanho do lote (`batch_size`) na função de processamento de texto, alterando de `batch_size=100` para `batch_size=32` ou menor.

------------------------------------------------------------------------

## Próximas Etapas e Evolução Tecnológica

Com este pipeline consolidado e rodando localmente, os dados sensíveis estão resguardados. Os próximos passos para elevar o nível de maturidade do projeto incluem:

- **Hardware Acceleration (Upgrade de Infraestrutura):** Implantação de clusters ou estações de trabalho equipadas com GPUs dedicadas para escalar o processamento e viabilizar a anonimização imediata de centenas de milhares de manifestações retroativas.
- **Automação Contínua (Agendamento):** Orquestrar a execução deste script para rodar de forma automática todos os dias, integrando as saídas (dados anonimizados) para consumo imediato em ferramentas de *Business Intelligence* do seu Órgão.

## Contato e Suporte

Para dúvidas sobre a arquitetura do código, calibração das expressões regulares ou relato de problemas na execução do pipeline, entre em contato com a equipe de desenvolvimento da COATD.
# Pasta NER (Treinamento do Modelo) - Documentação Técnica

## Visão Geral

A pasta `ner` é o cérebro de aprendizado do projeto de anonimização. É aqui que pegamos todo o conhecimento humano gerado na etapa anterior (a base de dados rotulada) e o utilizamos para realizar o *fine-tuning* (ajuste fino) de um modelo de Inteligência Artificial.

Utilizando a arquitetura **spaCy**, o script lê os textos anotados, converte-os para um formato otimizado, treina o modelo para reconhecer padrões e exporta uma versão inteligente capaz de realizar o Reconhecimento de Entidades Nomeadas (NER) de forma automática e estritamente local.

## Estrutura de Diretórios

```         
ner/
├── docker-compose.yml                      # Configuração do container Docker para o treinamento
├── data/                                   # Diretório de armazenamento de dados
│   └── raw/                                # Dados de entrada
│       └── json/                           # Arquivos JSON importados
│           └── dataset_rotulado.json       # Base de dados rotulada gerada pelo RME
├── models/                                 # Modelos treinados e configurações versionadas
│   ├── config_cpu.cfg                      # Configuração de treino versionada (Tok2Vec / CPU)
│   ├── config_gpu.cfg                      # Configuração de treino versionada (Transformers / GPU)
│   └── v1_modelo_inicial/                  # Diretório do primeiro ciclo de treinamento
├── outputs/                                # Resultados finais
│   └── pdf/                                # Arquivos do Relatório de Treinamento
│       └── ner.pdf                         # Relatório gerado com métricas e análises
└── scripts/                                # Scripts de processamento e treinamento
        └── qmd/                            # Documentos Quarto Markdown
            ├── ner.qmd                     # Script central que orquestra todo o treinamento
            └── ner_transformers.qmd        # Script de treinamento avançado com arquitetura Transformers (GPU)
```

------------------------------------------------------------------------

## Funcionalidade de Cada Componente

### 1. Arquivo `docker-compose.yml` (Orquestração em Container)

Define o ambiente isolado e containerizado onde o treinamento da Inteligência Artificial é executado. Configurações principais:

- **Serviço:** `motor-ner`
- **Imagem:** `motor-anonimizacao-base` (imagem Docker padrão com todas as dependências de Machine Learning pré-instaladas).
- **Container:** `pipeline-ner`
- **Volumes Montados:** Vincula as regras globais do projeto (`ABNT` e `_quarto.yml`) e mapeia as pastas de dados, scripts, modelos e resultados para dentro do container.
- **Comando de Execução:** Executa automaticamente a renderização do Quarto Markdown (`ner.qmd`) para iniciar o treinamento da IA e, ao finalizar com sucesso, garante a organização movendo o relatório PDF gerado para a pasta correta (`outputs/pdf/`).

### 2. Diretório `data/raw/json/` (Entrada)

Atua como a ponte entre a interface web e o motor de IA. Ele deve conter o arquivo `dataset_rotulado.json` contendo as marcações feitas pela equipe, onde cada entidade possui sua posição exata de início e fim no texto.

### 3. Script NER (`ner.qmd`)

Um documento interativo Quarto que executa o treinamento em etapas lógicas:

1.  **Análise Exploratória:** Conta quantas marcações de cada categoria (NOME, EMPRESA, etc.) existem.
2.  **Separação de Dados:** Divide os dados em **Treino (70%)**, **Validação/*dev* (15%)** e **Teste/*held-out* (15%)**. O *dev* é usado durante o treino para selecionar o melhor modelo; o *teste* fica reservado para a avaliação final honesta, com textos que o modelo nunca viu — nem no treino, nem na seleção.
3.  **Conversão (`DocBin`):** Transforma o arquivo JSON legível para humanos no formato `.spacy` binário, que é altamente eficiente para a máquina.
4.  **Treinamento:** Ajusta os pesos do modelo pré-treinado (`pt_core_news_lg`) para que ele aprenda o vocabulário e os contextos específicos da nossa base de dados.
5.  **Teste e Avaliação:** Executa um teste real com um texto fictício para provar que a IA aprendeu a localizar os dados.

### 3.1. Script de Treinamento Avançado (`ner_transformers.qmd`)

Um documento interativo Quarto semelhante ao `ner.qmd`, mas que executa o treinamento utilizando a arquitetura de aprendizado profundo **Transformers (BERTimbau)**.

**Por que um script semelhante foi feito?**
Para poder abraçar todos os públicos de ouvidorias públicas: tanto o com dinheiro investido em hardwares de vídeo (que podem aproveitar a aceleração de GPU com os Transformers), quanto os sem (que podem utilizar o `ner.qmd` padrão focado em CPU).

Embora siga as mesmas etapas lógicas (Análise, Divisão, Conversão, Treinamento e Teste), ele se diferencia por:
- Utilizar representações contextuais profundas em vez de vetores de palavras estáticos.
- Carregar a configuração versionada (`config_gpu.cfg`) que usa o `neuralmind/bert-base-portuguese-cased` (BERTimbau).
- Priorizar o *recall* (sensibilidade) para não deixar passar dados sensíveis em contextos complexos.

### 3.2. Configurações Versionadas (`config_cpu.cfg` e `config_gpu.cfg`)

Os arquivos de configuração do treinamento spaCy **são versionados no repositório**, dentro da pasta `models/`, em vez de serem gerados dinamicamente a cada execução. Isso garante **reprodutibilidade**: qualquer pessoa que clone o projeto treina com exatamente os mesmos hiperparâmetros, independentemente da versão do spaCy instalada.

- **`config_cpu.cfg`** — usado pelo `ner.qmd`. Arquitetura Tok2Vec com `vectors = "pt_core_news_lg"`.
- **`config_gpu.cfg`** — usado pelo `ner_transformers.qmd`. Arquitetura Transformer com `neuralmind/bert-base-portuguese-cased` (BERTimbau) e `patience = 600`.

Ambos já trazem os **pesos de seleção do modelo** (`score_weights`) ajustados para priorizar o *recall* (`ents_p = 0.33`, `ents_r = 0.67`), no espírito de uma métrica F-beta=2. No início de cada execução o script apenas **copia** o `.cfg` correspondente para `models/<modelo>/config.cfg`, de onde o spaCy o consome. Para alterar os hiperparâmetros do treino, edite diretamente o `.cfg` versionado.

> **Observação:** o `.gitignore` ignora todo o conteúdo pesado de `models/` (`**/models/*`), exceto esses arquivos de configuração (`!**/models/config*.cfg`).

### 4. Diretório `models/v1_modelo_inicial/` (Saída do Modelo)

Após a conclusão do script, esta pasta será preenchida com a versão finalizada e inteligente da IA (Salva na subpasta `model-best`). Este é o artefato que será levado para produção no pipeline principal de anonimização.

### 5. Diretório `outputs/pdf/` (Relatório Gerencial)

Armazena o documento `ner.pdf`, que serve como o "diploma" da IA, atestando com quais dados ela foi treinada, qual foi a sua margem de erro e quais são as suas métricas oficiais de acerto.

------------------------------------------------------------------------

## Como Iniciar o Treinamento do Modelo NER

**Pré-requisitos:** Ter o arquivo `dataset_rotulado.json` salvo na pasta `ner/data/raw/json/`. O Docker e o Docker Compose devem estar instalados e em execução na máquina.

1.  **Navegue até o diretório do NER:** Abra o seu terminal e acesse a pasta correspondente:

``` bash
cd ner
```

2.  **Inicie o container Docker:** Rode o comando abaixo para construir o ambiente e disparar o treinamento de forma 100% automatizada:

``` bash
docker-compose --profile cpu up
```

O Docker Compose irá: \* Carregar a imagem e montar os volumes necessários. \* Acionar o motor do Quarto Markdown no plano de fundo. \* Dividir os dados, convertê-los para o formato binário do spaCy e rodar os ciclos de aprendizado. \* Compilar e mover o relatório final `ner.pdf` para a pasta de saídas.

3. **Finalizando o container Docker**: Ao finalizar a pipeline execute o comando abaixo para remover o container:

``` bash
docker-compose --profile cpu down
```

## Entendendo as Métricas de Avaliação

Durante e após o treinamento, o relatório exibirá siglas técnicas para definir o quão inteligente o modelo ficou. Aqui está o significado prático de cada uma:

- **LOSS TOK2VEC:** É o tamanho do erro. Quanto menor esse número, melhor o modelo está compreendendo o texto.
- **LOSS NER:** Mede o erro específico na tarefa de achar as entidades (nomes, CPFs, empresas, etc).
- **Epochs (E):** Quantas vezes o modelo "leu" o conjunto de dados inteiro para melhorar seu desempenho. Ler poucas vezes gera ignorância; ler vezes demais gera memorização (*overfitting*).
- **\#** (Updates): Número de atualizações realizadas no modelo durante o treinamento. Cada atualização ocorre após a apresentação de um lote de dados, e o número total de atualizações pode indicar a quantidade de aprendizado que ocorreu.
- **Precisão (ENTS_P):** Quando o modelo diz "isso é um CPF", ele está certo em quantos % das vezes? Mede a confiabilidade da IA.
- **Recall (ENTS_R):** De todos os CPFs que realmente existiam no texto, quantos a IA conseguiu achar? Mede a capacidade de "não deixar passar nada".
- **Score (F1-Score):** É a média de equilíbrio entre a Precisão e o Recall. É a nota final de desempenho do modelo.

------------------------------------------------------------------------

## Fluxo de Dados do Treinamento

``` text
dataset_rotulado.json (Conhecimento Humano)
        ↓
ner.qmd (Script de Orquestração)
        ↓
Divisão 70/15/15 (Treino, Validação e Teste)
        ↓
Conversão para formato binário (.spacy)
        ↓
Ajuste fino utilizando vetores de palavras (pt_core_news_lg)
        ↓
model-best (Modelo Inteligente Salvo) + ner.pdf (Relatório Gerencial)
```

## Dependências Externas

As seguintes bibliotecas e ferramentas são o alicerce para a execução do treinamento nesta pasta (já configuradas na imagem Docker do projeto):

* **spaCy:** Biblioteca central de Processamento de Linguagem Natural (NLP) responsável pela criação do formato binário de treino (`DocBin`), calibração da rede neural e avaliação das métricas.
* **pt_core_news_lg:** Pacote de idioma pré-treinado do *spaCy* para a língua portuguesa. Fornece o conhecimento prévio de linguagem (vetores de palavras) que o modelo utiliza como ponto de partida antes do ajuste fino.
* **pandas:** Utilizado para a estruturação de tabelas durante a análise exploratória inicial dos dados.
* **Quarto:** Motor de renderização analítico que executa os blocos de código Python sequencialmente e compila os resultados visuais no relatório PDF.
* **Bibliotecas Nativas do Python (`json`, `pathlib`, `subprocess`, `random`, `shutil`):** Utilizadas para a leitura da base rotulada, manipulação segura de diretórios, embaralhamento dos dados (para a divisão justa entre Treino e Validação) e execução de processos em segundo plano no container.

------------------------------------------------------------------------

## Como Iniciar o Treinamento do Modelo Avançado (Transformers)

**Pré-requisitos:** Ter o arquivo `dataset_rotulado.json` salvo na pasta `ner/data/raw/json/`. O Docker e o Docker Compose devem estar instalados. Para este modelo, é fortemente **OBRIGATÓRIO** o uso de hardware com **GPU** (placa de vídeo) para um tempo de treinamento viável.

1.  **Navegue até o diretório do NER:** Abra o seu terminal e acesse a pasta correspondente:

``` bash
cd ner
```

2.  **Inicie o container Docker:** Rode o comando correspondente ao ambiente de transformers para disparar o treinamento:

``` bash
docker-compose --profile transformers up
```

3. **Finalizando o container Docker**: Ao finalizar a pipeline execute o comando abaixo para remover o container:

``` bash
docker-compose --profile transformers down
```

O fluxo automatizado irá: 
* Carregar a imagem baseada em GPU e montar os volumes. 
* Acionar o motor do Quarto Markdown (`ner_transformers.qmd`) no plano de fundo. 
* Injetar a arquitetura profunda BERTimbau (`neuralmind/bert-base-portuguese-cased`).
* Rodar os ciclos de aprendizado priorizando a sensibilidade (Recall) do modelo.
* Compilar e mover o relatório final `ner_transformers.pdf` para a pasta de saídas.

## Hiperparâmetro `patience` (Parada Antecipada)

A configuração versionada `models/config_gpu.cfg` define o parâmetro `patience` do spaCy como `600` (o padrão do spaCy é `1600`). Este parâmetro controla o mecanismo de **parada antecipada** (*early stopping*): ele define quantos *steps* de treinamento sem melhoria na pontuação de validação são tolerados antes de o processo ser interrompido automaticamente.

Como o spaCy avalia o modelo a cada **200 steps** por padrão, os valores se traduzem em:

- `patience = 1600` (padrão spaCy): aguarda **8 avaliações** consecutivas sem melhoria.
- `patience = 600` (valor ajustado): aguarda **3 avaliações** consecutivas sem melhoria.

**Por que reduzir?** O treinamento com Transformers em GPU é muito mais custoso em tempo e memória do que o Tok2Vec. Reduzir o `patience` encurta o tempo total de treinamento quando o modelo já convergiu, evitando ciclos desnecessários sem ganho real de precisão. Se o seu dataset for grande e você observar que o modelo ainda estava melhorando quando o treinamento parou, aumente o valor para `900` ou `1200` diretamente no arquivo `models/config_gpu.cfg`.

## Entendendo as Métricas de Avaliação (Transformers)

A lógica de avaliação é semelhante, porém o modelo baseado em redes neurais profundas exibe uma métrica de erro (LOSS) dividida em duas partes:

- **LOSS TRANSFORMER:** Mede o erro da IA ao tentar entender o contexto geral e a semântica da língua portuguesa. Quanto menor esse número, melhor o modelo mapeou as relações entre as palavras na frase.
- **LOSS NER:** Mede o erro específico na tarefa de achar as entidades (nomes, CPFs, empresas, etc).
- **Epochs (E):** Quantas vezes o modelo "leu" o conjunto de dados inteiro para melhorar seu desempenho. Ler poucas vezes gera ignorância; ler vezes demais gera memorização (*overfitting*).
- **\#** (Updates): Número de atualizações realizadas no modelo durante o treinamento. Cada atualização ocorre após a apresentação de um lote de dados, e o número total de atualizações pode indicar a quantidade de aprendizado que ocorreu.
- **Precisão (ENTS_P):** Quando o modelo diz "isso é um CPF", ele está certo em quantos % das vezes? Mede a confiabilidade da IA.
- **Recall (ENTS_R):** De todos os CPFs que realmente existiam no texto, quantos a IA conseguiu achar? Mede a capacidade de "não deixar passar nada".
- **Score (F1-Score):** É a média de equilíbrio entre a Precisão e o Recall. É a nota final de desempenho do modelo.

## Fluxo de Dados do Treinamento (Transformers)

``` text
dataset_rotulado.json (Conhecimento Humano)
        ↓
ner_transformers.qmd (Script de Orquestração Avançada)
        ↓
Divisão 70/15/15 (Treino, Validação e Teste)
        ↓
Conversão para formato binário (.spacy)
        ↓
Ajuste fino utilizando tensores contextuais profundos (BERTimbau)
        ↓
v1_modelo_transformers/model-best (Modelo Inteligente Salvo) + ner_transformers.pdf (Relatório)
```

## Dependências Externas (Modelo Transformers)

As seguintes bibliotecas e ferramentas formam o alicerce para a execução do treinamento avançado nesta arquitetura (já configuradas no `Dockerfile.transformers`):

* **spaCy & spacy-transformers:** Biblioteca central de NLP, agora estendida com seu módulo de transformers. É responsável por orquestrar a rede neural profunda, criar o formato binário de treino (`DocBin`) e calcular as métricas de perda (Loss).
* **BERTimbau (`neuralmind/bert-base-portuguese-cased`):** Modelo fundacional (Hugging Face) pré-treinado massivamente na língua portuguesa brasileira. Ele substitui o `pt_core_news_lg`, atuando como a base de inteligência contextual profunda para o ajuste fino do NER.
* **Quarto:** Motor de renderização analítico que executa os blocos de código Python sequencialmente e compila os resultados e logs de treinamento no relatório PDF.
* **Bibliotecas Nativas do Python (`json`, `pathlib`, `subprocess`, `random`, `shutil`, `collections`):** Essenciais para a manipulação dos diretórios de cache do modelo pesado, integração do script com os comandos de terminal do spaCy, embaralhamento e divisão justa dos dados para validação.

---

## Tratamento de Erros Comuns

### Aviso: "ERRO DE ALINHAMENTO" no console

- **Causa:** O texto original foi modificado ou contém caracteres invisíveis que fizeram as coordenadas da palavra grifada (no Rotulador) não baterem exatamente com a quebra de palavras do *spaCy*.
- **Solução:** O script já é inteligente o suficiente para ignorar essas palavras quebradas e continuar o treinamento. Apenas monitore se o número de descartes não está muito alto.

### Erro: Processo "Killed" ou container encerrado abruptamente

- **Causa:** Treinar modelos de Inteligência Artificial exige muita memória. O Docker provavelmente atingiu o limite de memória RAM alocada e "matou" o processo para proteger o sistema operacional (Out of Memory).
- **Solução:** Acesse as configurações do Docker Desktop e aumente a quantidade de memória RAM e núcleos de CPU dedicados aos containers antes de rodar o script novamente.

------------------------------------------------------------------------

## Evolução e Monitoramento Contínuo

O treinamento de Inteligência Artificial nunca tem um fim definitivo. Com o modelo base treinado nesta pasta, iniciamos o ciclo de aprendizado contínuo:

1.  **Deployment Local:** O `model-best` gerado aqui **não precisa ser copiado**. A pasta `ner/models/` é montada diretamente como volume no contêiner de `anonimizacao` (veja `anonimizacao/docker-compose.yml`: `../ner/models:/app/models`). Assim que o treinamento conclui, o pipeline de produção já consome o modelo recém-gerado automaticamente, sem duplicação de arquivos.
2.  **Validação com Dados Desconhecidos:** Periodicamente, precisaremos testar a IA com textos novíssimos para garantir que a forma de escrever do público não mudou (*Data Drift*).
3.  **Aprendizado Ativo (Active Learning):** As manifestações em que a IA ficar em dúvida serão separadas, enviadas novamente para a pasta `rme` (Rotulação), corrigidas por analistas humanos e devolvidas para esta pasta `ner` para um novo ciclo de treinamento, tornando a ferramenta cada vez mais implacável contra vazamentos de dados sensíveis.

---

## Próximas Etapas do Projeto

Após o treinamento e a validação do modelo nesta pasta, o ciclo de desenvolvimento da IA atinge um marco crucial. O modelo agora está pronto para sair do ambiente de "estudo" e ir para o mundo real. As próximas etapas consistem em:

* **Integração no Pipeline Principal:** Nenhuma transferência manual é necessária. A etapa de `anonimizacao` lê o artefato final (`model-best`) diretamente da pasta `ner/models/` via volume Docker, garantindo que o pipeline de produção sempre utilize a versão mais recente do modelo especialista assim que o treinamento é concluído.

## Contato e Suporte

Para dúvidas sobre a arquitetura do modelo, interpretação avançada das métricas de treinamento ou reporte de problemas na execução do container, consulte a documentação adicional nas pastas irmãs ou entre em contato com a equipe de análise e tratamento de dados da COATD.
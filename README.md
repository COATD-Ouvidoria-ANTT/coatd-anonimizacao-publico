# Projeto de Anonimização de Manifestações (Ouvidoria ANTT)

**Coordenação de Análise e Tratamento de Dados (COATD)**

Este repositório contém a arquitetura completa para extração, processamento, rotulação e ofuscação de dados sensíveis (PII) do sistema Fala.BR. Toda a solução foi desenhada para processamento estritamente local (*on-premises*) utilizando Inteligência Artificial (Deep Learning e NLP) e Expressões Regulares (Regex), garantindo conformidade total com a LGPD sem a necessidade de envio de dados para nuvens externas.

---

## Estrutura do Repositório

O repositório é modular e dividido em pastas com responsabilidades específicas. Cada diretório possui sua própria documentação técnica detalhada (`README.md` interno).

```text
coatd-anonimizacao-publico/
├── ABNT/                       # Regras globais de formatação e estilos para os relatórios
├── anonimizacao/               # Pipeline final de produção (Extração -> Ofuscação -> Exportação)
├── ner/                        # Motor de Inteligência Artificial (Treinamento e Fine-Tuning)
├── processamento/              # Scripts de preparação prévia de dados para a equipe de rotulação
├── rme/                        # Aplicação Web para Rotulação Manual de Entidades (Interface Humana)
├── _quarto.yml                 # Configurações globais de renderização de documentos
├── .dockerignore               # Exclusões de contexto para otimização do build
├── .gitignore                  # Exclusões de versionamento de arquivos sensíveis/locais
├── .gitattributes              # Padronização de finais de linha para ambientes Linux/Windows
├── Dockerfile                  # Receita da imagem base com todo o ecossistema
├── Dockerfile.transformers     # Receita da imagem adaptada apenas para treinamento do modelo transformers
├── requirements_cpu.txt        # Dependências e bibliotecas Python para todo pipeline, com exceção do modelo transformers
└── requirements_gpu.txt        # Dependências e bibliotecas Python do treinamento do modelo transformers
```

---

## Arquivos de Configuração e Infraestrutura

A raiz do projeto contém arquivos essenciais que padronizam a formatação dos relatórios, garantem a segurança do versionamento e definem o ambiente de execução.

### Configuração Global do Quarto (`_quarto.yml`)

O arquivo `_quarto.yml` atua como o modelo mestre para a renderização de todos os relatórios do projeto. Ele centraliza as regras visuais para que não seja necessário repeti-las em cada script.

Suas principais definições incluem:

* **Motor de Renderização:** Utiliza o `xelatex` para converter o Markdown em PDF de alta qualidade.
* **Estrutura do Documento:** Gera sumários automáticos (`toc: true`), numera as seções e aplica margens padronizadas (superior/inferior de 2.5cm, laterais de 3cm).
* **Cabeçalhos e Rodapés:** Configura o pacote LaTeX `fancyhdr` para injetar automaticamente "Relatório Técnico" e "Processo de Anonimização" no topo das páginas, além da numeração no rodapé.
* **Integração Bibliográfica:** Aponta automaticamente para os arquivos de referência (`referencias.bib`) e formatação ABNT.

### Segurança de Dados (`.gitignore`)

Como este projeto lida com dados sensíveis da Ouvidoria, o `.gitignore` foi rigorosamente configurado para impedir vazamentos e manter o repositório leve:

* **Bloqueio de Credenciais:** Impede o versionamento do arquivo `.env`, garantindo que o token da API da CGU nunca seja exposto no controle de versão. Para orientar a configuração sem expor segredos, cada etapa que consome a API (`processamento/` e `anonimizacao/`) versiona um modelo `.env.example` contendo apenas a variável `TOKEN_API_OUVIDORIA=` (sem valor) — basta copiá-lo para `.env` com o código abaixo:

```bash
cp .env.example .env
```

Após isso, preencha o token dentro do arquivo.
* **Bloqueio de Dados (LGPD):** Ignora todas as extensões de dados (`.csv`, `.xlsx`, `.json`, `.txt`) dentro das pastas `data/raw/` e `data/processed/`.
* **Bloqueio de Modelos Pesados:** Ignora a pasta `models/`, evitando que o repositório trave ao tentar subir redes neurais de vários gigabytes. A única exceção são os arquivos de configuração de treino versionados (`!**/models/config*.cfg`, como `config_cpu.cfg` e `config_gpu.cfg`), que são leves e garantem a reprodutibilidade do treinamento.
* **Preservação de Estrutura:** Utiliza a estratégia de exceção com arquivos vazios `!/.gitkeep`. Isso garante que as pastas sejam criadas na máquina de outros desenvolvedores, mesmo sem enviar os dados que deveriam estar dentro delas. Nas pastas `models/`, os próprios arquivos `config*.cfg` versionados já cumprem esse papel de manter a estrutura.

### Padronização de Finais de Linha (`.gitattributes`)

Este arquivo previne de forma invisível falhas de compatibilidade entre sistemas operacionais (Windows, Mac, Linux). Ele instrui o Git a forçar o padrão de quebra de linha LF (Line Feed) para códigos e scripts (`.sh`, `.yml`, `.py`, `.qmd`, `.json`).

### Receitas de Infraestrutura (`Dockerfile` e `Dockerfile.transformers`)

Para suportar as duas vias de processamento detalhadas anteriormente, o projeto utiliza receitas separadas:

* **`Dockerfile`:** Constrói a imagem leve e otimizada (`python:3.13-slim`), contendo tudo o que é necessário para a rotina diária da Ouvidoria e treinamento na arquitetura padrão (CPU).
* **`Dockerfile.transformers`:** Constrói a imagem pesada (`pytorch/pytorch`), injetando os drivers da NVIDIA (CUDA) e o cache do BERTimbau para viabilizar o processamento em GPU.

### Otimização de Construção (`.dockerignore`)

Este arquivo define o que é enviado para o "contexto de build" quando você roda o comando de criação da imagem do Docker. Ele foi configurado com uma abordagem extrema de "negação por padrão":

```text
# Ignora absolutamente tudo por padrão
*

# Abre exceções apenas para o que o Docker precisa para o BUILD
!requirements_cpu.txt
!requirements_gpu.txt
!Dockerfile
!Dockerfile.transformers
```

**Por que foi feito assim?**
As imagens Docker deste projeto atuam puramente como "motores" de processamento. Elas só precisam conhecer as receitas de instalação e as listas de bibliotecas. Todo o resto (scripts, modelos e dados) é bloqueado pelo `.dockerignore` para não ser adicionado dentro da imagem. A conexão entre o motor Docker e o código do projeto ocorre em tempo de execução através do mapeamento de **volumes** (descrito nos arquivos `docker-compose.yml`), permitindo que a equipe altere os scripts Python sem precisar reconstruir as imagens.

### Controle de Versões de Bibliotecas (`requirements_cpu.txt` e `requirements_gpu.txt`)

O versionamento explícito (ex: `spacy==3.8.14`, `pandas==3.0.2`) garante a total reprodutibilidade do projeto. Para evitar imagens inchadas, as dependências foram divididas estrategicamente:

* **`requirements_cpu.txt`:** Contém o ecossistema completo para sustentar a aplicação. Abrange a manipulação de dados (`pandas`), a interface web do rotulador (`Flask`), ferramentas de visualização (`matplotlib`, `seaborn`) e o motor PLN base.
* **`requirements_gpu.txt`:** Um arquivo estritamente enxuto, desenhado apenas para o contêiner de Inteligência Artificial avançada. Contém exclusivamente as pontes matemáticas e de modelagem (`transformers`, `spacy-transformers`), garantindo máxima performance de hardware sem o peso de bibliotecas de interface ou gráficos.

---

## Ordem Cronológica de Execução (O Fluxo de Trabalho)

Para que o projeto funcione corretamente, as pastas devem ser operadas em uma sequência lógica, onde a saída de uma etapa é a entrada da seguinte. O fluxo de vida dos dados segue esta ordem:

1. **`processamento/` (Preparação):** Onde tudo começa. Os dados brutos são ingeridos da API, passam por uma limpeza básica e são fatiados em blocos de texto menores (*chunking*). O resultado é exportado para a etapa seguinte.
2. **`rme/` (O Fator Humano):** Utiliza os dados processados para alimentar a Ferramenta de Rotulação Manual. A equipe utiliza a interface para ensinar à máquina o que é um nome, uma empresa ou um endereço.
3. **`ner/` (Aprendizado de Máquina):** Pega a base de dados que a equipe acabou de rotular na etapa anterior e treina o modelo de Inteligência Artificial (*Fine-tuning* do spaCy/Transformers), gerando o artefato final inteligente (`model-best`).
4. **`anonimizacao/` (Produção):** A etapa definitiva. Importa o modelo treinado na etapa 3 e roda o pipeline diário: extrai dados novos, aplica regras estáticas (Regex), roda a IA para o que for complexo e cospe a planilha final completamente anonimizada e segura para uso analítico.

---

## Configuração Inicial: Os Motores de Processamento (Docker)

Toda a arquitetura deste projeto roda dentro de contêineres isolados para garantir que funcione perfeitamente em qualquer ambiente. Para isso, precisamos construir as imagens base **uma única vez**.

**O Contexto da Infraestrutura Pública:**
É uma realidade comum que unidades de Ouvidoria e demais setores públicos operem com computadores padrão de escritório, sem acesso a hardwares gráficos dedicados (GPUs) de alto custo. Tentar executar modelos massivos e modernos de Inteligência Artificial (como a arquitetura baseada em *Transformers*) utilizando apenas o processador comum (CPU) é tecnicamente inviável devido à extrema lentidão.

Pensando nisso, o projeto foi desenhado com **duas vias de execução independentes**. Essa abordagem democratiza o uso da ferramenta para qualquer órgão público, ao mesmo tempo em que oferece uma abordagem extremamente atual para aqueles que possuem infraestrutura avançada.

Abra o terminal na pasta raiz

```bash
cd coatd-anonimizacao-publico
```

### 1. Construção do Motor Padrão (Otimizado para CPU comum)

**Recomendado para a maioria dos casos.** Este motor foi feito sob medida para operar perfeitamente nos computadores tradicionais fornecidos pela administração pública. Ele utiliza uma arquitetura de rede neural eficiente (Tok2Vec) que processa os dados de forma ágil e segura utilizando apenas a CPU. 
> *Se a sua máquina não possui uma placa de vídeo dedicada, o uso do modelo BERT é inviável. Baixe **apenas** a imagem abaixo e siga normalmente com o pipeline do projeto, que se inicia na pasta `processamento/`*

```bash
docker build -t motor-anonimizacao-base -f Dockerfile .
```

### 2. Construção do Motor Avançado (Requer Placa de Vídeo NVIDIA)

**Para desempenho superior e estado da arte.** Caso sua unidade disponha de servidores ou estações com aceleração gráfica dedicada (ex: NVIDIA RTX), esta é a versão definitiva. Ela habilita o uso de *Transformers* (BERTimbau) — a arquitetura de ponta por trás das IAs modernas. O nível de precisão, compreensão de contexto e desempenho de rotulação é **extremamente maior**.
> *Se a sua máquina possui uma placa de vídeo dedicada, o uso do modelo BERT é o mais recomendado. Baixe **as duas imagens** e siga com o pipeline do projeto, que se inicia na pasta `processamento/`*

```bash
docker build -t motor-anonimizacao-base -f Dockerfile .
docker build -t motor-anonimizacao-transformers -f Dockerfile.transformers .
```

> **Aviso Importante sobre o Tempo de Instalação:**
> Devido ao tamanho dos componentes de *Deep Learning*, linguagens e processadores de texto integrados, **a compilação inicial pode demorar de 20 a 40 minutos** dependendo da sua conexão com a internet (especialmente na versão Transformers, que baixa gigabytes de pesos neurais do *Hugging Face*). Não feche o terminal. Este é um processo de configuração executado apenas uma vez; após criadas, as instâncias das etapas seguintes iniciarão em poucos segundos.

---

## Tecnologias Utilizadas

O ecossistema do projeto foi construído empregando as ferramentas mais sólidas do mercado de Ciência de Dados e Engenharia de Software:

* **Python:** Linguagens base para processamento de dados e estatística.
* **spaCy:** Arquitetura central para o Processamento de Linguagem Natural e redes neurais.
* **Transformers:** Arquitetura de aprendizado profundo extremamente atual (utilizando o ecossistema Hugging Face e o modelo *BERTimbau*). Responsável por fornecer uma compreensão avançada do contexto das manifestações, elevando drasticamente a precisão na detecção de entidades sensíveis e ambíguas.
* **Flask:** Backend ágil para sustentar a ferramenta web de rotulação humana.
* **Quarto Markdown:** Motor analítico de ponta para a geração interativa e automatizada de relatórios gerenciais e acompanhamento de métricas.
* **Docker:** Orquestração e padronização do ambiente de execução.

## Contato

Para aprofundar-se no funcionamento técnico de cada etapa, navegue até as pastas individuais e consulte seus respectivos arquivos `README.md`. Para manutenção evolutiva ou suporte à infraestrutura, acione a Coordenação de Análise e Tratamento de Dados (COATD).

---

## Como Citar

Se você utilizar este pipeline de anonimização ou parte de sua arquitetura em suas pesquisas, projetos institucionais ou sistemas, por favor, cite-nos como referência intelectual utilizando o formato BibTeX abaixo:

```bibtex
@software{antt2026anonimizacao,
  author       = {Cherulli, Pedro and {Coordenação de Análise e Tratamento de Dados (COATD/OUVID/ANTT)}},
  title        = {Projeto de Anonimização de Manifestações (Ouvidoria ANTT)},
  year         = {2026},
  organization = {Agência Nacional de Transportes Terrestres (ANTT)},
  note         = {Pipeline on-premises de Processamento de Linguagem Natural e Deep Learning para anonimização de dados sensíveis em conformidade com a LGPD.},
  url          = {https://github.com/COATD-Ouvidoria-ANTT/coatd-anonimizacao-publico}
}
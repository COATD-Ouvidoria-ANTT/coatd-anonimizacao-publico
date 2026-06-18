# Pasta RME (Rotulação Manual de Entidades) - Documentação Técnica

## Visão Geral

A pasta `rme` abriga a **Ferramenta de Rotulação Manual de Entidades**, uma aplicação web desenvolvida para criar a base de dados que ensinará a Inteligência Artificial do projeto.

Como o modelo precisa aprender a identificar o que é um nome de pessoa, uma empresa ou um endereço dentro dos textos da ouvidoria, esta ferramenta permite que um humano leia os textos e "grife" essas informações sensíveis. Tudo funciona de forma estritamente local, garantindo que os dados protegidos pela LGPD não transitem por serviços em nuvem.

**Atenção ao Volume de Dados:** A inteligência do modelo é diretamente proporcional ao volume de exemplos que ele estuda. Quanto maior e mais rica for a base de dados anotada gerada por esta ferramenta, mais afiado e específico será o ajuste fino (*fine-tuning*) da nossa IA.

## Estrutura de Diretórios

```         
rme/
├── docker-compose.yml                      # Orquestração do ambiente da interface e painel
├── start.sh                                # Script de inicialização do container
├── data/                                   # Diretório de armazenamento de dados
│   ├── raw/                                # Dados brutos (entrada)
│   │   └── csv/                            # Arquivos CSV gerados
│   │       └── dataset_para_rotular.csv    # Base de dados utilizada pelo rotulador
│   └── processed/                          # Dados processados (intermediários)
│       └── json/                           # Arquivos JSON gerados
│           └── dataset_rotulado.json       # Base de dados rotulada gerada no processo
│           └── dataset_pulados.json        # Base de IDs pulados no processo
├── scripts/                                # Scripts de processamento
│   ├── templates/                          # Scripts em HTML/CSS
│   │   └── index_ner.html                  # Interface visual do rotulador (Frontend)
│   ├── qmd/                                # Documentos Quarto Markdown
│   │   └── relatorio_rme.qmd               # Dashboard de monitoramento em tempo real
│   ├──python/                              # Scripts em python
│   │   └── app.py                          # Servidor backend que controla a aplicação
└── outputs/                                # Resultados finais
    └── html/                               # Arquivos do Dashboard do Rotulador
```

------------------------------------------------------------------------

## Funcionalidade de Cada Componente

### 1. Servidor Backend (`app.py`)

Escrito de forma simples e funcional em Python utilizando Flask, este arquivo é o cérebro da operação. Ele lê os dados processados na etapa anterior, serve a página web para o usuário, salva as marcações feitas em um arquivo seguro (`dataset_rotulado.json`) e até utiliza o modelo de IA atual, caso exista, para sugerir marcações automáticas.

### 2. Interface Visual (`index_ner.html`)

É a tela onde o usuário trabalha. Foi desenhada para ser intuitiva e rápida. Ela se comunica constantemente com o servidor para salvar o progresso a cada clique.

### 3. Painel de Monitoramento (`relatorio_rme.qmd`)

Um documento interativo construído em Quarto Markdown. Ele gera gráficos em tempo real mostrando quantas mensagens já foram rotuladas, quantas entidades foram encontradas e o tamanho médio de cada texto.

### 4. Arquivo de Orquestração (`docker-compose.yml`)

Sobe todo esse ambiente em um container isolado, expondo duas portas principais:

- **Porta 5000:** Para acessar a ferramenta de rotulação.
- **Porta 4200:** (Opcional) Para hospedar e visualizar o Dashboard Quarto.

### 5. Script de Inicialização (`start.sh`)

Atua como o maestro do container. Quando você executa o Docker Compose, este script é chamado automaticamente para levantar todos os serviços em paralelo:

- Inicia o servidor backend da API em segundo plano.
- Executa a primeira renderização do Dashboard Quarto, garantindo que o painel inicial seja gerado.
- Inicia um servidor web leve (HTTP) na porta 4200 exclusivamente para exibir os gráficos.
- Gerencia o desligamento seguro de todos os processos caso o container seja interrompido.

------------------------------------------------------------------------

## Como Iniciar a Ferramenta

**Pré-requisitos:** Ter concluído a etapa da pasta `processamento` e possuir os arquivos de texto preparados dentro da pasta `data/raw/csv`.

1.  **Navegue até o diretório rme**:

``` bash
cd rme
```

2.  **Inicie o ambiente:** Abra o seu terminal, navegue até a pasta `rme` e execute o comando:

``` bash
docker-compose up
```

3.  **Acesse a Ferramenta de Rotulação:**

O `start.sh` deixará a aplicação disponível automaticamente. Abra o seu navegador de preferência e digite o seguinte endereço:

``` text
http://localhost:5000
```

4.  **Acesse o Dashboard de Acompanhamento:** Os relatórios são gerados e podem ser acessados por meio do endereço:

``` text
http://localhost:4200
```

5.  **Selecione o Arquivo do Diretório:** Para ver os gráficos de desempenho da equipe que está rotulando os dados, acesse o arquivo `relatorio_rme.html` dentro da interface apresentada após acessar o endereço http://localhost:4200.

6.  **Finalizando o container Docker**: Ao finalizar a pipeline execute o comando abaixo para remover o container e desocupar as portas utilizadas:

``` bash
docker-compose down
```


------------------------------------------------------------------------

## Guia de Operação do Rotulador

A tela principal exibirá um fragmento de texto da ouvidoria dividido palavra por palavra. Siga as instruções abaixo para classificar os dados:

- **Selecionando Palavras:** Clique sobre uma palavra para selecioná-la. Para selecionar termos compostos (ex: "Banco do Brasil"), clique na primeira palavra e, em seguida, na última. O sistema preencherá o espaço entre elas automaticamente.

- **Aplicando o Rótulo:** Com o texto selecionado, clique em um dos botões coloridos abaixo do texto:

- **NOME (Azul):** Para nomes de pessoas físicas.

- **EMPRESA (Verde):** Para pessoas jurídicas, concessionárias, marcas ou órgãos.

- **ENDEREÇO (Roxo):** Para ruas, rodovias, praças de pedágio ou cidades.

- **Corrigindo Erros:** Se marcou algo errado, clique com o **botão direito** do mouse sobre a palavra colorida para remover a cor e a classificação. Você também pode usar o botão **Desfazer** para anular a última ação.

- **Avançando:** Ao terminar de revisar e marcar todas as entidades sensíveis do texto atual, clique em **Próximo texto**. O sistema salva o seu trabalho automaticamente e carrega a próxima manifestação.

- **Pulando Textos:** Se um texto estiver confuso, incompleto ou não contiver dados relevantes, clique em **Pular texto** para ignorá-lo sem afetar a base de dados.

- **Voltando Textos:** Se marcou algo errado e clicou no botão **Próximo Texto**, pode voltar e navegar por textos anteriores apertando no botão **Voltar Texto**. Ele garante a integridade da base anotada, modificando alterações ao avançar para o próximo texto.

- **Buscando Palavras:** Utilize o campo "Caçar Palavra" no topo da tela para filtrar apenas os textos que contêm termos específicos que você deseja rotular no momento.

## Boas Práticas para um Treinamento de Alta Qualidade

Para garantir que o modelo de IA possua maior performance na hora de anonimizar os dados, a equipe de rotulação deve observar duas regras de ouro durante a seleção dos textos:

- **Diversidade de Cenários:** Para que a IA não fique "viciada", é fundamental rotular uma grande variedade de manifestações. Tente selecionar e rotular queixas longas, dúvidas curtas, textos muito formais (linguagem jurídica) e textos extremamente informais (com gírias ou erros de digitação). O modelo precisa aprender a encontrar os dados sensíveis em qualquer contexto e tom de voz.
- **Geração de Dados Sintéticos:** Caso a sua ouvidoria possua um volume histórico muito baixo de manifestações registradas ou o trabalho de rotulação esteja sendo extremamente desgastante. Nesse cenário, é altamente recomendável criar **dados sintéticos**, ou seja, redigir textos fictícios simulando o padrão de reclamações do seu órgão e rotulá-los aqui. Isso aumenta a base de treino artificialmente e garante um modelo final muito mais seguro.

## Guia de Operação do Dashboard

O painel de monitoramento tem como objetivo acompanhar, em tempo real, o processo de rotulagem manual de entidades nomeadas. Siga as instruções abaixo para interpretar e interagir com os dados:

- **Atualizando os Dados:** Para visualizar as informações mais recentes, clique no botão azul **Atualizar Relatório**, localizado no canto superior direito da tela. É obrigatório clicar neste botão toda vez que você quiser recarregar o painel com os dados das últimas anotações realizadas.

- **Analisando os Indicadores Gerais:** Logo abaixo do cabeçalho, quatro cartões coloridos fornecem um resumo rápido do progresso do seu trabalho:
- **Total de Mensagens Rotuladas (Azul):** Mostra a quantidade exata de manifestações que já foram revisadas e salvas.
- **Total de Entidades Detectadas (Roxo):** Exibe o volume absoluto de todas as marcações individuais feitas (soma de todos os rótulos aplicados).
- **Tipos de Entidades (Laranja):** Indica quantas categorias diferentes de dados sensíveis (ex: NOME, EMPRESA) foram encontradas e marcadas até o momento.
- **Média de Entidades por Mensagem (Verde):** Mostra a proporção média de termos classificados dentro de cada texto processado.

- **Acompanhando a Distribuição de Rótulos:** O gráfico de barras horizontais (à esquerda) exibe a **Contagem Total** de cada classe de entidade. Utilize-o para visualizar rapidamente o volume de cada categoria e entender quais tipos de dados (como EMPRESA ou NOME) estão aparecendo com mais frequência na base.
  
- **Avaliando o Tamanho das Entidades:** O gráfico de dispersão/boxplot (à direita) analisa o **tamanho** (comprimento) das marcações feitas para cada classe. Ele é fundamental para avaliar a qualidade das anotações, permitindo verificar a variação no tamanho dos termos selecionados e identificar se há anomalias (como marcações acidentalmente muito longas ou curtas demais) em categorias específicas.

## Como criar suas próprias entidades no Rotulador?

É comum que as entidades sensíveis variem de acordo com a logística e a necessidade de cada órgão. Enquanto a COATD pode focar em ocultar Nomes e Endereços, outro setor pode precisar mapear diferentes categorias não estruturadas.

A ferramenta foi construída para ser facilmente adaptável. Para adicionar uma nova categoria de entidade, você precisará editar apenas **três pequenos blocos** dentro do arquivo `scripts/templates/index_ner.html`.

Vamos usar como exemplo a criação de uma nova entidade chamada **MARCA**.

### Passo 1: Atualizar o "Dicionário" do JavaScript

Role o arquivo HTML até encontrar a tag `<script>`. Logo no início do código JavaScript, existe uma lista chamada `labelClass`. Ela é a responsável por "traduzir" o nome da entidade para a cor que aparecerá na tela.

Adicione a sua nova entidade seguindo o mesmo padrão:

``` javascript
const labelClass = {
    "NOME": "entidade-nome", 
    "EMPRESA": "entidade-empresa", 
    "ENDERECO": "entidade-endereco",
    "MARCA": "entidade-marca" // <-- Adicione sua nova entidade aqui
};
```

*Atenção: O texto à esquerda (ex: "MARCA") é exatamente como a classe será salva no banco de dados para o treinamento da Inteligência Artificial.*

### Passo 2: Criar o botão na Interface (HTML)

Agora, procure no meio do arquivo pela área onde os botões estão sendo desenhados (dentro da tag `<body>`). Você verá os botões de Nome, Empresa e Endereço.

Basta adicionar uma nova linha para criar o seu botão:

``` html
<div>
    <button class="nome" onclick="definirLabel('NOME')">Nome</button>
    <button class="empresa" onclick="definirLabel('EMPRESA')">Empresa</button>
    <button class="endereco" onclick="definirLabel('ENDERECO')">Endereço</button>
    <button class="marca" onclick="definirLabel('MARCA')">Marca</button>
</div>
```

*Atenção: O valor dentro de `definirLabel('MARCA')` deve ser idêntico ao que você cadastrou no Passo 1.*

### Passo 3: Definir as cores (CSS)

Por fim, para que a sua palavra selecionada e o seu botão fiquem bonitos e fáceis de identificar, suba até o início do arquivo, na tag `<style>`.

Adicione as cores para o botão e para o texto grifado. Você pode escolher qualquer código de cor hexadecimal (ex: um tom de laranja).

``` css
/* Cores para o texto grifado */
.entidade-nome { background-color: #2196F3; color: #fff; font-weight: bold; }
.entidade-empresa { background-color: #4CAF50; color: #fff; font-weight: bold; }
.entidade-endereco { background-color: #9C27B0; color: #fff; font-weight: bold; }
.entidade-marca { background-color: #FF9800; color: #fff; font-weight: bold; } /* Sua nova cor */

/* Cores para o botão */
button.nome { background-color: #2196F3; color:#fff; }
button.empresa { background-color: #4CAF50; color:#fff; }
button.endereco { background-color: #9C27B0; color:#fff; }
button.marca { background-color: #FF9800; color:#fff; } /* Sua nova cor */
```

*(Opcional) Se você quiser que a cor também fique adaptada para o Modo Escuro, procure pela seção `body.dark` no final do CSS e adicione uma versão mais suave da sua cor:*

``` css
body.dark .entidade-marca { background-color: #FFB74D; color: #000; }
```

### Pronto!

Basta salvar o arquivo `index_ner.html` e atualizar a página no seu navegador (`F5`). O novo botão já estará disponível e os dados rotulados com ele serão salvos perfeitamente no seu arquivo `.json`.

------------------------------------------------------------------------

## Fluxo de Dados da Rotulação

``` text
Arquivos .CSV (Textos preparados)
        ↓
start.sh inicializa o ambiente
        ↓
Interface Local (http://localhost:5000)
        ↓
Ação Humana (Seleção e Classificação)
        ↓
Salvamento Automático em JSON (dataset_rotulado.json)
        ↓
Geração de Gráficos (Dashboard Quarto)
        ↓
Exportação para a pasta /ner (Treinamento do Modelo)
```

## Dependências Externas

As seguintes bibliotecas e ferramentas são utilizadas para sustentar a interface e o servidor (especificadas no ambiente do projeto):

- **Flask & Flask-CORS**: Framework web utilizado para criar o servidor backend e permitir a comunicação com a interface de rotulação.
- **pandas**: Utilizado para a leitura, manipulação e transição dos dados em formato CSV para o sistema web.
- **spacy**: Carregamento do modelo de Processamento de Linguagem Natural (NLP) que fornece as marcações sugeridas automaticamente pela IA.
- **Quarto**: Motor analítico executado em segundo plano para gerar o Dashboard interativo de monitoramento.
- **json**: Biblioteca nativa do Python responsável por salvar e estruturar as anotações feitas pelo usuário de forma segura.

------------------------------------------------------------------------

## Tratamento de Erros Comuns

### Erro: "Porta 5000/4200 já está em uso" (Address already in use)

- **Causa:** Outro programa ou container na sua máquina já está utilizando a porta necessária para a interface.
- **Solução:** Pare os containers antigos (`docker-compose down`) ou reinicie o serviço do Docker. Se o problema persistir, você pode alterar a porta de saída no arquivo `docker-compose.yml`.

### Erro: "Nenhum arquivo CSV encontrado" ou Dados não aparecem na tela

- **Causa:** A pasta `data/raw/csv` está vazia. O rotulador precisa de dados pré-processados para funcionar.
- **Solução:** Retorne à etapa anterior (pasta `processamento`) e certifique-se de que o pipeline rodou com sucesso e exportou os dados para a pasta correspondente.

### Aviso: "Sugestões automáticas da IA não aparecem"

- **Causa:** O sistema não encontrou um modelo de IA pré-treinado na pasta `/models`.
- **Solução:** Se esta for a primeira vez que a equipe está rotulando dados (o primeiro ciclo do projeto), isso é **normal**. A rotulação terá que ser 100% manual. Nos ciclos seguintes, o modelo atualizado fará as sugestões.

### Erro: "Erro ao renderizar" no Dashboard

- **Causa:** Falha na execução do processo do Quarto ao tentar gerar os gráficos.
- **Solução:** Verifique os logs do terminal Docker para entender qual parte do script falhou ou se o arquivo `dataset_rotulado.json` está corrompido ou vazio.

------------------------------------------------------------------------

## Próximas Etapas do Projeto

Após a conclusão da rotulação nesta pasta, o arquivo contendo todo o conhecimento humano capturado (`dataset_rotulado.json`) é exportado automaticamente para a pasta irmã `ner/`. A próxima etapa consiste nos seguintes tópicos:

- **Treinamento e Ajuste Fino (*Fine-tuning*):** Utilizar a base anotada para ensinar e recalibrar o modelo de linguagem, tornando-o especialista nos textos da ANTT.
- **Validação de Métricas:** Avaliar a precisão do modelo atualizado antes de colocá-lo em produção no pipeline de anonimização.
- **Deploy Local:** Substituir o modelo antigo pelo recém-treinado, criando um ciclo de melhoria contínua (*Active Learning*).

## Contato e Suporte

Caso a interface apresente lentidão, o servidor não inicie ou as sugestões automáticas parem de funcionar, verifique os logs do terminal onde o comando Docker foi executado ou contate a equipe técnica da COATD para manutenção.
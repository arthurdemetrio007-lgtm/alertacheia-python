# Uso de IA e prompts

## Ferramenta

Claude (Anthropic), utilizado por meio de chat como ferramenta de apoio e consulta durante o desenvolvimento da disciplina de Computational Thinking with Python.

## Como a IA foi utilizada

Durante o desenvolvimento, utilizei o Claude para esclarecer dúvidas sobre a estrutura do programa, organização dos módulos, tratamento dos dados e implementação das regras de decisão.

As principais contribuições foram:

- Orientações para interpretar os requisitos da disciplina de Python dentro do contexto da Global Solution.
- Sugestões para organizar o programa em módulos, facilitando a separação das responsabilidades.
- Esclarecimento de dúvidas sobre leitura, tratamento e utilização dos dados da estação da ANA.
- Apoio na compreensão e implementação das regras de classificação dos níveis de alerta por bairro.
- Auxílio na análise de resultados e identificação de possíveis inconsistências.
- Orientações para organizar os testes e a documentação do projeto.

## O que foi feito e revisado por mim

- Definição do problema que o programa deveria resolver e sua integração com os dados utilizados pelo sensor (Edge) e pelo aplicativo web.
- Pesquisa e download da série histórica da estação 87450020 no site Hidro-Telemetria da ANA, selecionando a estação e o período desejado.
- Instalação das dependências necessárias e configuração do ambiente Python.
- Execução do programa no computador, testando as opções 1, 2 e 3 do menu.
- Conferência das informações apresentadas e comparação dos resultados com os dados utilizados na simulação.
- Revisão da tabela apresentada na opção 2, identificando uma inconsistência na recomendação de um bairro que havia mudado de estado apenas com base nos relatos, sem uma previsão de elevação do nível da água.
- Ajuste da recomendação para apresentar o motivo da classificação do bairro, evitando indicar uma previsão que não estava disponível nos dados.

## Prompts

Cada item resume as principais dúvidas e orientações solicitadas ao assistente durante o desenvolvimento. Prints e arquivos enviados estão identificados entre colchetes.

1. Pedi orientações para iniciar o desenvolvimento da parte de Python, considerando a integração com os dados do sensor e do aplicativo web já desenvolvido.
2. [Prints do site Hidro-Telemetria da ANA, do menu "Visualizar Dados" e da série da estação 87450020] Solicitei orientação para localizar e baixar os dados históricos do Guaíba.
3. [Arquivo `5-87450020-USINA_DO_GAS_METRO-2026-11-12.xls`, baixado por mim] Enviei a série histórica para auxiliar na utilização dos dados na simulação de cheia.
4. [Prints das opções 1, 2 e 3 do menu executadas no computador] Solicitei ajuda para conferir os resultados e identificar possíveis inconsistências nas recomendações apresentadas pelo programa.

## Considerações finais

O Claude foi utilizado como ferramenta de apoio para esclarecer dúvidas técnicas, orientar a organização do código e auxiliar na análise dos resultados. A escolha do problema, a pesquisa dos dados, a execução dos testes e a conferência das informações foram realizadas durante o desenvolvimento do projeto, com revisão das sugestões fornecidas pela ferramenta.

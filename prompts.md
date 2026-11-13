# Uso de IA e prompts

## Ferramenta

Claude (Anthropic), usado por chat.

## O que a IA fez

- Leu a seção de Computational Thinking with Python do enunciado e propôs a pergunta que o programa responde.
- Propôs a organização em módulos (coleta, tratamento, decisão, simulação, relatório) e as regras de decisão por bairro.
- Escreveu o código, os testes e este README.

## O que foi feito e revisado por mim

- Escolha do problema e definição de que o programa usa os mesmos dados do sensor (Edge) e do app web.
- Download da série da estação 87450020 no site Hidro-Telemetria da ANA, escolhendo a estação e o período.
- Instalação das dependências e execução dos testes e das opções 1, 2 e 3 do menu no meu computador, conferindo as saídas.
- Revisão da tabela da opção 2: encontrei a contradição entre "Alerta" com a recomendação "a água deve chegar em poucas horas" num bairro que tinha subido de estado só pelos relatos, sem previsão de nível. A recomendação passou a explicar o motivo do estado.

## Prompts

1. "nenhum precisa, seguimos": pedido para começar a disciplina de Python depois de fechar o app web.
2. [Prints do site Hidro-Telemetria da ANA, do menu "Visualizar Dados" e da série da estação 87450020]: pedido de ajuda para baixar a série do Guaíba de 2024.
3. [Arquivo baixado `5-87450020-USINA_DO_GAS_METRO-2026-11-12.xls`]: envio da série para o programa usar.
4. [Prints das opções 1, 2 e 3 do menu rodando no meu computador]: conferência dos resultados.

# Checklist — Etapa 4 e Rubrica de Avaliação

Este checklist foi atualizado para alinhar o projeto ao nível **Excelente** da rubrica.

## 1. Diagnóstico e formulação do problema

- [x] Problema real delimitado: decisão tardia/imprecisa sobre irrigação e pragas.
- [x] Dor prática definida: desperdício de água, custos com defensivos, perda de produtividade e baixa rastreabilidade da decisão.
- [x] Justificativa da IA: previsão de umidade, decisão por regras e explicação interpretável.

## 2. Modelagem PEAS e requisitos

- [x] PEAS documentado no README.
- [x] Sensores definidos: temperatura, umidade do ar, umidade do solo, chuva, vento, NDVI, confiança de praga e área foliar afetada.
- [x] Atuadores definidos: bomba, vazão, pulverizador e drone.
- [x] Requisitos funcionais documentados.
- [x] Requisitos não funcionais documentados.

## 3. Lógica de controle

- [x] Sistema Especialista implementado em Python.
- [x] Regras SE/ENTÃO adequadas para classificação de risco e decisão de controle.
- [x] Log registra regras acionadas e justificativa técnica.
- [x] Atuadores são definidos a partir da decisão especialista.

## 4. Integração analítica com Gemini

- [x] Função `explicar_com_gemini()` implementada.
- [x] Prompt contextualizado para AgTech, irrigação, pragas e atuadores.
- [x] Gemini não toma a decisão técnica; apenas interpreta.
- [x] Fallback local em caso de API indisponível ou chave ausente.

## 5. Modelo de aprendizado

- [x] RNA implementada com `MLPRegressor`.
- [x] Previsão de umidade do solo na próxima hora.
- [x] Métricas documentadas: MAE, RMSE, R², baseline e ganho percentual.
- [x] Resultado da RNA alimenta a lógica da Etapa 2.

## 6. Pipeline e tratamento de exceções

- [x] Fluxo completo: Sensores -> RNA -> Sistema Especialista -> Gemini/Fallback -> Atuadores.
- [x] Validação de dataset vazio.
- [x] Validação de colunas ausentes.
- [x] Tratamento de valores nulos.
- [x] Limite de faixa para sensores.
- [x] Tratamento de erro da API Gemini.
- [x] Geração de log de erro controlado.

## 7. Organização e Clean Code

- [x] Código organizado em funções.
- [x] Variáveis com nomes autoexplicativos.
- [x] Comentários e docstrings nos blocos principais.
- [x] Notebook limpo, sem células de rascunho.
- [x] Arquivo `src/pipeline_final_agtech.py` executável por terminal.

## 8. Documentação GitHub/README

- [x] README com badges.
- [x] README com diagnóstico, PEAS, requisitos, arquitetura, métricas, regras e execução.
- [x] Apêndice de IA incluído.
- [x] Estrutura correta: `/notebooks`, `/data`, `/src`, `/logs`, `/assets/images`, `/docs`.
- [x] Aviso para não enviar `.zip` ou `.rar` no GitHub.

## 9. Evidências visuais e métricas

- [x] Imagem geral do projeto.
- [x] Arquitetura do pipeline.
- [x] Gráfico de Loss.
- [x] Comparação antes/depois.
- [x] Gráfico real vs. previsto.
- [x] Log visual do pipeline.

## 10. Apresentação e pitch

- [x] Roteiro técnico de 2 a 3 minutos incluído.
- [x] Roteiro orienta demonstrar código rodando, gráficos e saída Gemini.
- [ ] Inserir link real do vídeo público no README após a gravação.

> Observação: o único item que depende do grupo é a gravação e publicação do vídeo. O repositório já contém o roteiro e o campo correto para inserir o link.

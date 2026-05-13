# Roteiro do Vídeo de Demonstração — 2 a 3 minutos

Objetivo: atender ao critério de apresentação da rubrica, demonstrando código rodando, gráficos evolutivos e inferência do Gemini.

## Tempo sugerido: 2min30s

### 0:00–0:20 — Problema

“Este projeto resolve uma dor da agricultura de precisão: decisões tardias sobre irrigação e controle de pragas. Sem automação inteligente, há desperdício de água, aumento de custos e risco de perda de produtividade.”

### 0:20–0:50 — Solução

“A solução integra sensores agrícolas, uma Rede Neural Artificial, um Sistema Especialista e a API Gemini. A RNA prevê a umidade do solo na próxima hora. O Sistema Especialista usa regras SE/ENTÃO para definir irrigação, manejo de pragas e atuadores. O Gemini explica a decisão em linguagem natural.”

### 0:50–1:20 — Mostrar o repositório

Na tela, mostrar rapidamente:

- `README.md`;
- `/notebooks`;
- `/src`;
- `/data`;
- `/logs`;
- `/assets/images`;
- `/docs`.

Fala sugerida:

“O repositório está organizado em pastas, sem arquivos compactados. O notebook executa o fluxo completo e o código limpo está separado em `src/pipeline_final_agtech.py`.”

### 1:20–1:50 — Mostrar execução e aprendizado

Na tela, executar ou mostrar o notebook:

- célula de treinamento da RNA;
- gráfico de Loss;
- comparação antes/depois;
- métrica de ganho percentual.

Fala sugerida:

“A curva de Loss comprova a evolução do aprendizado. A comparação antes e depois mostra que a previsão da RNA acompanha melhor a umidade real do que o método sem aprendizado.”

### 1:50–2:20 — Mostrar decisão e Gemini

Na tela, mostrar o log final:

- umidade prevista;
- regras acionadas;
- atuadores;
- análise do Gemini ou fallback.

Fala sugerida:

“A decisão técnica é feita pelo Sistema Especialista. O Gemini não decide; ele interpreta o resultado e gera explicações e alertas estratégicos. Caso a API falhe, o pipeline não quebra e usa fallback local.”

### 2:20–2:30 — Encerramento

“Assim, o projeto demonstra uma solução de automação agrícola capaz de prever, decidir e explicar, podendo ser expandida para sensores IoT, drones reais e dashboards agrícolas.”

## Checklist do vídeo

- [ ] Mostrar o repositório.
- [ ] Mostrar notebook executando.
- [ ] Mostrar gráfico de Loss.
- [ ] Mostrar comparação antes/depois.
- [ ] Mostrar log com decisão dos atuadores.
- [ ] Mostrar saída Gemini ou fallback local.
- [ ] Garantir duração entre 2 e 3 minutos.
- [ ] Inserir link público no README.

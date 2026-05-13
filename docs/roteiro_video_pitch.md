# Roteiro para vídeo de demonstração técnica — 2 a 3 minutos

## 0:00–0:20 — Abertura
Apresentar o problema: agricultura de precisão com drones ou robôs agrícolas para identificar pragas e gerenciar recursos hídricos.

## 0:20–0:45 — Arquitetura
Mostrar a imagem `assets/images/arquitetura_pipeline_agtech.png` e explicar o fluxo:
Sensores -> RNA -> Sistema Especialista -> Gemini -> Atuadores.

## 0:45–1:30 — Execução do notebook
Abrir `notebooks/AgTech_Etapa4_Validacao_Final.ipynb` e executar as principais células.
Destacar que o pipeline roda do início ao fim sem intervenção manual.

## 1:30–2:00 — Evidências de aprendizado
Mostrar o gráfico `grafico_loss_rna.png` e explicar que a queda da Loss indica aprendizado.
Mostrar também `comparacao_antes_depois.png`, destacando que a previsão da RNA melhora a tomada de decisão.

## 2:00–2:40 — Decisão e Gemini
Mostrar o log final em `logs/log_pipeline_final.json`.
Explicar os atuadores acionados: bomba de irrigação, pulverizador e drone de inspeção.
Em seguida, mostrar a análise interpretativa gerada pelo Gemini ou o fallback local quando a chave da API não está configurada.

## 2:40–3:00 — Fechamento
Concluir dizendo que o projeto integra visão computacional simulada, previsão por RNA, decisão especialista e explicação por IA generativa, formando uma solução AgTech pronta para avaliação acadêmica e pré-mercado.

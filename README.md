# AgTech: Automação de Precisão com RNA, Sistema Especialista e Gemini

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Google Colab](https://img.shields.io/badge/Google%20Colab-Compatible-orange)
![Scikit--Learn](https://img.shields.io/badge/Scikit--Learn-RNA-green)
![Gemini API](https://img.shields.io/badge/Gemini%20API-Análise%20Interpretativa-purple)
![Status](https://img.shields.io/badge/Etapa%204-Validação%20Final-success)

## 1. Resumo do projeto

Este projeto propõe um agente AgTech para **automação de precisão em drones ou robôs agrícolas**. O sistema utiliza sensores de campo, uma **Rede Neural Artificial** para prever a umidade do solo na próxima hora, um **Sistema Especialista** para tomar decisões técnicas e a **API do Gemini** para gerar uma explicação em linguagem natural.

O objetivo é apoiar decisões no campo, como irrigação, inspeção por drone e pulverização localizada, considerando risco de pragas e disponibilidade hídrica.

## 2. Arquitetura final

![Arquitetura do pipeline](assets/images/arquitetura_pipeline_agtech.png)

Fluxo implementado:

```text
Leitura dos Sensores
        ↓
RNA prevê umidade futura
        ↓
Sistema Especialista aplica regras SE/ENTÃO
        ↓
Gemini gera análise interpretativa
        ↓
Atuadores: bomba, pulverizador e drone
```

## 3. Abordagem escolhida na Etapa 3

A abordagem escolhida foi **Opção A — Redes Neurais Artificiais RNA**.

A RNA foi escolhida porque o sistema precisava de capacidade preditiva. Em vez de decidir irrigação apenas pela umidade atual, o agente passa a prever a **umidade do solo na próxima hora**, antecipando situações de estresse hídrico.

### Métricas obtidas

| Métrica | Valor |
|---|---:|
| MAE da RNA | 1.831 |
| RMSE da RNA | 2.372 |
| R² da RNA | 0.952 |
| MAE antes do aprendizado | 4.501 |
| Épocas treinadas | 453 |

## 4. Evidências visuais

### Gráfico de aprendizado da RNA

![Gráfico de Loss](assets/images/grafico_loss_rna.png)

### Comparação antes e depois do aprendizado

![Comparação antes e depois](assets/images/comparacao_antes_depois.png)

### Log final do pipeline integrado

![Log de execução](assets/images/log_execucao_pipeline.png)

## 5. Sistema Especialista

O Sistema Especialista recebe a previsão da RNA e os dados de sensores. Em seguida, aplica regras rígidas como:

```text
SE umidade prevista < 22% E não há chuva detectada
ENTÃO acionar irrigação crítica com bomba em 100%.

SE confiança de praga >= 70% E área foliar afetada >= 25%
ENTÃO classificar risco como alto.

SE risco de praga alto OU crítico E vento não está alto
ENTÃO acionar pulverização localizada e nova inspeção por drone.
```

## 6. Tratamento de exceções

O código contém validações para evitar falhas abruptas:

- ausência de colunas obrigatórias dos sensores;
- valores nulos ou inválidos;
- falha de autenticação na API do Gemini;
- indisponibilidade temporária da API;
- execução em modo contingência quando `GEMINI_API_KEY` não está configurada.


## 7. Estrutura do repositório

```text
.
├── README.md
├── requirements.txt
├── notebooks/
│   └── AgTech_Etapa4_Validacao_Final.ipynb
├── data/
│   └── sensores_agtech_simulados.csv
├── src/
│   └── pipeline_final_agtech.py
├── logs/
│   ├── log_pipeline_final.json
│   └── metricas_modelo_final.json
├── assets/
│   └── images/
│       ├── arquitetura_pipeline_agtech.png
│       ├── grafico_loss_rna.png
│       ├── comparacao_antes_depois.png
│       ├── previsao_vs_real_rna.png
│       └── log_execucao_pipeline.png
└── docs/
    └── roteiro_video_pitch.md
```

> Observação: não envie `.zip` ou `.rar` no GitHub. Os arquivos devem ficar expostos nas pastas do repositório.

## 8. Como executar no Google Colab

1. Abra o notebook:

```text
notebooks/AgTech_Etapa4_Validacao_Final.ipynb
```

2. Execute a célula de instalação:

```python
%pip install -q -U numpy pandas matplotlib scikit-learn google-genai
```

3. Configure a chave do Gemini no Colab:

```text
Nome do segredo: GEMINI_API_KEY
Valor: sua chave da API
```

4. Execute todas as células em sequência.

O notebook também roda sem a chave, mas nesse caso a explicação final será gerada em modo de contingência local.

## 9. Link do vídeo de demonstração

Inserir aqui o link público do vídeo no YouTube ou Google Drive:

```text
LINK_DO_VIDEO: [https://youtu.be/8vgx0_7GNys]
```

Sugestão: grave um vídeo de 2 a 3 minutos mostrando:

1. estrutura do repositório;
2. execução do notebook;
3. gráfico de Loss;
4. comparação antes/depois;
5. log final com decisão dos atuadores;
6. resposta do Gemini ou fallback local.

## 10. Resultado final esperado

Ao final da execução, o sistema deve mostrar um log parecido com:

```json
{
  "umidade_prevista_proxima_hora_pct": 61.52,
  "decisao_especialista": {
    "risco_praga": "baixo",
    "decisao_irrigacao": "irrigação moderada",
    "vazao_bomba_pct": 65,
    "atuadores": {
      "bomba_irrigacao": "ligada",
      "pulverizador": "desligado",
      "drone_inspecao": "stand-by"
    }
  }
}
```

## 11. Tecnologias utilizadas

- Python
- Google Colab
- Pandas
- NumPy
- Matplotlib
- Scikit-Learn
- Google Gemini API
- Sistema Especialista baseado em regras

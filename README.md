# AgTech: Automação de Precisão com Sistema Especialista e Gemini

## 1. Tema do projeto

Este projeto implementa um agente computacional para **AgTech: Automação de Precisão**, com foco em drones ou robôs agrícolas capazes de apoiar a identificação de pragas e o gerenciamento de recursos hídricos em lavouras.

O sistema integra três camadas principais:

1. **Visão Computacional com Redes Neurais**  
   Responsável por identificar indícios de pragas em imagens de campo. Nesta versão acadêmica, a saída da rede neural é simulada por dados estruturados: praga detectada, confiança da classificação e dano foliar estimado.

2. **Sistema Especialista**  
   Responsável pela decisão técnica. O motor de decisão usa regras do tipo **SE/ENTÃO** para classificar risco de praga, risco hídrico e prioridade operacional.

3. **API do Gemini**  
   Responsável pela **Análise Interpretativa**. O Gemini não toma a decisão técnica; ele recebe os outputs do Sistema Especialista e gera uma explicação em linguagem natural, com alertas estratégicos e sugestões de próximos dados a coletar.

---

## 2. Abordagem escolhida

A abordagem escolhida foi a **Opção B: Sistemas Especialistas**.

Essa escolha é adequada porque o problema envolve diagnóstico e classificação com base em conhecimento técnico, por exemplo:

- Se a praga foi detectada com alta confiança e há alto dano foliar, o risco deve ser crítico.
- Se o solo está seco, há pouca chuva prevista e o reservatório está adequado, o sistema deve recomendar irrigação controlada.
- Se há chuva prevista suficiente, a irrigação deve ser suspensa ou reavaliada.

---

## 3. Arquitetura lógica

```text
Imagem capturada pelo drone/robô
        ↓
Rede Neural de Visão Computacional
        ↓
Saída da IA visual:
- praga_detectada
- confianca_visao
- dano_foliar_pct
        ↓
Dados ambientais e hídricos:
- umidade_solo_pct
- chuva_prevista_mm
- nivel_reservatorio_pct
- temperatura_c
        ↓
Sistema Especialista
        ↓
Decisão técnica:
- risco_praga
- acao_praga
- risco_hidrico
- acao_hidrica
- prioridade_operacional
        ↓
Gemini API
        ↓
Análise Interpretativa:
- explicação em linguagem natural
- justificativa
- alertas estratégicos
- próximos dados recomendados
```

---

## 4. Árvore de decisão simplificada

### 4.1 Decisão de pragas

```text
Praga detectada?
├── Não
│   └── Risco baixo → monitoramento normal
└── Sim
    ├── Confiança ≥ 0,80 e dano foliar ≥ 25%
    │   └── Risco crítico → intervenção localizada e alerta técnico
    ├── Confiança ≥ 0,70 e dano foliar entre 10% e 25%
    │   └── Risco alto → inspeção prioritária e manejo localizado
    ├── Confiança ≥ 0,50 ou dano foliar entre 5% e 10%
    │   └── Risco médio → monitoramento reforçado
    └── Caso contrário
        └── Risco baixo → monitoramento normal
```

### 4.2 Decisão hídrica

```text
Chuva prevista ≥ 10 mm?
├── Sim
│   └── Suspender irrigação e reavaliar após chuva
└── Não
    ├── Umidade < 30%, chuva < 5 mm e reservatório ≥ 30%
    │   └── Acionar irrigação controlada
    ├── Umidade < 30%, chuva < 5 mm e reservatório < 30%
    │   └── Irrigação restrita e alerta de reservatório baixo
    ├── Umidade entre 30% e 45%, chuva < 3 mm e temperatura > 32 ºC
    │   └── Irrigação moderada preventiva
    └── Caso contrário
        └── Manter monitoramento hídrico
```

---

## 5. Regras da base de conhecimento

### Regras para pragas

| Regra | Condição | Saída |
|---|---|---|
| R1 | Praga detectada, confiança ≥ 0,80 e dano foliar ≥ 25% | Risco crítico |
| R2 | Praga detectada, confiança ≥ 0,70 e dano foliar entre 10% e 25% | Risco alto |
| R3 | Praga detectada, confiança ≥ 0,50 ou dano foliar entre 5% e 10% | Risco médio |
| R4 | Sem praga relevante ou dano baixo | Risco baixo |

### Regras para recursos hídricos

| Regra | Condição | Saída |
|---|---|---|
| H1 | Umidade < 30%, chuva < 5 mm e reservatório ≥ 30% | Irrigação controlada |
| H2 | Umidade < 30%, chuva < 5 mm e reservatório < 30% | Irrigação restrita |
| H3 | Umidade entre 30% e 45%, chuva < 3 mm e temperatura > 32 ºC | Irrigação moderada |
| H4 | Chuva prevista ≥ 10 mm | Suspender irrigação |
| H5 | Condições dentro do aceitável | Monitoramento hídrico |

---

## 6. Como executar no Google Colab

1. Abra o arquivo `AgTech_Sistema_Especialista_Gemini.ipynb` no Google Colab.
2. Execute a célula de instalação das bibliotecas.
3. Crie uma chave da API no Google AI Studio.
4. No Colab, abra a aba de **Segredos**.
5. Crie um segredo chamado:

```text
GEMINI_API_KEY
```

6. Cole sua chave da API nesse segredo.
7. Libere o acesso do notebook ao segredo.
8. Execute todas as células.

---

## 7. Estrutura sugerida do repositório

```text
agtech-automacao-precisao/
│
├── README.md
├── notebooks/
│   └── AgTech_Sistema_Especialista_Gemini.ipynb
│
├── logs/
│   ├── logs_sistema_especialista.json
│   ├── resumo_logs.csv
│   └── analises_gemini.json
│
└── docs/
    └── arquitetura_logica.md
```

---

## 8. Exemplo de log de saída do Sistema Especialista

```json
{
  "entrada": {
    "talhao": "T-01",
    "cultura": "Soja",
    "praga_detectada": "lagarta",
    "confianca_visao": 0.92,
    "dano_foliar_pct": 31,
    "umidade_solo_pct": 24,
    "chuva_prevista_mm": 1,
    "nivel_reservatorio_pct": 68,
    "temperatura_c": 33.5
  },
  "decisao_praga": {
    "risco_praga": "crítico",
    "acao_praga": "intervenção localizada imediata e alerta ao responsável técnico",
    "regra_acionada": "R1: praga confirmada com alta confiança e dano foliar severo"
  },
  "decisao_hidrica": {
    "risco_hidrico": "alto",
    "acao_hidrica": "acionar irrigação controlada",
    "regra_acionada_hidrica": "H1: solo seco, baixa chuva e reservatório adequado"
  },
  "prioridade_operacional": "prioridade máxima: tratar foco de praga antes de ampliar irrigação"
}
```

---

## 9. Exemplo esperado de análise interpretativa do Gemini

```text
1. Resumo da situação
O talhão T-01 apresenta detecção de lagarta com alta confiança da visão computacional e dano foliar severo.

2. Justificativa da decisão
A regra R1 foi acionada porque a confiança da detecção é de 0,92 e o dano foliar é de 31%, indicando risco crítico de praga.

3. Ação recomendada
Realizar intervenção localizada no foco detectado e acionar o responsável técnico.

4. Alertas estratégicos
Evitar ampliar irrigação antes da intervenção, pois isso pode afetar a eficiência operacional do manejo.

5. Próximos dados que devem ser coletados
Novas imagens do talhão, mapa de severidade da infestação e leitura atualizada da umidade do solo.
```

---

## 10. Resultado esperado

Ao final da execução, o notebook deve demonstrar:

- inferência lógica do Sistema Especialista;
- tabela de decisões por talhão;
- log JSON detalhado;
- chamada real à API do Gemini;
- análise interpretativa em linguagem natural.

---

## 11. Observações acadêmicas

O projeto atende ao requisito de que o agente computacional tenha um motor próprio de decisão. A camada generativa não substitui a lógica de controle, apenas traduz e contextualiza as decisões para o operador humano.

Essa separação melhora a confiabilidade do sistema, pois as regras técnicas permanecem auditáveis e explicáveis.

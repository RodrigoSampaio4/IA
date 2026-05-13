# Apêndice de Uso de IA

## Finalidade do uso de IA no projeto

A Inteligência Artificial foi utilizada em dois níveis diferentes:

1. **IA preditiva**, implementada por uma Rede Neural Artificial em Python, responsável por prever a umidade do solo na próxima hora.
2. **IA generativa**, representada pela API Gemini, responsável apenas pela análise interpretativa em linguagem natural.

## Separação entre decisão técnica e interpretação

A decisão técnica do agente não é feita pelo Gemini. O Gemini recebe um resultado já calculado pelo pipeline e explica a decisão para o usuário final.

Fluxo de decisão:

```text
Sensores -> RNA -> Sistema Especialista -> Atuadores
```

Fluxo de interpretação:

```text
Resultado técnico -> Gemini API -> Explicação em linguagem natural
```

## Papel da RNA

A RNA aprende padrões dos dados simulados de sensores e prevê a umidade futura do solo. Essa previsão é usada para antecipar a decisão de irrigação.

Exemplo:

```text
Entrada: temperatura, umidade do ar, umidade do solo, chuva, vento, NDVI e pragas
Saída: umidade prevista do solo na próxima hora
```

## Papel do Sistema Especialista

O Sistema Especialista aplica regras SE/ENTÃO para converter a previsão e os dados de pragas em ações de controle.

Exemplo:

```text
SE umidade prevista < 32% E chuva < 2,5 mm
ENTÃO irrigação moderada com bomba em 65%.
```

## Papel do Gemini

O Gemini recebe o log técnico e gera uma explicação contextual com:

- previsão feita pela RNA;
- regras acionadas pelo Sistema Especialista;
- atuadores definidos;
- alertas estratégicos;
- limitação dos dados simulados.

## Limitações

- Os dados são simulados para validação acadêmica.
- Em ambiente real, seria necessário treinar a RNA com histórico de campo.
- O Sistema Especialista deve ser calibrado por agrônomos.
- O Gemini depende de chave de API válida para gerar a resposta real.
- Quando a API não está disponível, o sistema utiliza fallback local.

## Transparência

O projeto preserva transparência porque a decisão final sempre aparece no log com:

- leitura dos sensores;
- umidade prevista;
- regras acionadas;
- justificativa técnica;
- atuadores definidos;
- análise Gemini ou fallback local.

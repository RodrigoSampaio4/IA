# Projeto - Sistema Especialista com Integração Gemini

## 👥 Integrantes
- Rodrigo Sampaio - 062220027
- Rodrigo Batalha - 062220003
- Felipe Marques - 062220025
- Gabriel Damazio - 062220005

---

## 📌 Descrição
Este projeto implementa um Sistema Especialista baseado em regras para análise de risco em equipamentos industriais.

O sistema utiliza variáveis como:
- Temperatura
- Vibração
- Ruído

Com base nesses dados, o sistema toma decisões utilizando regras SE/ENTÃO.

---

## 🧠 Arquitetura Lógica

### Regras:

- SE temperatura > 80 E vibração > 70 → ALTO RISCO
- SE temperatura > 60 OU vibração > 50 → RISCO MODERADO
- SE ruído > 70 → VERIFICAR COMPONENTES
- SENÃO → OPERAÇÃO NORMAL

---

## 🤖 Integração com Gemini

A API do Gemini é utilizada para:
- Explicar a decisão do sistema
- Sugerir ações corretivas

---

## 📊 Exemplo de Saída

Decisão do Sistema: ALTO RISCO DE FALHA

Explicação do Gemini:
"O sistema identificou altos níveis de temperatura e vibração, indicando possível falha iminente..."

---

## ▶️ Execução

1. Abrir o notebook no Google Colab
2. Inserir a API KEY do Gemini
3. Executar todas as células

---

## ✅ Critério de Sucesso

O sistema executa:
- Inferência lógica corretamente
- Integração com API do Gemini sem erros

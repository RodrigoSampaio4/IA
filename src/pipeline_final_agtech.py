"""Pipeline final AgTech - Etapa 4.

Fluxo: sensores -> RNA -> Sistema Especialista -> Gemini -> atuadores.
O arquivo foi feito para ser simples, reprodutível e com tratamento de exceções.
"""

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

SEED = 42
FEATURES = [
    "temperatura_c", "umidade_ar_pct", "umidade_solo_pct", "chuva_mm",
    "vento_kmh", "ndvi", "confianca_praga_pct", "area_foliar_afetada_pct"
]
TARGET = "umidade_solo_proxima_hora_pct"


def gerar_dados_sensores(n=720, seed=SEED):
    """Gera uma base simulada de sensores agrícolas para validação do agente."""
    rng = np.random.default_rng(seed)
    horas = np.arange(n)
    timestamps = pd.date_range("2026-05-01 06:00:00", periods=n, freq="h")
    temperatura = 25 + 6*np.sin(2*np.pi*(horas % 24)/24) + rng.normal(0, 1.5, n)
    umidade_ar = np.clip(66 - 0.8*(temperatura - 25) + rng.normal(0, 5.0, n), 25, 95)
    chuva_mm = rng.gamma(shape=1.1, scale=2.4, size=n)
    chuva_mm[rng.random(n) < 0.65] = 0
    vento_kmh = np.clip(9 + rng.normal(0, 3, n), 1, 28)
    ndvi = np.clip(0.68 + rng.normal(0, 0.08, n), 0.35, 0.92)
    confianca_praga = np.clip(22 + 80*(0.72 - ndvi) + rng.normal(0, 15, n), 0, 100)
    area_foliar_afetada = np.clip(0.55*confianca_praga + rng.normal(0, 9, n), 0, 100)
    umidade_solo = np.clip(
        45 + 10*np.sin(2*np.pi*(horas % 168)/168)
        - 0.25*(temperatura - 25) + 0.35*chuva_mm
        - 0.06*area_foliar_afetada + rng.normal(0, 4.5, n),
        12, 82
    )
    umidade_futura = np.clip(
        umidade_solo - 0.55*np.maximum(temperatura - 24, 0)
        - 0.12*vento_kmh + 0.08*umidade_ar
        + 1.8*chuva_mm - 0.07*area_foliar_afetada
        + rng.normal(0, 2.0, n),
        8, 88
    )
    df = pd.DataFrame({
        "timestamp": timestamps,
        "temperatura_c": np.round(temperatura, 2),
        "umidade_ar_pct": np.round(umidade_ar, 2),
        "umidade_solo_pct": np.round(umidade_solo, 2),
        "chuva_mm": np.round(chuva_mm, 2),
        "vento_kmh": np.round(vento_kmh, 2),
        "ndvi": np.round(ndvi, 3),
        "confianca_praga_pct": np.round(confianca_praga, 2),
        "area_foliar_afetada_pct": np.round(area_foliar_afetada, 2),
        TARGET: np.round(umidade_futura, 2),
    })
    return df

def validar_leitura_sensor(leitura):
    """Impede que o pipeline rode com campos ausentes, nulos ou inválidos."""
    faltantes = sorted(set(FEATURES) - set(leitura.keys()))
    if faltantes:
        raise ValueError(f"Leitura de sensores incompleta. Campos ausentes: {faltantes}")
    for chave in FEATURES:
        valor = leitura[chave]
        if valor is None or not np.isfinite(float(valor)):
            raise ValueError(f"Parâmetro inválido em {chave}: {valor}")
    return True


def treinar_rna(df):
    """Treina a RNA que prevê a umidade do solo na próxima hora."""
    x_train, x_test, y_train, y_test = train_test_split(
        df[FEATURES], df[TARGET], test_size=0.25, shuffle=False
    )
    modelo = Pipeline([
        ("padronizador", StandardScaler()),
        ("rna", MLPRegressor(
            hidden_layer_sizes=(64, 32), activation="relu", solver="adam",
            random_state=SEED, max_iter=700, early_stopping=True,
            validation_fraction=0.15, n_iter_no_change=30, learning_rate_init=0.002
        )),
    ])
    modelo.fit(x_train, y_train)
    y_pred = modelo.predict(x_test)
    y_baseline = x_test["umidade_solo_pct"].to_numpy()
    metricas = {
        "mae_rna": float(mean_absolute_error(y_test, y_pred)),
        "rmse_rna": float(mean_squared_error(y_test, y_pred) ** 0.5),
        "r2_rna": float(r2_score(y_test, y_pred)),
        "mae_baseline_sem_aprendizado": float(mean_absolute_error(y_test, y_baseline)),
        "rmse_baseline_sem_aprendizado": float(mean_squared_error(y_test, y_baseline) ** 0.5),
        "epocas_treinadas": int(modelo.named_steps["rna"].n_iter_),
    }
    return modelo, metricas


def classificar_risco_praga(confianca_praga_pct, area_foliar_afetada_pct):
    """Classifica o risco de praga com base na visão computacional simulada."""
    if confianca_praga_pct >= 85 and area_foliar_afetada_pct >= 35:
        return "crítico"
    if confianca_praga_pct >= 70 and area_foliar_afetada_pct >= 25:
        return "alto"
    if confianca_praga_pct >= 50 or area_foliar_afetada_pct >= 18:
        return "moderado"
    if confianca_praga_pct >= 30 or area_foliar_afetada_pct >= 10:
        return "baixo"
    return "normal"


def sistema_especialista(leitura, umidade_prevista_pct):
    """Aplica regras SE/ENTÃO para decidir irrigação, pulverização e inspeção."""
    validar_leitura_sensor(leitura)
    risco_praga = classificar_risco_praga(
        leitura["confianca_praga_pct"], leitura["area_foliar_afetada_pct"]
    )
    chuva_detectada = leitura["chuva_mm"] >= 2.5
    vento_alto = leitura["vento_kmh"] >= 18
    if umidade_prevista_pct < 22 and not chuva_detectada:
        decisao_irrigacao, vazao = "irrigação crítica", 100
    elif umidade_prevista_pct < 32 and not chuva_detectada:
        decisao_irrigacao, vazao = "irrigação moderada", 65
    elif umidade_prevista_pct < 42:
        decisao_irrigacao, vazao = "monitorar umidade", 25
    else:
        decisao_irrigacao, vazao = "não irrigar", 0
    if risco_praga in ["alto", "crítico"] and not vento_alto:
        manejo, pulverizador = "acionar pulverização localizada e nova inspeção por drone", "ligado"
    elif risco_praga in ["alto", "crítico"] and vento_alto:
        manejo, pulverizador = "adiar pulverização e priorizar nova inspeção por drone devido ao vento", "bloqueado por vento"
    elif risco_praga == "moderado":
        manejo, pulverizador = "agendar nova varredura em até 24h", "desligado"
    else:
        manejo, pulverizador = "manter monitoramento padrão", "desligado"
    return {
        "risco_praga": risco_praga,
        "decisao_irrigacao": decisao_irrigacao,
        "vazao_bomba_pct": vazao,
        "manejo_praga": manejo,
        "atuadores": {
            "bomba_irrigacao": "ligada" if vazao > 0 else "desligada",
            "vazao_bomba_pct": vazao,
            "pulverizador": pulverizador,
            "drone_inspecao": "acionado" if risco_praga in ["moderado", "alto", "crítico"] else "stand-by",
        },
    }


def explicar_com_gemini(resultado_pipeline):
    """Envia o resultado técnico para o Gemini; usa fallback se a API falhar."""
    prompt = f"""
Explique a decisão deste agente AgTech de automação de precisão.
Comente a previsão da RNA, as regras do Sistema Especialista, os atuadores e os alertas estratégicos.

Resultado técnico:
{json.dumps(resultado_pipeline, ensure_ascii=False, indent=2)}
"""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        try:
            from google.colab import userdata
            if not api_key:
                api_key = userdata.get("GEMINI_API_KEY")
        except Exception:
            pass
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY não configurada.")
        from google import genai
        cliente = genai.Client(api_key=api_key)
        modelo = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")
        resposta = cliente.models.generate_content(model=modelo, contents=prompt)
        return {"modo": "gemini_api", "texto": resposta.text}
    except Exception as erro:
        decisao = resultado_pipeline.get("decisao_especialista", {})
        texto = (
            "MODO CONTINGÊNCIA: API do Gemini indisponível ou chave não configurada. "
            f"A RNA previu umidade futura de {resultado_pipeline.get('umidade_prevista_proxima_hora_pct')}%. "
            f"O Sistema Especialista decidiu {decisao.get('decisao_irrigacao')} e classificou risco de praga como {decisao.get('risco_praga')}."
        )
        return {"modo": "fallback_local", "erro": str(erro), "texto": texto}


def executar_pipeline(df, modelo):
    """Executa o fluxo integrado do início ao fim sem intervenção manual."""
    leitura = df.iloc[-1][FEATURES].astype(float).to_dict()
    validar_leitura_sensor(leitura)
    umidade_prevista = float(modelo.predict(pd.DataFrame([leitura])[FEATURES])[0])
    decisao = sistema_especialista(leitura, umidade_prevista)
    resultado = {
        "leitura_sensores": leitura,
        "umidade_prevista_proxima_hora_pct": round(umidade_prevista, 2),
        "decisao_especialista": decisao,
    }
    resultado["analise_interpretativa"] = explicar_com_gemini(resultado)
    return resultado


if __name__ == "__main__":
    base = Path(__file__).resolve().parents[1]
    logs = base / "logs"
    logs.mkdir(exist_ok=True)
    dados = gerar_dados_sensores()
    modelo, metricas = treinar_rna(dados)
    resultado = executar_pipeline(dados, modelo)
    (logs / "metricas_modelo_final.json").write_text(json.dumps(metricas, indent=2, ensure_ascii=False), encoding="utf-8")
    (logs / "log_pipeline_final.json").write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

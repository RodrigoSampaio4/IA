"""Pipeline final AgTech — Etapa 4.

Fluxo validado pela rubrica: Sensores -> Previsão RNA -> Sistema Especialista
-> Gemini/Fallback -> Atuadores.

O objetivo deste arquivo é permitir execução direta por terminal ou Colab, com
código limpo, variáveis autoexplicativas e tratamento de exceções para falhas de
sensores, dados inválidos e indisponibilidade da API Gemini.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

SEED = 42
FEATURES = [
    "temperatura_c",
    "umidade_ar_pct",
    "umidade_solo_pct",
    "chuva_mm",
    "vento_kmh",
    "ndvi",
    "confianca_praga_pct",
    "area_foliar_afetada_pct",
]
TARGET = "umidade_solo_proxima_hora_pct"
COLUNAS_OBRIGATORIAS = FEATURES + [TARGET]

LIMITES_VALIDOS = {
    "temperatura_c": (-5, 55),
    "umidade_ar_pct": (0, 100),
    "umidade_solo_pct": (0, 100),
    "chuva_mm": (0, 120),
    "vento_kmh": (0, 120),
    "ndvi": (0, 1),
    "confianca_praga_pct": (0, 100),
    "area_foliar_afetada_pct": (0, 100),
    TARGET: (0, 100),
}


def gerar_dados_sensores(n: int = 720, seed: int = SEED) -> pd.DataFrame:
    """Gera dados simulados coerentes com uma lavoura monitorada por IoT/drone."""
    rng = np.random.default_rng(seed)
    horas = np.arange(n)
    timestamps = pd.date_range("2026-05-01 06:00:00", periods=n, freq="h")

    temperatura = 25 + 6 * np.sin(2 * np.pi * (horas % 24) / 24) + rng.normal(0, 1.5, n)
    umidade_ar = np.clip(66 - 0.8 * (temperatura - 25) + rng.normal(0, 5.0, n), 25, 95)
    chuva_mm = rng.gamma(shape=1.1, scale=2.4, size=n)
    chuva_mm[rng.random(n) < 0.65] = 0
    vento_kmh = np.clip(9 + rng.normal(0, 3, n), 1, 28)
    ndvi = np.clip(0.68 + rng.normal(0, 0.08, n), 0.35, 0.92)

    # A confiança de praga cresce quando o NDVI cai, simulando saída de visão computacional.
    confianca_praga = np.clip(22 + 80 * (0.72 - ndvi) + rng.normal(0, 15, n), 0, 100)
    area_foliar_afetada = np.clip(0.55 * confianca_praga + rng.normal(0, 9, n), 0, 100)

    umidade_solo = np.clip(
        45
        + 10 * np.sin(2 * np.pi * (horas % 168) / 168)
        - 0.25 * (temperatura - 25)
        + 0.35 * chuva_mm
        - 0.06 * area_foliar_afetada
        + rng.normal(0, 4.5, n),
        12,
        82,
    )

    umidade_futura = np.clip(
        umidade_solo
        - 0.55 * np.maximum(temperatura - 24, 0)
        - 0.12 * vento_kmh
        + 0.08 * umidade_ar
        + 1.8 * chuva_mm
        - 0.07 * area_foliar_afetada
        + rng.normal(0, 2.0, n),
        8,
        88,
    )

    return pd.DataFrame(
        {
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
        }
    )


def _campos_faltantes(campos_esperados: Iterable[str], campos_recebidos: Iterable[str]) -> list[str]:
    """Retorna campos obrigatórios ausentes de forma ordenada."""
    return sorted(set(campos_esperados) - set(campos_recebidos))


def validar_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Valida e higieniza o dataset, evitando que o treinamento quebre abruptamente."""
    if df is None or df.empty:
        raise ValueError("Dataset vazio: não há leituras suficientes para treinar a RNA.")

    faltantes = _campos_faltantes(COLUNAS_OBRIGATORIAS, df.columns)
    if faltantes:
        raise ValueError(f"Colunas obrigatórias ausentes no dataset: {faltantes}")

    df_limpo = df.copy()
    for coluna in COLUNAS_OBRIGATORIAS:
        df_limpo[coluna] = pd.to_numeric(df_limpo[coluna], errors="coerce")
        if df_limpo[coluna].isna().all():
            raise ValueError(f"A coluna {coluna} não possui valores numéricos válidos.")
        df_limpo[coluna] = df_limpo[coluna].fillna(df_limpo[coluna].median())
        minimo, maximo = LIMITES_VALIDOS[coluna]
        df_limpo[coluna] = df_limpo[coluna].clip(minimo, maximo)

    return df_limpo


def validar_leitura_sensor(leitura: Dict[str, Any]) -> Dict[str, float]:
    """Valida uma leitura individual e devolve valores numéricos normalizados."""
    faltantes = _campos_faltantes(FEATURES, leitura.keys())
    if faltantes:
        raise ValueError(f"Leitura de sensores incompleta. Campos ausentes: {faltantes}")

    leitura_validada: Dict[str, float] = {}
    for chave in FEATURES:
        try:
            valor = float(leitura[chave])
        except (TypeError, ValueError) as erro:
            raise ValueError(f"Valor inválido em {chave}: {leitura[chave]}") from erro
        if not np.isfinite(valor):
            raise ValueError(f"Valor não finito em {chave}: {valor}")
        minimo, maximo = LIMITES_VALIDOS[chave]
        leitura_validada[chave] = float(np.clip(valor, minimo, maximo))

    return leitura_validada


def treinar_rna(df: pd.DataFrame) -> Tuple[Pipeline, Dict[str, float], Dict[str, Any]]:
    """Treina a RNA e retorna métricas que comprovam a evolução do aprendizado."""
    df_limpo = validar_dataset(df)
    x_train, x_test, y_train, y_test = train_test_split(
        df_limpo[FEATURES], df_limpo[TARGET], test_size=0.25, shuffle=False
    )

    modelo = Pipeline(
        [
            ("padronizador", StandardScaler()),
            (
                "rna",
                MLPRegressor(
                    hidden_layer_sizes=(64, 32),
                    activation="relu",
                    solver="adam",
                    random_state=SEED,
                    max_iter=700,
                    early_stopping=True,
                    validation_fraction=0.15,
                    n_iter_no_change=30,
                    learning_rate_init=0.002,
                ),
            ),
        ]
    )

    modelo.fit(x_train, y_train)
    y_pred = modelo.predict(x_test)
    y_baseline = x_test["umidade_solo_pct"].to_numpy()

    metricas = {
        "mae_rna": round(float(mean_absolute_error(y_test, y_pred)), 3),
        "rmse_rna": round(float(mean_squared_error(y_test, y_pred) ** 0.5), 3),
        "r2_rna": round(float(r2_score(y_test, y_pred)), 3),
        "mae_baseline_sem_aprendizado": round(float(mean_absolute_error(y_test, y_baseline)), 3),
        "rmse_baseline_sem_aprendizado": round(float(mean_squared_error(y_test, y_baseline) ** 0.5), 3),
        "epocas_treinadas": int(modelo.named_steps["rna"].n_iter_),
        "ganho_percentual_mae": round(
            100 * (1 - mean_absolute_error(y_test, y_pred) / mean_absolute_error(y_test, y_baseline)), 2
        ),
    }

    evidencias = {
        "y_test": y_test.to_numpy().tolist(),
        "y_pred": y_pred.tolist(),
        "y_baseline": y_baseline.tolist(),
        "loss_curve": modelo.named_steps["rna"].loss_curve_,
    }
    return modelo, metricas, evidencias


def classificar_risco_praga(confianca_praga_pct: float, area_foliar_afetada_pct: float) -> str:
    """Classifica risco de pragas usando regras rígidas de conhecimento especialista."""
    if confianca_praga_pct >= 85 and area_foliar_afetada_pct >= 35:
        return "crítico"
    if confianca_praga_pct >= 70 and area_foliar_afetada_pct >= 25:
        return "alto"
    if confianca_praga_pct >= 50 or area_foliar_afetada_pct >= 18:
        return "moderado"
    if confianca_praga_pct >= 30 or area_foliar_afetada_pct >= 10:
        return "baixo"
    return "normal"


def sistema_especialista(leitura: Dict[str, Any], umidade_prevista_pct: float) -> Dict[str, Any]:
    """Aplica regras SE/ENTÃO para definir irrigação, manejo de pragas e atuadores."""
    leitura_validada = validar_leitura_sensor(leitura)
    umidade_prevista_pct = float(np.clip(umidade_prevista_pct, 0, 100))

    regras_acionadas: list[str] = []
    risco_praga = classificar_risco_praga(
        leitura_validada["confianca_praga_pct"], leitura_validada["area_foliar_afetada_pct"]
    )
    regras_acionadas.append(f"Risco de praga classificado como {risco_praga}.")

    chuva_detectada = leitura_validada["chuva_mm"] >= 2.5
    vento_alto = leitura_validada["vento_kmh"] >= 18

    if umidade_prevista_pct < 22 and not chuva_detectada:
        decisao_irrigacao, vazao = "irrigação crítica", 100
        regras_acionadas.append("SE umidade prevista < 22% E chuva < 2,5 mm ENTÃO bomba em 100%.")
    elif umidade_prevista_pct < 32 and not chuva_detectada:
        decisao_irrigacao, vazao = "irrigação moderada", 65
        regras_acionadas.append("SE umidade prevista < 32% E chuva < 2,5 mm ENTÃO bomba em 65%.")
    elif umidade_prevista_pct < 42:
        decisao_irrigacao, vazao = "monitorar umidade", 25
        regras_acionadas.append("SE umidade prevista < 42% ENTÃO manter vazão preventiva em 25%.")
    else:
        decisao_irrigacao, vazao = "não irrigar", 0
        regras_acionadas.append("SE umidade prevista >= 42% ENTÃO não irrigar.")

    if risco_praga in {"alto", "crítico"} and not vento_alto:
        manejo, pulverizador = "acionar pulverização localizada e nova inspeção por drone", "ligado"
        regras_acionadas.append("SE risco alto/crítico E vento < 18 km/h ENTÃO pulverização localizada.")
    elif risco_praga in {"alto", "crítico"} and vento_alto:
        manejo, pulverizador = "adiar pulverização e priorizar inspeção por drone devido ao vento", "bloqueado por vento"
        regras_acionadas.append("SE risco alto/crítico E vento >= 18 km/h ENTÃO bloquear pulverização por segurança.")
    elif risco_praga == "moderado":
        manejo, pulverizador = "agendar nova varredura em até 24h", "desligado"
        regras_acionadas.append("SE risco moderado ENTÃO nova varredura em até 24h.")
    else:
        manejo, pulverizador = "manter monitoramento padrão", "desligado"
        regras_acionadas.append("SE risco normal/baixo ENTÃO manter monitoramento padrão.")

    drone_inspecao = "acionado" if risco_praga in {"moderado", "alto", "crítico"} else "stand-by"
    return {
        "risco_praga": risco_praga,
        "decisao_irrigacao": decisao_irrigacao,
        "vazao_bomba_pct": vazao,
        "manejo_praga": manejo,
        "regras_acionadas": regras_acionadas,
        "justificativa_tecnica": (
            f"A umidade prevista foi {umidade_prevista_pct:.2f}%. "
            f"Chuva detectada: {'sim' if chuva_detectada else 'não'}. "
            f"Vento alto: {'sim' if vento_alto else 'não'}. "
            f"Risco de praga: {risco_praga}."
        ),
        "atuadores": {
            "bomba_irrigacao": "ligada" if vazao > 0 else "desligada",
            "vazao_bomba_pct": vazao,
            "pulverizador": pulverizador,
            "drone_inspecao": drone_inspecao,
        },
    }


def explicar_com_gemini(resultado_pipeline: Dict[str, Any]) -> Dict[str, str]:
    """Interpreta a decisão técnica no Gemini; aplica fallback local se houver falha."""
    prompt = f"""
Você é um especialista em AgTech, automação agrícola, visão computacional e irrigação de precisão.
A decisão técnica já foi tomada por uma RNA e por um Sistema Especialista. Não altere a decisão.

Gere uma análise interpretativa em português, com tom técnico e objetivo, contendo:
1. Explicação da previsão da RNA e por que ela influencia a irrigação.
2. Regras do Sistema Especialista que justificam a ação.
3. Atuadores acionados e motivo operacional.
4. Alertas estratégicos de campo: risco hídrico, risco de praga, vento/chuva e próxima ação recomendada.
5. Limitação: informe que os dados são simulados para validação acadêmica.

Resultado técnico em JSON:
{json.dumps(resultado_pipeline, ensure_ascii=False, indent=2)}
"""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        try:
            from google.colab import userdata  # type: ignore

            if not api_key:
                api_key = userdata.get("GEMINI_API_KEY")
        except Exception:
            pass

        if not api_key:
            raise RuntimeError("GEMINI_API_KEY não configurada no ambiente de execução.")

        from google import genai  # type: ignore

        cliente = genai.Client(api_key=api_key)
        modelo = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")
        resposta = cliente.models.generate_content(model=modelo, contents=prompt)
        return {"modo": "gemini_api", "modelo": modelo, "texto": resposta.text}
    except Exception as erro:
        decisao = resultado_pipeline.get("decisao_especialista", {})
        texto = (
            "MODO CONTINGÊNCIA: a API do Gemini não foi acionada, mas o pipeline permaneceu operacional. "
            f"A RNA previu umidade futura de {resultado_pipeline.get('umidade_prevista_proxima_hora_pct')}%. "
            f"O Sistema Especialista decidiu '{decisao.get('decisao_irrigacao')}', com bomba em "
            f"{decisao.get('vazao_bomba_pct')}%, risco de praga '{decisao.get('risco_praga')}' e manejo: "
            f"{decisao.get('manejo_praga')}."
        )
        return {"modo": "fallback_local", "erro": str(erro), "texto": texto}


def executar_pipeline(df: pd.DataFrame, modelo: Pipeline) -> Dict[str, Any]:
    """Executa o fluxo completo: sensores -> RNA -> especialista -> Gemini -> atuadores."""
    df_limpo = validar_dataset(df)
    leitura = df_limpo.iloc[-1][FEATURES].astype(float).to_dict()
    leitura_validada = validar_leitura_sensor(leitura)

    umidade_prevista = float(modelo.predict(pd.DataFrame([leitura_validada])[FEATURES])[0])
    decisao = sistema_especialista(leitura_validada, umidade_prevista)

    resultado = {
        "status_pipeline": "executado_com_sucesso",
        "etapas_executadas": [
            "leitura_sensores",
            "previsao_rna",
            "sistema_especialista",
            "analise_gemini_ou_fallback",
            "acionamento_atuadores",
        ],
        "leitura_sensores": leitura_validada,
        "umidade_prevista_proxima_hora_pct": round(umidade_prevista, 2),
        "decisao_especialista": decisao,
    }
    resultado["analise_interpretativa"] = explicar_com_gemini(resultado)
    return resultado


def salvar_json(caminho: Path, conteudo: Dict[str, Any]) -> None:
    """Salva dicionários em JSON UTF-8 com indentação legível."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(conteudo, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    """Executa a validação final e grava dados, métricas e logs no repositório."""
    base = Path(__file__).resolve().parents[1]
    pasta_logs = base / "logs"
    pasta_dados = base / "data"
    pasta_logs.mkdir(exist_ok=True)
    pasta_dados.mkdir(exist_ok=True)

    try:
        dados = gerar_dados_sensores()
        dados.to_csv(pasta_dados / "sensores_agtech_simulados.csv", index=False, encoding="utf-8")
        modelo, metricas, _ = treinar_rna(dados)
        resultado = executar_pipeline(dados, modelo)
        salvar_json(pasta_logs / "metricas_modelo_final.json", metricas)
        salvar_json(pasta_logs / "log_pipeline_final.json", resultado)
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    except Exception as erro:
        erro_controlado = {
            "status_pipeline": "erro_controlado",
            "tipo_erro": erro.__class__.__name__,
            "mensagem": str(erro),
            "acao_recomendada": "Verificar dataset, colunas obrigatórias, valores dos sensores e dependências instaladas.",
        }
        salvar_json(pasta_logs / "log_erro_controlado.json", erro_controlado)
        print(json.dumps(erro_controlado, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

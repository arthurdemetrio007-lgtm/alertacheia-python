"""Leitura, limpeza e preparo dos dados com pandas."""

import json

import pandas as pd

from . import config


def carregar_bairros():
    """Tabela de bairros com a margem (cm) acima da cota de inundação em que cada um alaga."""
    bairros = pd.read_csv(config.ARQUIVO_BAIRROS)
    bairros["bairro"] = bairros["bairro"].str.strip()
    return bairros


def carregar_leituras_sensor():
    """Leituras do sensor salvas pela coleta, em ordem de tempo e sem valores inválidos."""
    if not config.ARQUIVO_SENSOR.exists():
        return pd.DataFrame(columns=["data", "nivel_cm"])
    leituras = pd.read_csv(config.ARQUIVO_SENSOR)
    leituras["data"] = pd.to_datetime(leituras["data"], utc=True).dt.tz_convert("America/Sao_Paulo")
    leituras["nivel_cm"] = pd.to_numeric(leituras["nivel_cm"], errors="coerce")
    leituras = leituras.dropna(subset=["nivel_cm"])
    # Descarta medições impossíveis (fora da altura em que o sensor está instalado)
    leituras = leituras[leituras["nivel_cm"].between(0, 300)]
    return leituras.sort_values("data").reset_index(drop=True)


def carregar_ocorrencias():
    """Ocorrências dos moradores, com data em horário de Brasília."""
    if not config.ARQUIVO_OCORRENCIAS.exists():
        return pd.DataFrame(columns=["bairro", "gravidade", "status", "data"])
    with open(config.ARQUIVO_OCORRENCIAS, encoding="utf-8") as arquivo:
        ocorrencias = pd.DataFrame(json.load(arquivo))
    if ocorrencias.empty:
        return pd.DataFrame(columns=["bairro", "gravidade", "status", "data"])
    ocorrencias["bairro"] = ocorrencias["bairro"].str.strip()
    ocorrencias["data"] = pd.to_datetime(ocorrencias["createdAt"], utc=True).dt.tz_convert("America/Sao_Paulo")
    return ocorrencias[["bairro", "gravidade", "status", "data"]]


def preparar_serie(leituras, frequencia, janela_taxa, janela_media=3):
    """Deixa a série com intervalo fixo e calcula a taxa de subida.

    - frequencia: intervalo fixo, como "1min" ou "1h"
    - janela_taxa: quantos intervalos olhar para trás ao calcular a taxa
    - janela_media: quantos intervalos entram na média móvel (filtra ruído)

    A taxa de subida é a derivada do nível no tempo, em cm por hora:
    (nível agora - nível de janela_taxa intervalos atrás) / tempo entre eles.
    """
    serie = leituras.set_index("data")["nivel_cm"].resample(frequencia).mean()
    serie = serie.interpolate(limit=janela_taxa)  # preenche falhas curtas, não inventa períodos longos

    horas_por_intervalo = pd.Timedelta(frequencia) / pd.Timedelta(hours=1)
    tabela = pd.DataFrame({"nivel_cm": serie})
    tabela["nivel_suave_cm"] = tabela["nivel_cm"].rolling(janela_media, min_periods=1).mean()
    tabela["taxa_cm_h"] = tabela["nivel_suave_cm"].diff(janela_taxa) / (janela_taxa * horas_por_intervalo)
    return tabela.dropna(subset=["nivel_cm"])

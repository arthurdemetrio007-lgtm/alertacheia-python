"""Coleta dos dados nas APIs, com cópia salva em arquivo.

Se a internet ou a API falhar, o programa segue com a última cópia salva.
"""

import json

import pandas as pd
import requests

from . import config


def baixar_leituras_sensor(quantidade=500):
    """Baixa as últimas leituras do sensor no ThingSpeak e salva em CSV.

    Devolve uma mensagem dizendo o que aconteceu.
    """
    parametros = {"api_key": config.THINGSPEAK_CHAVE_LEITURA, "results": quantidade}
    try:
        resposta = requests.get(config.URL_SENSOR, params=parametros, timeout=config.TEMPO_LIMITE_S)
        resposta.raise_for_status()
        feeds = resposta.json().get("feeds", [])
    except requests.RequestException as erro:
        return f"Sensor: não foi possível baixar ({erro.__class__.__name__}). Usando a cópia salva."

    tabela = pd.DataFrame(feeds)
    if tabela.empty:
        return "Sensor: o canal não tem leituras. Usando a cópia salva."

    # field1 = nível (cm), field2 = estado decidido no dispositivo, field3 = comporta (1 fechada)
    tabela = tabela.rename(
        columns={"created_at": "data", "field1": "nivel_cm", "field2": "estado", "field3": "comporta_fechada"}
    )
    tabela = tabela[["data", "nivel_cm", "estado", "comporta_fechada"]]
    tabela = tabela.dropna(subset=["nivel_cm"])  # linhas sem nível são mudanças de limite, não leituras
    tabela.to_csv(config.ARQUIVO_SENSOR, index=False)
    return f"Sensor: {len(tabela)} leituras salvas em {config.ARQUIVO_SENSOR.name}."


def baixar_ocorrencias():
    """Baixa as ocorrências registradas pelos moradores no app web e salva em JSON."""
    try:
        resposta = requests.get(config.URL_OCORRENCIAS, timeout=config.TEMPO_LIMITE_S)
        if resposta.status_code == 404:  # o MockAPI responde 404 quando não há registros
            ocorrencias = []
        else:
            resposta.raise_for_status()
            ocorrencias = resposta.json()
    except requests.RequestException as erro:
        return f"Ocorrências: não foi possível baixar ({erro.__class__.__name__}). Usando a cópia salva."

    with open(config.ARQUIVO_OCORRENCIAS, "w", encoding="utf-8") as arquivo:
        json.dump(ocorrencias, arquivo, ensure_ascii=False, indent=2)
    return f"Ocorrências: {len(ocorrencias)} registros salvos em {config.ARQUIVO_OCORRENCIAS.name}."

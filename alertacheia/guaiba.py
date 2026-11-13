"""Montagem da série do Guaíba em maio de 2024, na régua do Cais Mauá.

Duas fontes, porque nenhuma cobre a cheia inteira:

1. ANA, estação 87450020 (Usina do Gasômetro), a cada 15 min, a partir de
   03/05/2024 15:00, quando a estação começou a transmitir. O arquivo baixado
   do site Hidro-Telemetria é uma tabela HTML com extensão .xls.
   O site entrega o nível na referência atual da estação. Para voltar à régua
   usada nos boletins de 2024, somamos 120 cm: o pico de 5,37 m publicado pelo
   SGB aparece na série como 417 cm, e os 3,47 m de 02/06/2024 às 9h15 aparecem
   como 229 cm (diferença de 118 a 120 cm).

2. MetSul, valores da régua do Cais Central publicados dia a dia na subida,
   de 26/04 a 03/05/2024 de manhã. Entre um valor e outro, e entre o último
   valor da MetSul e o primeiro da ANA, o nível é interpolado.
"""

import io

import pandas as pd

from . import config

AJUSTE_REGUA_CM = 120


def ler_serie_ana(caminho):
    """Lê a tabela baixada do site da ANA e devolve data e nível (cm, régua da ANA)."""
    with open(caminho, encoding="latin-1") as arquivo:
        tabela = pd.read_html(io.StringIO(arquivo.read()))[0]

    # As primeiras linhas da planilha são a legenda de cores; os dados vêm depois do cabeçalho "Data/Hora"
    inicio = tabela.index[tabela[0] == "Data/Hora"][0] + 1
    dados = tabela.loc[inicio:, [0, 2]]
    dados.columns = ["data", "nivel_cm"]
    dados["data"] = pd.to_datetime(dados["data"], format="%d/%m/%Y %H:%M:%S", errors="coerce")
    dados["nivel_cm"] = pd.to_numeric(dados["nivel_cm"], errors="coerce")
    return dados.dropna().sort_values("data").reset_index(drop=True)


def ler_subida_metsul(caminho, ponto_final):
    """Pontos publicados pela MetSul, interpolados a cada 15 min até o ponto_final.

    ponto_final é o primeiro valor da ANA (data, nível em cm); entra só para ligar as
    duas fontes e não aparece no resultado.
    """
    pontos = pd.read_csv(caminho, parse_dates=["data"])
    serie = pontos.set_index("data")["nivel_m"].mul(100)
    serie.loc[ponto_final[0]] = ponto_final[1]
    serie = serie.sort_index().resample("15min").interpolate("time")
    return serie.iloc[:-1].rename("nivel_cm").reset_index()


def montar_serie_guaiba():
    """Série única na régua do Cais Mauá, com a origem de cada valor."""
    ana = ler_serie_ana(config.ARQUIVO_GUAIBA_ANA)
    ana["nivel_cm"] = ana["nivel_cm"] + AJUSTE_REGUA_CM
    ana["origem"] = "ANA 87450020 (+120 cm)"

    primeiro = ana.iloc[0]
    subida = ler_subida_metsul(config.ARQUIVO_GUAIBA_SUBIDA, (primeiro["data"], primeiro["nivel_cm"]))
    pontos = set(pd.read_csv(config.ARQUIVO_GUAIBA_SUBIDA, parse_dates=["data"])["data"])
    subida["origem"] = subida["data"].map(lambda data: "MetSul" if data in pontos else "interpolado")

    serie = pd.concat([subida, ana], ignore_index=True)
    return serie.sort_values("data").reset_index(drop=True)

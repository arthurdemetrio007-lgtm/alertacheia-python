"""Regras de decisão: em que estado cada bairro está e o que fazer."""

import math

import pandas as pd

from . import config

# Do menos ao mais grave. A posição na lista permite comparar e subir de nível.
ESTADOS = ["NORMAL", "ATENCAO", "ALERTA", "EVACUAR"]


def horas_ate_cota(nivel_cm, taxa_cm_h, cota_cm):
    """Tempo previsto, em horas, até o nível chegar à cota, mantida a taxa atual.

    0 se a água já chegou; infinito se o nível não está subindo.
    """
    if nivel_cm >= cota_cm:
        return 0.0
    if taxa_cm_h is None or math.isnan(taxa_cm_h) or taxa_cm_h <= 0:
        return math.inf
    return (cota_cm - nivel_cm) / taxa_cm_h


def classificar_pelo_nivel(nivel_cm, taxa_cm_h, cota_cm, alerta_cm):
    """Estado do bairro pelo nível medido e pela tendência."""
    horas = horas_ate_cota(nivel_cm, taxa_cm_h, cota_cm)
    if horas == 0:
        estado = "EVACUAR"
    elif horas <= config.HORAS_PARA_ALERTA:
        estado = "ALERTA"
    elif horas <= config.HORAS_PARA_ATENCAO or nivel_cm >= alerta_cm:
        estado = "ATENCAO"
    else:
        estado = "NORMAL"
    return estado, horas


def estado_minimo_pelos_relatos(relatos):
    """Estado mínimo indicado pelos relatos ativos de um bairro.

    Um relato sozinho pode estar errado, então só vários relatos graves levam a evacuar.
    - 2 ou mais relatos de gravidade alta: EVACUAR
    - 1 relato de gravidade alta: ALERTA
    - algum relato de gravidade média: ATENCAO
    """
    graves = (relatos["gravidade"] == "alta").sum()
    medios = (relatos["gravidade"] == "media").sum()
    if graves >= 2:
        return "EVACUAR"
    if graves == 1:
        return "ALERTA"
    if medios >= 1:
        return "ATENCAO"
    return "NORMAL"


def mais_grave(estado_a, estado_b):
    return max(estado_a, estado_b, key=ESTADOS.index)


def acao_recomendada(estado, por_relatos=False):
    """O que o morador deve fazer. A explicação muda se o estado veio dos relatos ou do nível."""
    match (estado, por_relatos):
        case ("EVACUAR", False):
            return "Água na rua. Saia agora para um lugar alto ou abrigo e desligue a energia."
        case ("EVACUAR", True):
            return "Vários moradores relatam água entrando nas casas. Saia agora para um lugar alto ou abrigo."
        case ("ALERTA", False):
            return "A água deve chegar em poucas horas. Separe documentos e remédios e prepare a saída."
        case ("ALERTA", True):
            return "Moradores relatam alagamento grave no bairro. Separe documentos e remédios e prepare a saída."
        case ("ATENCAO", False):
            return "Nível subindo. Acompanhe os avisos e tire objetos do chão."
        case ("ATENCAO", True):
            return "Moradores relatam ruas alagadas. Evite circular por elas e tire objetos do chão."
        case _:
            return "Sem risco previsto agora."


def relatos_ativos(ocorrencias, referencia):
    """Relatos não resolvidos registrados nas últimas horas antes da referência."""
    if ocorrencias is None or ocorrencias.empty:
        return pd.DataFrame(columns=["bairro", "gravidade", "status", "data"])
    inicio = referencia - pd.Timedelta(hours=config.HORAS_RELATOS_RECENTES)
    ativos = ocorrencias[
        (ocorrencias["status"] != "resolvida") & (ocorrencias["data"].between(inicio, referencia))
    ]
    return ativos


def avaliar_bairros(nivel_cm, taxa_cm_h, bairros, regua, relatos=None):
    """Monta a tabela de situação de todos os bairros para um nível e uma taxa."""
    linhas = []
    for bairro in bairros.itertuples():
        cota = regua["inundacao_cm"] + bairro.margem_cm
        alerta = regua["alerta_cm"] + bairro.margem_cm
        estado_nivel, horas = classificar_pelo_nivel(nivel_cm, taxa_cm_h, cota, alerta)

        relatos_bairro = (
            relatos[relatos["bairro"].str.casefold() == bairro.bairro.casefold()]
            if relatos is not None and not relatos.empty
            else pd.DataFrame(columns=["gravidade"])
        )
        estado_relatos = estado_minimo_pelos_relatos(relatos_bairro)
        estado = mais_grave(estado_nivel, estado_relatos)
        por_relatos = estado != estado_nivel

        linhas.append(
            {
                "bairro": bairro.bairro,
                "estado": estado,
                "cota_alagamento_cm": cota,
                "falta_cm": max(0.0, round(cota - nivel_cm, 1)),
                "horas_ate_alagar": None if math.isinf(horas) else round(horas, 1),
                "relatos_ativos": len(relatos_bairro),
                "motivo": "relatos dos moradores" if por_relatos else "nível medido",
                "acao": acao_recomendada(estado, por_relatos),
            }
        )

    tabela = pd.DataFrame(linhas)
    tabela["gravidade"] = tabela["estado"].map(ESTADOS.index)
    return tabela.sort_values(["gravidade", "falta_cm"], ascending=[False, True]).drop(columns="gravidade")

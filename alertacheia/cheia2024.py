"""Simulação da cheia de maio de 2024: o que o AlertaCheia teria avisado, e quando.

Roda as mesmas regras de decisão hora a hora sobre a série real do Guaíba e
mede, para cada bairro, quantas horas antes da água chegar o alerta teria saído.
"""

import pandas as pd

from . import config
from .decisao import ESTADOS, avaliar_bairros
from .tratamento import preparar_serie

REGUA = config.REGUAS["guaiba"]


def simular(serie_guaiba, bairros):
    """Devolve (tabela de antecedência por bairro, série horária preparada)."""
    serie = preparar_serie(serie_guaiba, frequencia="1h", janela_taxa=3)

    primeiro_aviso = {}  # primeira vez em ATENCAO ou pior
    primeiro_alerta = {}  # primeira vez em ALERTA ou pior
    agua_chegou = {}
    for momento, linha in serie.iterrows():
        situacao = avaliar_bairros(linha["nivel_suave_cm"], linha["taxa_cm_h"], bairros, REGUA)
        for registro in situacao.itertuples():
            if ESTADOS.index(registro.estado) >= ESTADOS.index("ATENCAO"):
                primeiro_aviso.setdefault(registro.bairro, momento)
            if ESTADOS.index(registro.estado) >= ESTADOS.index("ALERTA"):
                primeiro_alerta.setdefault(registro.bairro, momento)
            if registro.estado == "EVACUAR":
                agua_chegou.setdefault(registro.bairro, momento)

    def horas_entre(inicio, fim):
        if inicio is None or fim is None:
            return None
        return round((fim - inicio) / pd.Timedelta(hours=1), 1)

    linhas = []
    for bairro in bairros.itertuples():
        aviso = primeiro_aviso.get(bairro.bairro)
        alerta = primeiro_alerta.get(bairro.bairro)
        chegada = agua_chegou.get(bairro.bairro)
        linhas.append(
            {
                "bairro": bairro.bairro,
                "cota_alagamento_m": (REGUA["inundacao_cm"] + bairro.margem_cm) / 100,
                "primeiro_aviso": aviso,
                "primeiro_alerta": alerta,
                "agua_chegou": chegada,
                "antecedencia_aviso_h": horas_entre(aviso, chegada),
                "antecedencia_alerta_h": horas_entre(alerta, chegada),
            }
        )
    return pd.DataFrame(linhas), serie


def salvar_grafico(serie, antecedencia, caminho, inicio_medicao=None):
    """Gráfico do nível do Guaíba com a cota de cada bairro.

    inicio_medicao: quando começam os dados medidos pela ANA; antes disso a série
    foi reconstruída com os boletins da MetSul e aparece sombreada.
    """
    import matplotlib

    matplotlib.use("Agg")  # gera o arquivo sem abrir janela
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt

    figura, eixo = plt.subplots(figsize=(11, 6.5))
    if inicio_medicao is not None:
        eixo.axvspan(serie.index[0], inicio_medicao, color="#e5e7eb", alpha=0.7,
                     label="Subida reconstruída (boletins MetSul)")
    eixo.plot(serie.index, serie["nivel_cm"] / 100, color="#0e7490", linewidth=2, label="Nível do Guaíba (Cais Mauá)")
    eixo.axhline(REGUA["alerta_cm"] / 100, color="#92400e", linestyle="--", label="Cota de alerta (2,55 m)")
    eixo.axhline(REGUA["inundacao_cm"] / 100, color="#b91c1c", linestyle="--", label="Cota de inundação (3,00 m)")
    # Rótulos alternados entre a esquerda e a direita para não se sobreporem
    for posicao, linha in enumerate(antecedencia.sort_values("cota_alagamento_m").itertuples()):
        eixo.axhline(linha.cota_alagamento_m, color="#9ca3af", linewidth=0.8)
        na_direita = posicao % 2 == 1
        eixo.annotate(
            linha.bairro,
            (serie.index[-1] if na_direita else serie.index[0], linha.cota_alagamento_m),
            fontsize=8,
            color="#4b5563",
            ha="right" if na_direita else "left",
            xytext=(-4 if na_direita else 4, 2),
            textcoords="offset points",
        )
    eixo.set_title("Cheia de maio de 2024 e cota de alagamento de cada bairro")
    eixo.set_ylabel("Nível (m)")
    eixo.grid(alpha=0.3)
    eixo.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=4, fontsize=9, frameon=False)
    eixo.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    figura.autofmt_xdate()
    figura.tight_layout()
    figura.savefig(caminho, dpi=120)
    plt.close(figura)

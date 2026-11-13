"""Testes das regras de decisão e do cálculo da taxa de subida.

Rodar com: python -m unittest
"""

import math
import unittest

import pandas as pd

from alertacheia.decisao import (
    avaliar_bairros,
    classificar_pelo_nivel,
    estado_minimo_pelos_relatos,
    horas_ate_cota,
)
from alertacheia.tratamento import preparar_serie

REGUA = {"alerta_cm": 150, "inundacao_cm": 200}


class TestHorasAteCota(unittest.TestCase):
    def test_agua_ja_chegou(self):
        self.assertEqual(horas_ate_cota(210, 5, 200), 0)

    def test_nivel_parado_ou_descendo_nao_preve(self):
        self.assertTrue(math.isinf(horas_ate_cota(100, 0, 200)))
        self.assertTrue(math.isinf(horas_ate_cota(100, -3, 200)))
        self.assertTrue(math.isinf(horas_ate_cota(100, float("nan"), 200)))

    def test_previsao_pela_taxa(self):
        self.assertAlmostEqual(horas_ate_cota(150, 10, 200), 5)


class TestClassificacao(unittest.TestCase):
    def test_estados_pelo_nivel(self):
        self.assertEqual(classificar_pelo_nivel(205, 0, 200, 150)[0], "EVACUAR")
        self.assertEqual(classificar_pelo_nivel(170, 10, 200, 150)[0], "ALERTA")  # 3 h
        self.assertEqual(classificar_pelo_nivel(100, 5, 200, 150)[0], "ATENCAO")  # 20 h
        self.assertEqual(classificar_pelo_nivel(160, 0, 200, 150)[0], "ATENCAO")  # passou do alerta
        self.assertEqual(classificar_pelo_nivel(100, 0, 200, 150)[0], "NORMAL")


class TestRelatos(unittest.TestCase):
    def relatos(self, *gravidades):
        return pd.DataFrame({"gravidade": list(gravidades)})

    def test_um_relato_grave_nao_basta_para_evacuar(self):
        self.assertEqual(estado_minimo_pelos_relatos(self.relatos("alta")), "ALERTA")
        self.assertEqual(estado_minimo_pelos_relatos(self.relatos("alta", "alta")), "EVACUAR")
        self.assertEqual(estado_minimo_pelos_relatos(self.relatos("media")), "ATENCAO")
        self.assertEqual(estado_minimo_pelos_relatos(self.relatos("baixa")), "NORMAL")

    def test_relatos_sobem_o_estado_do_bairro(self):
        bairros = pd.DataFrame({"bairro": ["Sarandi", "Menino Deus"], "margem_cm": [0, 0]})
        relatos = pd.DataFrame({"bairro": ["sarandi"], "gravidade": ["alta"]})
        tabela = avaliar_bairros(100, 0, bairros, REGUA, relatos).set_index("bairro")
        self.assertEqual(tabela.loc["Sarandi", "estado"], "ALERTA")
        self.assertEqual(tabela.loc["Sarandi", "motivo"], "relatos dos moradores")
        self.assertEqual(tabela.loc["Menino Deus", "estado"], "NORMAL")


class TestTaxa(unittest.TestCase):
    def test_taxa_em_cm_por_hora(self):
        datas = pd.date_range("2024-05-01", periods=10, freq="1h")
        leituras = pd.DataFrame({"data": datas, "nivel_cm": [100 + 4 * i for i in range(10)]})
        serie = preparar_serie(leituras, frequencia="1h", janela_taxa=3, janela_media=1)
        self.assertAlmostEqual(serie["taxa_cm_h"].iloc[-1], 4)


if __name__ == "__main__":
    unittest.main()

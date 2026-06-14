import unittest
from sbc.parser import parse_kb
from sbc.engine import query, forward_chain, backward_chain
from sbc.models import Triple
from pathlib import Path

KB_PATH = Path("kb/automocion.kb")

# --- Tarea 1 data ---

SINTOMAS = {
    "coche_A": {"vibracion", "ruido_frenos"},
    "coche_B": {"humo_motor", "temperatura_alta"},
    "coche_C": {"perdida_potencia", "consumo_alto"},
    "coche_D": {"ruido_frenos", "temperatura_alta"},
    "coche_E": {"vibracion", "perdida_potencia"},
    "coche_F": {"consumo_alto", "humo_motor"},
}

INDICADORES = {
    "vibracion": {"fallo_rueda", "desalineacion_ruedas", "neumatico_desgastado"},
    "ruido_frenos": {"pastillas_gastadas", "disco_frenado_dañado", "liquido_frenos_bajo"},
    "humo_motor": {"fuga_aceite", "mezcla_rica_combustible", "desgaste_motor"},
    "temperatura_alta": {"fallo_refrigeracion", "bomba_agua_defectuosa", "termostato_atascado"},
    "perdida_potencia": {"filtro_aire_sucio", "turbo_defectuoso", "sensor_oxigeno_fallando"},
    "consumo_alto": {"inyectores_sucios", "mezcla_rica_combustible", "sensor_masa_aire_defectuoso"}
}

URGENCIAS_CRITICA = {"pastillas_gastadas", "fuga_aceite"}
URGENCIAS_ALTA = {
    "fallo_refrigeracion", "fallo_rueda", "turbo_defectuoso",
    "disco_frenado_dañado", "liquido_frenos_bajo",
    "desgaste_motor", "termostato_atascado", "bomba_agua_defectuosa"
}
URGENCIAS_MEDIA = {
    "filtro_aire_sucio", "inyectores_sucios", "mezcla_rica_combustible",
    "sensor_oxigeno_fallando", "sensor_masa_aire_defectuoso",
    "neumatico_desgastado", "desalineacion_ruedas"
}

URGENCIA_CRITICA_COCHES = {"coche_A", "coche_B", "coche_D", "coche_F"}
NO_URGENCIA_CRITICA_COCHES = {"coche_C", "coche_E"}

# --- Tarea 2 data ---

GASOLINA = {"mustang", "camaro", "supra", "rx7", "capuccino", "beat", "m3", "911"}
DIESEL = {"ram", "f150", "golf", "leon"}
HIBRIDO = {"prius"}
ELECTRICO = {"tesla"}

AMERICANO = {"mustang", "camaro", "ram", "f150", "tesla"}
JDM = {"supra", "rx7", "beat", "capuccino", "prius"}
EUROPEO = {"m3", "911", "golf", "leon"}

MUSCLE = {"mustang", "camaro"}
PICKUP = {"ram", "f150"}
AMERICANO_FAMILIAR = {"tesla"}
JDM_SPORT = {"supra", "rx7"}
KEI = {"beat", "capuccino"}
JAPONES_FAMILIAR = {"prius"}
EURO_SPORT = {"m3", "911"}
EUROPEO_FAMILIAR = {"golf", "leon"}

MARCAS = {
    "mustang": "ford", "camaro": "chevrolet", "ram": "dodge", "f150": "ford",
    "tesla": "tesla", "supra": "toyota", "rx7": "mazda", "beat": "honda",
    "capuccino": "suzuki", "prius": "toyota", "m3": "bmw", "911": "porsche",
    "golf": "volkswagen", "leon": "seat",
}

RIVALES = {
    "mustang": {"camaro"}, "camaro": {"mustang"},
    "supra": {"rx7"}, "rx7": {"supra"},
    "m3": {"911"}, "911": {"m3"},
    "ram": {"f150"}, "f150": {"ram"},
    "beat": {"capuccino"}, "capuccino": {"beat"},
    "golf": {"leon"}, "leon": {"golf"},
}

ALTERNATIVAS = {
    "mustang": {"camaro"}, "supra": {"rx7"}, "m3": {"911"},
    "golf": {"leon"}, "ram": {"f150"}, "beat": {"capuccino"},
    "prius": set(), "tesla": set(),
}

# --- helpers ---

def get_degree(kb, triple):
    for fact in kb.facts:
        if fact == triple:
            return fact.degree
    return None


# =====================
# Tarea 1
# =====================

class TestDiagnosticoHechos(unittest.TestCase):
    def test_sintomas_directos(self):
        kb = parse_kb(KB_PATH)
        for coche, sintomas in SINTOMAS.items():
            for sintoma in sintomas:
                with self.subTest(coche=coche, sintoma=sintoma):
                    results = query(kb, Triple(coche, "tiene_sintoma", sintoma))
                    self.assertEqual(len(results), 1)
                    self.assertGreater(results[0][1], 0.5)

    def test_indicadores(self):
        kb = parse_kb(KB_PATH)
        for sintoma, fallos in INDICADORES.items():
            for fallo in fallos:
                with self.subTest(sintoma=sintoma, fallo=fallo):
                    results = query(kb, Triple(sintoma, "indica", fallo))
                    self.assertEqual(len(results), 1)
                    self.assertGreater(results[0][1], 0.5)

    def test_urgencias_critica(self):
        kb = parse_kb(KB_PATH)
        for fallo in URGENCIAS_CRITICA:
            with self.subTest(fallo=fallo):
                results = query(kb, Triple(fallo, "tiene_urgencia", "critica"))
                self.assertEqual(len(results), 1)
                self.assertAlmostEqual(results[0][1], 1.0)

    def test_urgencias_alta(self):
        kb = parse_kb(KB_PATH)
        for fallo in URGENCIAS_ALTA:
            with self.subTest(fallo=fallo):
                results = query(kb, Triple(fallo, "tiene_urgencia", "alta"))
                self.assertEqual(len(results), 1)

    def test_urgencias_media(self):
        kb = parse_kb(KB_PATH)
        for fallo in URGENCIAS_MEDIA:
            with self.subTest(fallo=fallo):
                results = query(kb, Triple(fallo, "tiene_urgencia", "media"))
                self.assertEqual(len(results), 1)


class TestDiagnosticoDerivados(unittest.TestCase):
    def test_fallos_derivados_exist(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)
        for coche, sintomas in SINTOMAS.items():
            for sintoma in sintomas:
                for fallo in INDICADORES[sintoma]:
                    with self.subTest(coche=coche, fallo=fallo):
                        self.assertIn(Triple(coche, "tiene_fallo", fallo), kb.facts)

    def test_fallos_derivados_degree(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)
        for coche, sintomas in SINTOMAS.items():
            for sintoma in sintomas:
                for fallo in INDICADORES[sintoma]:
                    with self.subTest(coche=coche, fallo=fallo):
                        d = get_degree(kb, Triple(coche, "tiene_fallo", fallo))
                        self.assertIsNotNone(d)
                        self.assertGreater(d, 0.4)
                        self.assertLessEqual(d, 1.0)

    def test_urgencia_critica_coches(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)
        for coche in URGENCIA_CRITICA_COCHES:
            with self.subTest(coche=coche):
                self.assertIn(Triple(coche, "necesita_atencion_urgente", "critica"), kb.facts)

    def test_no_urgencia_critica_coches(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)
        for coche in NO_URGENCIA_CRITICA_COCHES:
            with self.subTest(coche=coche):
                self.assertNotIn(Triple(coche, "necesita_atencion_urgente", "critica"), kb.facts)

    def test_es_fallo_probable_alta_urgencia(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)
        # every fault with urgencia alta that a coche has should appear as es_fallo_probable
        for coche, sintomas in SINTOMAS.items():
            for sintoma in sintomas:
                for fallo in INDICADORES[sintoma]:
                    if fallo in URGENCIAS_ALTA:
                        with self.subTest(coche=coche, fallo=fallo):
                            self.assertIn(Triple(coche, "es_fallo_probable", fallo), kb.facts)


# =====================
# Tarea 2
# =====================

class TestClasificacionHechos(unittest.TestCase):
    def test_marcas(self):
        kb = parse_kb(KB_PATH)
        for coche, marca in MARCAS.items():
            with self.subTest(coche=coche):
                self.assertEqual(len(query(kb, Triple(coche, "es_marca", marca))), 1)

    def test_origen_americano(self):
        kb = parse_kb(KB_PATH)
        for coche in AMERICANO:
            with self.subTest(coche=coche):
                self.assertEqual(len(query(kb, Triple(coche, "es_origen", "americano"))), 1)

    def test_origen_jdm(self):
        kb = parse_kb(KB_PATH)
        for coche in JDM:
            with self.subTest(coche=coche):
                self.assertEqual(len(query(kb, Triple(coche, "es_origen", "jdm"))), 1)

    def test_origen_europeo(self):
        kb = parse_kb(KB_PATH)
        for coche in EUROPEO:
            with self.subTest(coche=coche):
                self.assertEqual(len(query(kb, Triple(coche, "es_origen", "europeo"))), 1)

    def test_estilo_muscle(self):
        kb = parse_kb(KB_PATH)
        for coche in MUSCLE:
            with self.subTest(coche=coche):
                results = query(kb, Triple(coche, "es_estilo", "muscle"))
                self.assertEqual(len(results), 1)
                self.assertGreaterEqual(results[0][1], 0.9)

    def test_estilo_pickup(self):
        kb = parse_kb(KB_PATH)
        for coche in PICKUP:
            with self.subTest(coche=coche):
                results = query(kb, Triple(coche, "es_estilo", "pickup"))
                self.assertEqual(len(results), 1)
                self.assertGreaterEqual(results[0][1], 0.9)

    def test_estilo_sport(self):
        kb = parse_kb(KB_PATH)
        for coche in JDM_SPORT | EURO_SPORT:
            with self.subTest(coche=coche):
                self.assertEqual(len(query(kb, Triple(coche, "es_estilo", "sport"))), 1)

    def test_estilo_kei(self):
        kb = parse_kb(KB_PATH)
        for coche in KEI:
            with self.subTest(coche=coche):
                self.assertEqual(len(query(kb, Triple(coche, "es_estilo", "kei"))), 1)

    def test_estilo_familiar(self):
        kb = parse_kb(KB_PATH)
        for coche in AMERICANO_FAMILIAR | JAPONES_FAMILIAR | EUROPEO_FAMILIAR:
            with self.subTest(coche=coche):
                self.assertEqual(len(query(kb, Triple(coche, "es_estilo", "familiar"))), 1)


class TestClasificacionDerivados(unittest.TestCase):
    def _check_tipo(self, kb, coches, tipo, min_degree=0.85):
        for coche in coches:
            with self.subTest(coche=coche, tipo=tipo):
                self.assertIn(Triple(coche, "es_tipo", tipo), kb.facts)
                d = get_degree(kb, Triple(coche, "es_tipo", tipo))
                self.assertGreaterEqual(d, min_degree)

    def test_muscle_cars(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)
        self._check_tipo(kb, MUSCLE, "muscle_car")

    def test_jdm_sport(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)
        self._check_tipo(kb, JDM_SPORT, "jdm_sport")

    def test_euro_sport(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)
        self._check_tipo(kb, EURO_SPORT, "euro_sport")

    def test_europeo_familiar(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)
        self._check_tipo(kb, EUROPEO_FAMILIAR, "europeo_familiar")

    def test_pickup_trucks(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)
        self._check_tipo(kb, PICKUP, "pickup_truck")

    def test_kei_cars(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)
        self._check_tipo(kb, KEI, "kei_car")

    def test_japones_familiar(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)
        self._check_tipo(kb, JAPONES_FAMILIAR, "japones_familiar")

    def test_americano_familiar(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)
        self._check_tipo(kb, AMERICANO_FAMILIAR, "americano_familiar")

    def test_no_cross_clasificacion(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)
        groups = {
            "muscle_car": MUSCLE, "pickup_truck": PICKUP,
            "americano_familiar": AMERICANO_FAMILIAR, "jdm_sport": JDM_SPORT,
            "kei_car": KEI, "japones_familiar": JAPONES_FAMILIAR,
            "euro_sport": EURO_SPORT, "europeo_familiar": EUROPEO_FAMILIAR,
        }
        all_types = set(groups.keys())
        for tipo, coches in groups.items():
            for coche in coches:
                for otro_tipo in all_types - {tipo}:
                    with self.subTest(coche=coche, otro_tipo=otro_tipo):
                        self.assertNotIn(Triple(coche, "es_tipo", otro_tipo), kb.facts)


# =====================
# Tarea 3
# =====================

class TestCombustibleHechos(unittest.TestCase):
    def test_gasolina_coches(self):
        kb = parse_kb(KB_PATH)
        for coche in GASOLINA:
            with self.subTest(coche=coche):
                self.assertEqual(len(query(kb, Triple(coche, "usa_combustible", "gasolina"))), 1)

    def test_diesel_coches(self):
        kb = parse_kb(KB_PATH)
        for coche in DIESEL:
            with self.subTest(coche=coche):
                self.assertEqual(len(query(kb, Triple(coche, "usa_combustible", "diesel"))), 1)

    def test_hibrido_coches(self):
        kb = parse_kb(KB_PATH)
        for coche in HIBRIDO:
            with self.subTest(coche=coche):
                self.assertEqual(len(query(kb, Triple(coche, "usa_combustible", "hibrido"))), 1)

    def test_electrico_coches(self):
        kb = parse_kb(KB_PATH)
        for coche in ELECTRICO:
            with self.subTest(coche=coche):
                self.assertEqual(len(query(kb, Triple(coche, "usa_combustible", "electrico"))), 1)

    def test_tipos_combustible(self):
        kb = parse_kb(KB_PATH)
        casos = [
            ("gasolina", "combustible_fosil"),
            ("diesel", "combustible_fosil"),
            ("hibrido", "combustible_mixto"),
            ("electrico", "combustible_limpio"),
        ]
        for comb, tipo in casos:
            with self.subTest(comb=comb, tipo=tipo):
                self.assertEqual(len(query(kb, Triple(comb, "es_clase", tipo))), 1)

    def test_emisiones_tipos(self):
        kb = parse_kb(KB_PATH)
        casos = [
            ("combustible_fosil", "alta", 0.8),
            ("combustible_mixto", "media", 0.8),
            ("combustible_limpio", "nula", 0.9),
        ]
        for comb, emision, min_d in casos:
            with self.subTest(comb=comb, emision=emision):
                results = query(kb, Triple(comb, "tiene_emision", emision))
                self.assertEqual(len(results), 1)
                self.assertGreater(results[0][1], min_d)


class TestCombustibleDerivados(unittest.TestCase):
    def test_emision_alta_fosil(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)

        for coche in GASOLINA | DIESEL:
            with self.subTest(coche=coche):
                self.assertIn(
                    Triple(coche, "tiene_emision", "alta"),
                    kb.facts
                )

    def test_no_emision_alta_limpios(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)

        for coche in ELECTRICO | HIBRIDO:
            with self.subTest(coche=coche):
                self.assertNotIn(
                    Triple(coche, "tiene_emision", "alta"),
                    kb.facts
                )

    def test_eficientes_ciudad(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)

        for coche in ELECTRICO | HIBRIDO:
            with self.subTest(coche=coche):
                self.assertIn(
                    Triple(coche, "es_eficiente_en", "ciudad"),
                    kb.facts
                )

    def test_gasolina_no_eficiente_ciudad(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)

        for coche in GASOLINA:
            with self.subTest(coche=coche):
                self.assertNotIn(
                    Triple(coche, "es_eficiente_en", "ciudad"),
                    kb.facts
                )

    def test_gasolina_no_eficiente_ciudad(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)

        for coche in GASOLINA:
            with self.subTest(coche=coche):
                self.assertNotIn(
                    Triple(coche, "es_eficiente_en", "ciudad"),
                    kb.facts
                )

    def test_recomendado_viaje_largo(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)

        for coche in DIESEL | HIBRIDO:
            with self.subTest(coche=coche):
                self.assertIn(
                    Triple(coche, "es_recomendado_para", "viaje_largo"),
                    kb.facts
                )

    def test_recomendado_ciudad(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)

        for coche in ELECTRICO | HIBRIDO:
            with self.subTest(coche=coche):
                self.assertIn(
                    Triple(coche, "es_recomendado_para", "ciudad"),
                    kb.facts
                )


class TestRestriccionesDerivados(unittest.TestCase):
    def test_rivales_exist(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)
        for coche, rivales in RIVALES.items():
            for rival in rivales:
                with self.subTest(coche=coche, rival=rival):
                    self.assertIn(Triple(coche, "es_rival_de", rival), kb.facts)

    def test_no_autorivales(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)
        todos = MUSCLE | PICKUP | AMERICANO_FAMILIAR | JDM_SPORT | KEI | JAPONES_FAMILIAR | EURO_SPORT | EUROPEO_FAMILIAR
        for coche in todos:
            with self.subTest(coche=coche):
                self.assertNotIn(Triple(coche, "es_rival_de", coche), kb.facts)

    def test_alternativas_exist(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)
        for coche, alts in ALTERNATIVAS.items():
            for alt in alts:
                with self.subTest(coche=coche, alt=alt):
                    self.assertIn(Triple(coche, "es_alternativa_a", alt), kb.facts)

    def test_no_autoalternativas(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)
        todos = MUSCLE | PICKUP | AMERICANO_FAMILIAR | JDM_SPORT | KEI | JAPONES_FAMILIAR | EURO_SPORT | EUROPEO_FAMILIAR
        for coche in todos:
            with self.subTest(coche=coche):
                self.assertNotIn(Triple(coche, "es_alternativa_a", coche), kb.facts)

    def test_rival_degree(self):
        kb = parse_kb(KB_PATH)
        forward_chain(kb)
        for coche, rivales in RIVALES.items():
            for rival in rivales:
                with self.subTest(coche=coche, rival=rival):
                    d = get_degree(kb, Triple(coche, "es_rival_de", rival))
                    self.assertIsNotNone(d)
                    self.assertGreater(d, 0.5)


if __name__ == "__main__":
    unittest.main()
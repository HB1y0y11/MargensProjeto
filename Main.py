from kivy.config import Config
#oi
Config.set("graphics", "width", "360")
Config.set("graphics", "height", "740")
Config.set("graphics", "resizable", False)

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from datetime import datetime
from kivymd.uix.menu import MDDropdownMenu

import firebase_admin
from firebase_admin import credentials, db

MESES = [
    "jan", "fev", "mar", "abr",
    "mai", "jun", "jul", "ago",
    "set", "out", "nov", "dez"
]

ESCALA_GRAFICO = 160 / 300

cred = credentials.Certificate("firebase_key.json")

firebase_admin.initialize_app(cred, {
    "databaseURL": "https://margens-13760-default-rtdb.firebaseio.com/"
})

class Gerenciador(ScreenManager):
    pass

class Historico(Screen):

    modo = StringProperty("diario")

    dia_texto = StringProperty("")
    mes_texto = StringProperty("")
    ano_texto = StringProperty("")

    unidade = StringProperty("kw / dia")

    consumo = NumericProperty(0)
    porcentagem = NumericProperty(0)

    dia = NumericProperty(1)
    mes = NumericProperty(1)
    ano = NumericProperty(2025)

    barra1 = NumericProperty(0)
    barra2 = NumericProperty(0)
    barra3 = NumericProperty(0)
    barra4 = NumericProperty(0)
    barra5 = NumericProperty(0)
    barra6 = NumericProperty(0)
    barra7 = NumericProperty(0)
    barra8 = NumericProperty(0)
    barra9 = NumericProperty(0)
    barra10 = NumericProperty(0)
    barra11 = NumericProperty(0)
    barra12 = NumericProperty(0)

    def on_pre_enter(self):

        hoje = datetime.now()

        self.dia = hoje.day
        self.mes = hoje.month
        self.ano = hoje.year

        self.carregar_diario()

    # -------------------------
    # TEXTOS
    # -------------------------

    def atualizar_textos(self):

        self.dia_texto = f"{self.dia} {MESES[self.mes - 1]}"
        self.mes_texto = MESES[self.mes - 1]
        self.ano_texto = str(self.ano)

    # -------------------------
    # GRAFICO
    # -------------------------

    def definir_barras(self, valores):

        # completa até 12 barras
        while len(valores) < 12:
            valores.append(0)

        barras = [v * ESCALA_GRAFICO for v in valores]

        self.barra1 = barras[0]
        self.barra2 = barras[1]
        self.barra3 = barras[2]
        self.barra4 = barras[3]
        self.barra5 = barras[4]
        self.barra6 = barras[5]
        self.barra7 = barras[6]
        self.barra8 = barras[7]
        self.barra9 = barras[8]
        self.barra10 = barras[9]
        self.barra11 = barras[10]
        self.barra12 = barras[11]

    # -------------------------
    # MODOS
    # -------------------------

    def carregar_diario(self):

        self.modo = "diario"

        self.unidade = "kw / dia"

        try:

            ref = db.reference("/consumo/hoje")

            dados = ref.get()

            self.consumo = dados["total"]

            self.porcentagem = min(self.consumo / 500, 1)

            # HORÁRIOS (MESMOS DO HOME)
            valores = [
                dados["00h"],
                dados["04h"],
                dados["08h"],
                dados["12h"],
                dados["16h"],
                dados["20h"],
                0
            ]

            self.definir_barras(valores)

        except Exception as e:
            print(e)

        self.atualizar_textos()

    def carregar_mensal(self):

        self.modo = "mensal"

        self.unidade = "kw / mês"

        self.consumo = 180

        self.porcentagem = min(self.consumo / 500, 1)

        # SEMANA
        valores = [140, 175, 160, 100, 170, 320, 350]

        self.definir_barras(valores)

        self.atualizar_textos()

    def carregar_anual(self):

        self.modo = "anual"

        self.unidade = "kw / ano"

        self.consumo = 320

        self.porcentagem = min(self.consumo / 500, 1)

        # MESES
        valores = [
            220, 180, 250, 200,
            170, 210, 190, 230,
            240, 180, 260, 200
        ]

        self.definir_barras(valores)

        self.atualizar_textos()

    # -------------------------
    # MENUS
    # -------------------------

    def abrir_menu_data(self, botao):

        itens = []

        if self.modo == "diario":

            for i in range(1, 32):

                itens.append({
                    "text": str(i),
                    "on_release": lambda x=i: self.selecionar_dia(x)
                })

        elif self.modo == "mensal":

            for i, mes in enumerate(MESES):

                itens.append({
                    "text": mes,
                    "on_release": lambda x=i + 1: self.selecionar_mes(x)
                })

        else:

            for ano in range(2026, 1899, -1):

                itens.append({
                    "text": str(ano),
                    "on_release": lambda x=ano: self.selecionar_ano(x)
                })

        self.menu = MDDropdownMenu(
            caller=botao,
            items=itens,
            width_mult=3
        )

        self.menu.open()

    # -------------------------
    # SELEÇÃO
    # -------------------------

    def selecionar_dia(self, dia):

        self.dia = dia

        self.atualizar_textos()

        self.menu.dismiss()

    def selecionar_mes(self, mes):

        self.mes = mes

        self.atualizar_textos()

        self.menu.dismiss()

    def selecionar_ano(self, ano):

        self.ano = ano

        self.atualizar_textos()

        self.menu.dismiss()

class Aparelhos(Screen):
    status_geladeira = StringProperty("Desligado")
    watts_geladeira = NumericProperty(0)
    porcentagem_geladeira = NumericProperty(0)

    status_ventilador = StringProperty("Desligado")
    watts_ventilador = NumericProperty(0)
    porcentagem_ventilador = NumericProperty(0)

    def carregar_dados(self):

        try:

            ref = db.reference("/aparelhos")

            dados = ref.get()

            geladeira = dados["geladeira"]

            self.status_geladeira = geladeira["status"]
            self.watts_geladeira = geladeira["watts"]
            self.porcentagem_geladeira = geladeira["watts"] / 200

            ventilador = dados["ventilador"]

            self.status_ventilador = ventilador["status"]
            self.watts_ventilador = ventilador["watts"]
            self.porcentagem_ventilador = ventilador["watts"] / 200

        except Exception as e:
            print(e)

class Geladeira(Screen):
    kw_dia = NumericProperty(0)

    porcentagem = NumericProperty(0)
    data_atual = StringProperty("")

    dia1 = NumericProperty(0)
    dia2 = NumericProperty(0)
    dia3 = NumericProperty(0)
    dia4 = NumericProperty(0)
    dia5 = NumericProperty(0)
    dia6 = NumericProperty(0)
    dia7 = NumericProperty(0)

    def carregar_dados(self):

        hoje = datetime.now()

        MESES

        self.data_atual = f"{hoje.day} {MESES[hoje.month - 1]}"

        try:

            ref = db.reference("/aparelhos/geladeira")

            dados = ref.get()

            # CONSUMO PRINCIPAL
            self.kw_dia = dados["kw_dia"]

            self.porcentagem = min(self.kw_dia / 500, 1)

            # GRAFICO
            semana = dados["semana"]

            self.dia1 = semana["dom"] * ESCALA_GRAFICO
            self.dia2 = semana["seg"] * ESCALA_GRAFICO
            self.dia3 = semana["ter"] * ESCALA_GRAFICO
            self.dia4 = semana["qua"] * ESCALA_GRAFICO
            self.dia5 = semana["qui"] * ESCALA_GRAFICO
            self.dia6 = semana["sex"] * ESCALA_GRAFICO
            self.dia7 = semana["sab"] * ESCALA_GRAFICO

        except Exception as e:
            print(e)

class Ventilador(Screen):
    pass

class Home(Screen):

    porcentagem = NumericProperty(0.0)

    nivel = StringProperty("Baixo")

    def carregar_dados(self):

        try:

            ref = db.reference("/consumo/hoje")

            dados = ref.get()

            total = dados["total"]

            self.ids.gauge_label.text = f"{total} kw/h"

            # porcentagem do circulo
            self.porcentagem = total / 300

            # texto baixo/medio/alto
            if total < 100:
                self.nivel = "Baixo"

            elif total < 200:
                self.nivel = "Médio"

            else:
                self.nivel = "Alto"

            # barras
            self.ids.barra1.size_hint_y = dados["00h"] / 200
            self.ids.barra2.size_hint_y = dados["04h"] / 200
            self.ids.barra3.size_hint_y = dados["08h"] / 200
            self.ids.barra4.size_hint_y = dados["12h"] / 200
            self.ids.barra5.size_hint_y = dados["16h"] / 200
            self.ids.barra6.size_hint_y = dados["20h"] / 200

        except Exception as e:
            print(e)

class Main(MDApp):

    def build(self):

        self.theme_cls.theme_style = "Light"

        gerenciador = Gerenciador()

        Clock.schedule_once(
            lambda dt: gerenciador.get_screen("home").carregar_dados(),
            1
        )
        Clock.schedule_once(
            lambda dt: gerenciador.get_screen("aparelhos").carregar_dados(),
            1
        )
        Clock.schedule_once(
            lambda dt: gerenciador.get_screen("geladeira").carregar_dados(),
            1
        )

        return gerenciador


Main().run()
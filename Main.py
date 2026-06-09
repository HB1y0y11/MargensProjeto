from kivy.config import Config

Config.set("graphics", "width", "360")
Config.set("graphics", "height", "740")
Config.set("graphics", "resizable", False)

from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty
from datetime import datetime
from kivymd.uix.boxlayout import MDBoxLayout
import firebase_admin
from firebase_admin import credentials, db
import os

MESES = [
    "jan", "fev", "mar", "abr",
    "mai", "jun", "jul", "ago",
    "set", "out", "nov", "dez"
]

ESCALA_GRAFICO = 160 / 300
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
firebase_path = os.path.join(BASE_DIR, "firebase_key.json")

# Inicialização segura do Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_path)
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://margens-13760-default-rtdb.firebaseio.com/"
    })

class TelaPrincipal(MDBoxLayout):
    pass

class Gerenciador(ScreenManager):
    pass

# ============================================================
# CLASSES DAS TELAS RECALIBRADAS COM AS PROPRIEDADES ANTIGAS
# ============================================================

class Home(Screen):
    porcentagem = NumericProperty(0)
    nivel = StringProperty("Baixo")

    def carregar_dados(self):
        try:
            ref = db.reference("/consumo/hoje")
            dados = ref.get()
            if not dados:
                return

            total = dados.get("total", 0)
            if 'gauge_label' in self.ids:
                self.ids.gauge_label.text = f"{total} kw/h"
            self.porcentagem = total / 300

            if total < 100:
                self.nivel = "Baixo"
            elif total < 200:
                self.nivel = "Médio"
            else:
                self.nivel = "Alto"

            # Atualização segura das barras gráficas
            barras_horarios = ["barra_00h", "barra_04h", "barra_08h", "barra_12h", "barra_16h", "barra_20h"]
            chaves_firebase = ["00h", "04h", "08h", "12h", "16h", "20h"]
            for id_barra, chave in zip(barras_horarios, chaves_firebase):
                if id_barra in self.ids:
                    valor_firebase = dados.get(chave, 0)
                    self.ids[id_barra].size_hint_y = valor_firebase / 200
                    
        except Exception as e:
            print(f"Erro na Home ao carregar Firebase: {e}")

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
    porcentagem = NumericProperty(0)
    kw_dia = StringProperty("0.0")
    data_atual = StringProperty("--/--")
    
    dia1 = NumericProperty(0)
    dia2 = NumericProperty(0)
    dia3 = NumericProperty(0)
    dia4 = NumericProperty(0)
    dia5 = NumericProperty(0)
    dia6 = NumericProperty(0)
    dia7 = NumericProperty(0)

    def carregar_dados(self):
        try:
            hoje = datetime.now()
            self.data_atual = f"{hoje.day} {MESES[hoje.month - 1]}"

            ref = db.reference("/aparelhos/geladeira")
            dados = ref.get()
            
            if dados:
                # Carrega o consumo de kW/dia
                consumo = dados.get('kw_dia', 0)
                self.kw_dia = str(consumo)
                
                # Sincroniza o gráfico em pizza/arco central (0.0 a 1.0)
                self.porcentagem = min(1.0, float(consumo) / 300.0) if consumo else 0.0
                
                if 'data' in dados:
                    self.data_atual = dados.get('data')

                # CALIBRADORES MULTIPLICADORES DA ALTURA DA BARRA (0.0 a 1.0)
                # Como a linha de base 0 está suspensa no KV, o valor máximo real visível é 0.8
                VALOR_MAXIMO = 360.0
                FATOR_ESC = 0.80
                
                semana = dados.get('semana')
                if not isinstance(semana, dict):
                    semana = {}
                
                self.dia1 = (float(semana.get('dom', 0)) / VALOR_MAXIMO) * FATOR_ESC
                self.dia2 = (float(semana.get('seg', 0)) / VALOR_MAXIMO) * FATOR_ESC
                self.dia3 = (float(semana.get('ter', 0)) / VALOR_MAXIMO) * FATOR_ESC
                self.dia4 = (float(semana.get('qua', 0)) / VALOR_MAXIMO) * FATOR_ESC
                self.dia5 = (float(semana.get('qui', 0)) / VALOR_MAXIMO) * FATOR_ESC
                self.dia6 = (float(semana.get('sex', 0)) / VALOR_MAXIMO) * FATOR_ESC
                self.dia7 = (float(semana.get('sab', 0)) / VALOR_MAXIMO) * FATOR_ESC
                
        except Exception as e:
            print(f"Erro ao carregar dados reais da Geladeira: {e}")

class Ventilador(Screen):
    pass

class Ideias(Screen):
    pass

# ============================================================
# CLASSE PRINCIPAL DA APLICAÇÃO
# ============================================================
class Main(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        
        # Carrega a árvore visual completa do arquivo .kv
        root_widget = Builder.load_file(os.path.join(BASE_DIR, "interface.kv"))
        
        # Agenda o carregamento inicial seguro dos dados assim que a árvore de IDs estiver construída
        Clock.schedule_interval(self.tentar_carregar_inicial, 0.5)
        return root_widget

    def tentar_carregar_inicial(self, dt):
        try:
            gerenciador = self.root.ids.screen_manager
            home_screen = gerenciador.get_screen("home")
            
            # Quando a árvore gráfica estiver linkada, dispara as requisições de dados
            if 'gauge_label' in home_screen.ids:
                home_screen.carregar_dados()
                gerenciador.get_screen("aparelhos").carregar_dados()
                gerenciador.get_screen("geladeira").carregar_dados()
                return False  # Cancela o intervalo do relógio com sucesso
        except Exception:
            pass
        return True

if __name__ == "__main__":
    Main().run()
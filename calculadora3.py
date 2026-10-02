import math
import sys
import customtkinter as ctk
from tkinter import messagebox

# Configuración inicial de CustomTkinter
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

BLUE_DARK = "#1a237e"
BLUE_MED = "#283593"
BLUE_LIGHT = "#3949ab"
BLUE_ACCENT = "#5c6bc0"
BLUE_PALE = "#e8eaf6"
WHITE = "#ffffff"
GRAY_LIGHT = "#f5f5f5"
GRAY_BORDER = "#d0d3d8"
RED = "#c62828"
RED_HOVER = "#e53935"

MAX_HISTORIAL = 5
SIMBOLOS = {"+": "+", "-": "-", "*": "×", "/": "÷"}


class Calculadora(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Calculadora")
        self.resizable(False, False)
        self.configure(fg_color=GRAY_LIGHT)

        self._operacion = None
        self._operandos = []
        self._nuevo_numero = False
        self._error_activo = False
        self._historial = []

        self.pantalla_var = ctk.StringVar(value="0")
        self.operacion_var = ctk.StringVar(value="")

        self._construir_interfaz()
        self._refrescar_historial()

    # ------------------------------------------------------------------ UI

    def _construir_interfaz(self):
        contenedor = ctk.CTkFrame(self, fg_color=GRAY_LIGHT, corner_radius=0)
        contenedor.pack(fill="both", expand=True, padx=20, pady=16)

        # Header
        header = ctk.CTkLabel(
            contenedor,
            text="Calculadora Básica",
            fg_color=BLUE_DARK,
            text_color=WHITE,
            font=("Segoe UI", 16, "bold"),
            corner_radius=8,
            pady=12,
        )
        header.pack(fill="x")

        # Pantalla principal
        pantalla = ctk.CTkLabel(
            contenedor,
            textvariable=self.pantalla_var,
            fg_color=WHITE,
            text_color=BLUE_DARK,
            font=("Consolas", 24, "bold"),
            anchor="e",
            corner_radius=8,
            border_width=2,
            border_color=BLUE_ACCENT,
            padx=15,
            pady=12,
        )
        pantalla.pack(fill="x", pady=(12, 0))
        self.pantalla = pantalla

        # Subtítulo de operación en curso
        ctk.CTkLabel(
            contenedor,
            textvariable=self.operacion_var,
            fg_color=GRAY_LIGHT,
            text_color=BLUE_DARK,
            font=("Segoe UI", 11),
            anchor="e",
        ).pack(fill="x", pady=(4, 0))

        self._construir_teclado(contenedor)
        self._construir_historial(contenedor)

        # Footer
        ctk.CTkLabel(
            contenedor,
            text="Realizado por Javier Sanguino - 2026",
            fg_color=BLUE_PALE,
            text_color=BLUE_DARK,
            font=("Segoe UI", 9),
            corner_radius=6,
            pady=6,
        ).pack(fill="x", pady=(14, 0))

        self.bind("<Key>", self._tecla_pulsada)
        self.focus_force()

    def _construir_teclado(self, padre):
        marco = ctk.CTkFrame(padre, fg_color=GRAY_LIGHT, corner_radius=0)
        marco.pack(pady=(10, 0))

        botones = [
            ("7", 0, 0), ("8", 0, 1), ("9", 0, 2), ("/", 0, 3),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2), ("*", 1, 3),
            ("1", 2, 0), ("2", 2, 1), ("3", 2, 2), ("-", 2, 3),
            ("0", 3, 0), (".", 3, 1), ("C", 3, 2), ("+", 3, 3),
        ]

        for texto, fila, col in botones:
            if texto in SIMBOLOS:
                bg, hover, fg = BLUE_MED, BLUE_DARK, WHITE
                comando = lambda t=texto: self._operador(t)
            elif texto == "C":
                bg, hover, fg = RED, RED_HOVER, WHITE
                comando = self._limpiar
            else:
                bg, hover, fg = BLUE_PALE, BLUE_ACCENT, BLUE_DARK
                comando = lambda t=texto: self._digito(t)

            btn = ctk.CTkButton(
                marco,
                text=texto,
                command=comando,
                width=55,
                height=45,
                font=("Segoe UI", 16, "bold"),
                fg_color=bg,
                hover_color=hover,
                text_color=fg,
                corner_radius=8,
                cursor="hand2",
            )
            btn.grid(row=fila, column=col, padx=3, pady=3)

        btn_igual = ctk.CTkButton(
            marco,
            text="=",
            command=self._igual,
            height=45,
            font=("Segoe UI", 18, "bold"),
            fg_color=BLUE_ACCENT,
            hover_color=BLUE_LIGHT,
            text_color=WHITE,
            corner_radius=8,
            cursor="hand2",
        )
        btn_igual.grid(row=4, column=0, columnspan=4, sticky="ew", padx=3, pady=(3, 0))
        marco.grid_columnconfigure(0, weight=1)

    def _construir_historial(self, padre):
        marco = ctk.CTkFrame(
            padre,
            fg_color=WHITE,
            border_color=GRAY_BORDER,
            border_width=1,
            corner_radius=8,
        )
        marco.pack(fill="x", pady=(14, 0))

        # Contenedor interno para los márgenes del historial
        contenido_historial = ctk.CTkFrame(marco, fg_color=WHITE, corner_radius=0)
        contenido_historial.pack(fill="x", padx=10, pady=8)

        ctk.CTkLabel(
            contenido_historial,
            text=f"Historial (últimas {MAX_HISTORIAL} operaciones)",
            fg_color=WHITE,
            text_color=BLUE_MED,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(fill="x")

        self.marco_historial = ctk.CTkFrame(contenido_historial, fg_color=WHITE, corner_radius=0)
        self.marco_historial.pack(fill="x", pady=(6, 0))

        btn_limpiar = ctk.CTkButton(
            contenido_historial,
            text="Limpiar historial",
            command=self._limpiar_historial,
            font=("Segoe UI", 9),
            fg_color=BLUE_PALE,
            hover_color=BLUE_ACCENT,
            text_color=BLUE_DARK,
            corner_radius=6,
            height=24,
            cursor="hand2",
        )
        btn_limpiar.pack(anchor="e", pady=(6, 0))

    # ----------------------------------------------------------- historial

    def _registrar_historial(self, a, b, op, resultado):
        self._historial.insert(0, (a, b, op, resultado))
        del self._historial[MAX_HISTORIAL:]
        self._refrescar_historial()

    def _refrescar_historial(self):
        for widget in self.marco_historial.winfo_children():
            widget.destroy()

        if not self._historial:
            ctk.CTkLabel(
                self.marco_historial,
                text="Sin operaciones",
                fg_color=WHITE,
                text_color="#9e9e9e",
                font=("Segoe UI", 9, "italic"),
                anchor="w",
            ).pack(fill="x")
            return

        for indice, (a, b, op, resultado) in enumerate(self._historial, start=1):
            fila = ctk.CTkFrame(self.marco_historial, fg_color=WHITE, corner_radius=0)
            fila.pack(fill="x", pady=1)

            ctk.CTkLabel(
                fila,
                text=f"{indice}.",
                fg_color=WHITE,
                text_color="#9e9e9e",
                font=("Segoe UI", 9),
                width=20,
                anchor="w",
            ).pack(side="left")

            ctk.CTkLabel(
                fila,
                text=f"{self._formatear(a)} {SIMBOLOS[op]} {self._formatear(b)}",
                fg_color=WHITE,
                text_color=BLUE_MED,
                font=("Consolas", 10),
                anchor="w",
            ).pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(
                fila,
                text=f"= {self._formatear(resultado)}",
                fg_color=WHITE,
                text_color=BLUE_DARK,
                font=("Consolas", 10, "bold"),
                anchor="e",
            ).pack(side="right")

    def _limpiar_historial(self):
        self._historial = []
        self._refrescar_historial()

    # ------------------------------------------------------------- lógica

    def _digito(self, texto):
        if self._error_activo:
            self._reiniciar()

        actual = self.pantalla_var.get()
        if self._nuevo_numero:
            actual = "0"
            self._nuevo_numero = False

        if texto == ".":
            if "." in actual:
                return
            if actual in ("0", "-0"):
                self._cambiar_texto("0.")
            else:
                self._cambiar_texto(actual + ".")
            return

        if actual in ("0", "-0"):
            self._cambiar_texto(texto)
        else:
            self._cambiar_texto(actual + texto)

    def _operador(self, op):
        if self._error_activo:
            self._reiniciar()

        valor = self._leer_pantalla()
        if valor is None:
            return

        if self._operacion is not None and not self._nuevo_numero:
            resultado = self._calcular(self._operandos[0], valor, self._operacion)
            if resultado is None:
                return
            self._registrar_historial(
                self._operandos[0], valor, self._operacion, resultado
            )
            self._operandos = [resultado]
            self._cambiar_texto(self._formatear(resultado))
        else:
            self._operandos = [valor]

        self._operacion = op
        self._nuevo_numero = True
        self.operacion_var.set(f"{self._formatear(self._operandos[0])} {SIMBOLOS[op]}")
        self.focus_set()

    def _igual(self):
        if self._operacion is None or len(self._operandos) < 1:
            return

        valor = self._leer_pantalla()
        if valor is None:
            return

        a, b, op = self._operandos[0], valor, self._operacion
        resultado = self._calcular(a, b, op)

        self._operacion = None
        self._operandos = []
        self._nuevo_numero = True
        self.operacion_var.set("")

        if resultado is None:
            return

        self._registrar_historial(a, b, op, resultado)
        self._cambiar_texto(self._formatear(resultado))

    def _calcular(self, a, b, op):
        try:
            if op == "+":
                resultado = a + b
            elif op == "-":
                resultado = a - b
            elif op == "*":
                resultado = a * b
            elif op == "/":
                if b == 0:
                    self._error("No se puede dividir entre cero")
                    return None
                resultado = a / b
            else:
                self._error("Operación no válida")
                return None

            if not math.isfinite(resultado):
                self._error("El resultado es demasiado grande")
                return None
            return resultado
        except ZeroDivisionError:
            self._error("No se puede dividir entre cero")
            return None
        except (OverflowError, ValueError):
            self._error("Error en la operación")
            return None

    def _leer_pantalla(self):
        try:
            valor = float(self.pantalla_var.get())
            if not math.isfinite(valor):
                raise ValueError
            return valor
        except ValueError:
            self._error("Entrada no válida")
            return None

    def _formatear(self, valor):
        if valor == int(valor) and abs(valor) < 1e16:
            return str(int(valor))
        return f"{valor:.10g}"

    def _cambiar_texto(self, texto):
        self.pantalla_var.set(texto)
        self.pantalla.configure(text_color=BLUE_DARK, border_color=BLUE_ACCENT)

    def _error(self, mensaje):
        self.pantalla_var.set(mensaje)
        self.pantalla.configure(text_color=RED, border_color=RED)
        self._operacion = None
        self._operandos = []
        self._nuevo_numero = True
        self._error_activo = True
        self.operacion_var.set("")
        messagebox.showwarning("Error", mensaje, parent=self)

    def _limpiar(self):
        self._reiniciar()

    def _reiniciar(self):
        self._operacion = None
        self._operandos = []
        self._nuevo_numero = False
        self._error_activo = False
        self.operacion_var.set("")
        self._cambiar_texto("0")

    # ----------------------------------------------------------- teclado

    def _tecla_pulsada(self, evento):
        texto = evento.char
        if texto.isdigit() or texto == ".":
            self._digito(texto)
        elif texto in SIMBOLOS:
            self._operador(texto)
        elif texto in ("=", "\r", "\n"):
            self._igual()
        elif evento.keysym == "BackSpace":
            if self._error_activo:
                self._reiniciar()
                return "break"
            if self._nuevo_numero:
                self._cambiar_texto("0")
                return "break"

            actual = self.pantalla_var.get()
            nuevo = actual[:-1] if len(actual) > 1 else "0"
            if nuevo in ("", "-", "+", "-."):
                nuevo = "0"
            self._cambiar_texto(nuevo)
            return "break"
        elif evento.keysym == "Escape":
            self._limpiar()
            return "break"
        return "break"


def main():
    app = Calculadora()
    app.mainloop()


if __name__ == "__main__":
    main()
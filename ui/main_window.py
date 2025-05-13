from PyQt5.QtWidgets import (
    QMainWindow, QFileDialog, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout,QMessageBox
)
import pandas as pd
import os

from core.lexer.lexer import Lexer
from core.parser.parser import Parser
from core.parser.parser_utils import load_tokens_from_csv
from core.semantic.semantic_analyzer import SemanticAnalyzer
from core.codegen.vci_generator import VCIGenerator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analizador Léxico y Sintáctico")
        self.resize(1200, 700)

        self.label = QLabel("Archivo cargado: Ninguno")

        self.token_table = QTableWidget()
        self.token_table.setColumnCount(4)
        self.token_table.setHorizontalHeaderLabels(["Tipo", "Valor", "Línea", "Columna"])

        self.error_table = QTableWidget()
        self.error_table.setColumnCount(4)
        self.error_table.setHorizontalHeaderLabels(["Mensaje", "Valor", "Línea", "Columna"])

        self.syntax_error_table = QTableWidget()
        self.syntax_error_table.setColumnCount(4)
        self.syntax_error_table.setHorizontalHeaderLabels(["Mensaje", "Valor", "Línea", "Columna"])

        self.vci_table = QTableWidget()
        self.vci_table.setColumnCount(4)
        self.vci_table.setHorizontalHeaderLabels(["Operación", "Arg1", "Arg2", "Resultado"])

        self.load_button = QPushButton("Cargar archivo .txt")
        self.load_button.clicked.connect(self.load_file)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.load_button)

        table_layout = QHBoxLayout()
        table_layout.addWidget(self.token_table)
        table_layout.addWidget(self.error_table)
        table_layout.addWidget(self.syntax_error_table)
        table_layout.addWidget(self.vci_table)


        layout.addLayout(table_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo de código", "", "Archivos de texto (*.txt)")
        if file_path:
            self.label.setText(f"Archivo cargado: {file_path}")

            with open(file_path, encoding="utf-8") as f:
                code = f.read()
                lexer = Lexer()
                lexer.analyze(code)
                lexer.export_to_csv()

            self.load_csvs()
            self.run_parser()

    def load_csvs(self):
        self.load_csv("output/tokens.csv", self.token_table)
        self.load_csv("output/lexical_errors.csv", self.error_table)

    def load_csv(self, path, table_widget):
        if os.path.exists(path):
            df = pd.read_csv(path)
            table_widget.setRowCount(len(df))
            table_widget.setColumnCount(len(df.columns))
            table_widget.setHorizontalHeaderLabels(list(df.columns))
            for i, row in df.iterrows():
                for j, col in enumerate(row):
                    table_widget.setItem(i, j, QTableWidgetItem(str(col)))

    def load_vci_table(self, path):
        import pandas as pd
        if not os.path.exists(path): return
        df = pd.read_csv(path)
        self.vci_table.setRowCount(len(df))
        for i, row in df.iterrows():
            for j, col in enumerate(row):
                self.vci_table.setItem(i, j, QTableWidgetItem(str(col)))

    def run_parser(self):
        try:
            tokens = load_tokens_from_csv("output/tokens.csv")
            parser = Parser(tokens)
            ast = parser.parse()

            data = []
            for err in parser.errors:
                data.append([err.message, err.value, err.line, err.column])

            self.syntax_error_table.setRowCount(len(data))
            self.syntax_error_table.setColumnCount(4)
            self.syntax_error_table.setHorizontalHeaderLabels(["Mensaje", "Valor", "Línea", "Columna"])
            for i, row in enumerate(data):
                for j, col in enumerate(row):
                    self.syntax_error_table.setItem(i, j, QTableWidgetItem(str(col)))

            if parser.errors:
                QMessageBox.warning(self, "Errores sintácticos", "Se detectaron errores sintácticos. Revisa la tabla.")

            if not parser.errors:
                QMessageBox.information(
                    self,
                    "Compilación exitosa",
                    "El análisis sintáctico se completó correctamente. ¡El código fue compilado con éxito!"
                )

            if not parser.errors:
                analyzer = SemanticAnalyzer()
                analyzer.analyze(ast)
                analyzer.export_symbol_table()

                if analyzer.errors:
                    for err in analyzer.errors:
                        print( "Error semántico: {err.message} → {err.value}")
                    QMessageBox.information(
                        self,
                        "Error semántico",
                        "Hubo un error en el analisis sintactico"
                    )

                if not analyzer.errors:
                    QMessageBox.information(
                        self,
                        "Compilacion del Sistema Semantico Exitoso",
                        "El analisis Semantico se completo Correctamente."
                    )

            if not parser.errors and not analyzer.errors:
                vci = VCIGenerator()
                vci.generate(ast)
                vci.export_to_csv()
                self.load_vci_table("output/vci.csv")
                

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error inesperado",
                f"Ocurrió un error durante el análisis sintáctico:\n\n{str(e)}"
        )

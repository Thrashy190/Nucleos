# 🛠️ Proyecto: Analizador Léxico, Sintáctico, Semántico y Generador de Código Intermedio (VCI)

Este proyecto implementa un compilador educativo en Python que incluye:

- ✅ Interfaz visual con PyQt5
- ✅ Análisis léxico
- ✅ Análisis sintáctico (AST)
- ✅ Análisis semántico (tabla de símbolos y validaciones)
- ✅ Generación de código intermedio (VCI)
- ✅ Exportación de resultados en formato CSV

---

## 🚀 Requisitos

- Python 3.8 o superior
- Pip

### 📦 Librerías necesarias

Instálalas con:

```bash
pip install -r requirements.txt
```

O manualmente:

```bash
pip install PyQt5 pandas
```

---

## 📂 Estructura del Proyecto

```
CompilerSystem/
│
├── core/
│   ├── lexer/               # Analizador léxico
│   ├── parser/              # Parser LL(1) con AST
│   ├── semantic/            # Análisis semántico y tabla de símbolos
│   └── codegen/             # Generación de VCI (código intermedio)
│
├── models/                  # Clases base: Token, ASTNode, Symbol, etc.
├── output/                  # CSVs generados (tokens, errores, tabla de símbolos, VCI)
├── ui/
│   └── main_window.py       # Interfaz principal PyQt5
│
├── input.txt                # Código fuente de prueba
└── main.py                  # Archivo de Ejecucion Principal
```

---

## 🖥️ ¿Cómo correr la aplicación?

### Interfaz gráfica (PyQt5)

```bash
python main.py
```

Se abrirá una ventana que te permite:

1. Cargar un archivo `.txt` de entrada (por ejemplo, `input.txt`)
2. Ver:

   - Tabla de tokens
   - Errores léxicos
   - Errores sintácticos
   - Tabla de símbolos
   - Código intermedio (VCI)

---

## 🧪 Ejemplo de archivo de entrada válido

```txt
programa ejemplo@;
variables
   entero a&, b&, suma&;
inicio
    leer(a&);
    leer(b&);
    suma& = a& + b&;
    escribir(suma&);
fin
```

---

## 📤 Archivos generados

Al compilar, se generan archivos en `/output`:

| Archivo              | Contenido                                |
| -------------------- | ---------------------------------------- |
| `tokens.csv`         | Tokens válidos reconocidos               |
| `lexical_errors.csv` | Errores léxicos (si hay)                 |
| `symbol_table.csv`   | Tabla de símbolos del análisis semántico |
| `vci.csv`            | Instrucciones de código intermedio       |

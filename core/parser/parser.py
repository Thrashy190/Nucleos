from models.token import Token
from models.ast_node import ASTNode
from models.syntax_error import SyntaxError

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.errors = []

    def current_token(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def match(self, expected_type=None, expected_value=None):
        token = self.current_token()
        if token is None:
            return None
        if expected_type and token.type != expected_type:
            return None
        if expected_value and token.value != expected_value:
            return None
        self.position += 1
        return token

    def expect(self, expected_type=None, expected_value=None):
        token = self.match(expected_type, expected_value)
        if token is None:
            current = self.current_token()
            msg = f"Se esperaba {'tipo ' + expected_type if expected_type else ''} {'valor ' + expected_value if expected_value else ''}"
            if current:
                self.errors.append(SyntaxError(msg, current.value, current.line, current.column))
            else:
                self.errors.append(SyntaxError(msg, "EOF", -1, -1))
        return token

    def parse(self):
        return self.programa()

    def programa(self):
        root = ASTNode("PROGRAMA")
        self.expect("RESERVADA", "programa")
        id_token = self.expect("ID_METODO")
        root.children.append(ASTNode("ID", id_token.value) if id_token else ASTNode("ID", "ERROR"))
        self.expect("SIMBOLO", ";")
        if self.current_token() and self.current_token().value == "variables":
            self.match("RESERVADA", "variables")  # consumir palabra "variables"
            root.children.append(self.declaraciones())
        root.children.append(self.bloque())
        return root

    def declaraciones(self):
        decls = ASTNode("DECLARACIONES")
        while self.current_token() and self.current_token().value in {"entero", "real", "cadena", "logico"}:
            tipo_token = self.match("RESERVADA")
            tipo = ASTNode("TIPO", tipo_token.value)
            lista = self.lista_id()
            tipo.children.extend(lista.children)
            self.expect("SIMBOLO", ";")
            decls.children.append(tipo)
        return decls

    def lista_id(self):
        lista = ASTNode("LISTA_ID")
        token = self.match("ID_ENTERO") or self.match("ID_REAL") or self.match("ID_CADENA") or self.match("ID_LOGICO")
        if token:
            lista.children.append(ASTNode("ID", token.value))
        else:
            self.errors.append(SyntaxError("Se esperaba un identificador válido", self.current_token().value, self.current_token().line, self.current_token().column))
            return lista
        while self.match("SIMBOLO", ","):
            token = self.match("ID_ENTERO") or self.match("ID_REAL") or self.match("ID_CADENA") or self.match("ID_LOGICO")
            if token:
                lista.children.append(ASTNode("ID", token.value))
            else:
                print(token)
                self.errors.append(SyntaxError("Se esperaba otro identificador", self.current_token().value, self.current_token().line, self.current_token().column))
        return lista

    def bloque(self):
        bloque = ASTNode("BLOQUE")
        self.expect("RESERVADA", "inicio")
        instrucciones = self.instrucciones()
        bloque.children.extend(instrucciones.children)
        self.expect("RESERVADA", "fin")
        return bloque

    def instrucciones(self):
        instrucciones = ASTNode("INSTRUCCIONES")
        while True:
            token = self.current_token()
            if token and (token.value in {"leer", "escribir", "si", "mientras", "repetir"} or token.type in {"ID_ENTERO", "ID_REAL", "ID_CADENA", "ID_LOGICO"}):
                instrucciones.children.append(self.instruccion())
            else:
                break
        return instrucciones

    def instruccion(self):
        token = self.current_token()
        if token.value == "leer":
            return self.instruccion_leer()
        elif token.value == "escribir":
            return self.instruccion_escribir()
        elif token.value == "si":
            return self.instruccion_si()
        elif token.value == "mientras":
            return self.instruccion_mientras()
        elif token.value == "repetir":
            return self.instruccion_repetir()
        elif token.type in {"ID_ENTERO", "ID_REAL", "ID_CADENA", "ID_LOGICO"}:
            return self.asignacion()
        else:
            self.errors.append(SyntaxError("Instrucción no reconocida", token.value, token.line, token.column))
            self.position += 1
            return ASTNode("ERROR")

    def instruccion_leer(self):
        nodo = ASTNode("LEER")
        self.expect("RESERVADA", "leer")
        self.expect("SIMBOLO", "(")
        id_token = self.match("ID_ENTERO") or self.match("ID_REAL") or self.match("ID_CADENA") or self.match("ID_LOGICO")
        if id_token:
            nodo.children.append(ASTNode("ID", id_token.value))
        self.expect("SIMBOLO", ")")
        self.expect("SIMBOLO", ";")
        return nodo

    def instruccion_escribir(self):
        nodo = ASTNode("ESCRIBIR")
        self.expect("RESERVADA", "escribir")
        self.expect("SIMBOLO", "(")
        expr = self.expresion()
        nodo.children.append(ASTNode("EXPR", None, [expr]))
        self.expect("SIMBOLO", ")")
        self.expect("SIMBOLO", ";")
        return nodo

    def asignacion(self):
        nodo = ASTNode("ASIGNACION")
        id_token = self.match("ID_ENTERO") or self.match("ID_REAL") or self.match("ID_CADENA") or self.match("ID_LOGICO")
        if id_token:
            nodo.children.append(ASTNode("ID", id_token.value))
        self.expect("OPERADOR", "=")
        expr = self.expresion()
        nodo.children.append(ASTNode("VALOR", None, [expr]))
        self.expect("SIMBOLO", ";")
        return nodo

    def instruccion_si(self):
        nodo = ASTNode("SI")
        self.expect("RESERVADA", "si")
        self.expect("SIMBOLO", "(")
        condicion = self.expresion()
        nodo.children.append(ASTNode("CONDICION", None, [condicion]))
        self.expect("SIMBOLO", ")")
        self.expect("RESERVADA", "entonces")
        nodo_si = self.bloque()
        nodo.children.append(ASTNode("BLOQUE_SI", None, [nodo_si]))
        if self.current_token() and self.current_token().value == "sino":
            self.match("RESERVADA", "sino")
            nodo_sino = self.bloque()
            nodo.children.append(ASTNode("BLOQUE_SINO", None, [nodo_sino]))
        return nodo

    def instruccion_mientras(self):
        nodo = ASTNode("MIENTRAS")
        self.expect("RESERVADA", "mientras")
        self.expect("SIMBOLO", "(")
        condicion = self.expresion()
        nodo.children.append(ASTNode("CONDICION", None, [condicion]))
        self.expect("SIMBOLO", ")")
        self.expect("RESERVADA", "hacer")
        cuerpo = self.bloque()
        nodo.children.append(ASTNode("CUERPO", None, [cuerpo]))
        return nodo

    def instruccion_repetir(self):
        nodo = ASTNode("REPETIR")
        self.expect("RESERVADA", "repetir")
        cuerpo = self.bloque()
        nodo.children.append(ASTNode("CUERPO", None, [cuerpo]))
        self.expect("RESERVADA", "hasta")
        self.expect("SIMBOLO", "(")
        condicion = self.expresion()
        nodo.children.append(ASTNode("CONDICION", None, [condicion]))
        self.expect("SIMBOLO", ")")
        self.expect("SIMBOLO", ";")
        return nodo

    def expresion(self):
        nodo = self.expresion_simple()
        if self.current_token() and self.current_token().value in {">", "<", ">=", "<=", "==", "!="}:
            op = self.match("OPERADOR")
            if op:
                derecho = self.expresion_simple()
                nodo = ASTNode("COMPARACION", op.value, [nodo, derecho])
        return nodo

    def expresion_simple(self):
        nodo = self.termino()
        while self.current_token() and self.current_token().value in {"+", "-", "||"}:
            op = self.match("OPERADOR")
            if op:
                derecho = self.termino()
                nodo = ASTNode("OPERACION", op.value, [nodo, derecho])
        return nodo

    def termino(self):
        nodo = self.factor()
        while self.current_token() and self.current_token().value in {"*", "/", "&&"}:
            op = self.match("OPERADOR")
            if op:
                derecho = self.factor()
                nodo = ASTNode("OPERACION", op.value, [nodo, derecho])
        return nodo

    def factor(self):
        token = self.match("ID_ENTERO") or self.match("ID_REAL") or self.match("ID_CADENA") or self.match("ID_LOGICO") or self.match("ENTERO") or self.match("REAL") or self.match("CADENA") or self.match("BOOLEANO")
        if token:
            return ASTNode("LITERAL", token.value)
        elif self.match("SIMBOLO", "("):
            expr = self.expresion()
            self.expect("SIMBOLO", ")")
            return expr
        else:
            self.errors.append(SyntaxError("Factor inválido", self.current_token().value, self.current_token().line, self.current_token().column))
            return ASTNode("ERROR")

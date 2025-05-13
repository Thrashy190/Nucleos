import csv
from models.token import Token

def load_tokens_from_csv(path="output/tokens.csv"):
    tokens = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tokens.append(Token(
                type=row["Tipo"],
                value=row["Valor"],
                line=int(row["Línea"]),
                column=int(row["Columna"])
            ))
    return tokens

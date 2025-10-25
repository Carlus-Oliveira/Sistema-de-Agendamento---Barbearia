from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc
import re

app = Flask(__name__)
app.secret_key = "chave_super_secreta"


conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=BarbeariaMagnus;"
    "Trusted_Connection=yes;"
)

 # retorno p/ pagina html

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/cadastros")
def cadastros():
    return render_template("cadastros.html")

# Pagina cliente

def formatar_telefone(telefone: str) -> str:
    """Formata o telefone para (99) 99999-9999 ou (99) 9999-9999"""
    numeros = re.sub(r"\D", "", telefone)
    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    elif len(numeros) == 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    return telefone

@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    cursor = conn.cursor()
    if request.method == "POST":
        nome = request.form["nome"].strip()
        email = request.form["email"].strip()
        telefone = formatar_telefone(request.form["telefone"])

        # verificar nome e telefone cliente "duplicidade"

        cursor.execute(
            "SELECT COUNT(*) FROM Clientes WHERE nome = ? AND telefone = ?",
            (nome, telefone)
        )
        existe = cursor.fetchone()[0]

        if existe > 0:
            flash("❌ Já existe um cliente com este nome e telefone.", "error")
            return redirect(url_for("clientes"))

        try:
            cursor.execute(
                "INSERT INTO Clientes (nome, email, telefone) VALUES (?, ?, ?)",
                (nome, email, telefone)
            )
            conn.commit()
            flash("✅ Cliente cadastrado com sucesso!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"❌ Erro ao cadastrar cliente: {e}", "error")

        return redirect(url_for("clientes"))

    # exibir lista

    cursor.execute("SELECT id, nome, email, telefone FROM Clientes")
    clientes = cursor.fetchall()
    return render_template("clientes.html", clientes=clientes)

@app.route("/excluir_cliente/<int:id>")
def excluir_cliente(id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Clientes WHERE id=?", (id,))
    conn.commit()
    flash("✅ Cliente excluído com sucesso!", "success")
    return redirect(url_for("clientes"))

# pagina Barbeiros

@app.route("/barbeiros", methods=["GET", "POST"])
def barbeiros():
    cursor = conn.cursor()
    if request.method == "POST":
        nome = request.form["nome"]
        especialidade = request.form["especialidade"]
        cursor.execute(
            "INSERT INTO Barbeiros (nome, especialidade) VALUES (?, ?)",
            (nome, especialidade),
        )
        conn.commit()
        flash("✅ Barbeiro cadastrado com sucesso!", "success")
        return redirect(url_for("barbeiros"))

    cursor.execute("SELECT id, nome, especialidade FROM Barbeiros")
    barbeiros = cursor.fetchall()
    return render_template("barbeiros.html", barbeiros=barbeiros)


@app.route("/excluir_barbeiro/<int:id>")
def excluir_barbeiro(id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Barbeiros WHERE id=?", (id,))
    conn.commit()
    flash("✅ Barbeiro excluído com sucesso!", "success")
    return redirect(url_for("barbeiros"))

# Serviços

@app.route("/servicos", methods=["GET", "POST"])
def servicos():
    cursor = conn.cursor()
    if request.method == "POST":
        nome = request.form["nome"]
        preco = float(request.form["preco"])  # ✅ novo campo
        duracao_minutos = int(request.form["duracao_minutos"])

        try:
            cursor.execute(
                "INSERT INTO Servicos (nome, preco, duracao_minutos) VALUES (?, ?, ?)",
                (nome, preco, duracao_minutos),
            )
            conn.commit()
            flash("✅ Serviço cadastrado com sucesso!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"❌ Erro ao cadastrar serviço: {e}", "error")

        return redirect(url_for("servicos"))

    cursor.execute("SELECT id, nome, preco, duracao_minutos FROM Servicos")
    servicos = cursor.fetchall()
    return render_template("servicos.html", servicos=servicos)

@app.route("/excluir_servico/<int:id>")
def excluir_servico(id):
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Servicos WHERE id=?", (id,))
        conn.commit()
        flash("✅ Serviço excluído com sucesso!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"❌ Erro ao excluir serviço: {e}", "error")

    return redirect(url_for("servicos"))
#rum

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "vaca-parida-dev"
BASE_DIR = Path(__file__).resolve().parent
DB = BASE_DIR / "vaca_parida.db"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS animais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brinco TEXT NOT NULL,
            tipo TEXT NOT NULL,
            raca TEXT,
            sexo TEXT,
            nascimento TEXT,
            peso REAL DEFAULT 0,
            observacoes TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS custos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            categoria TEXT NOT NULL,
            data TEXT,
            valor REAL NOT NULL,
            animal_id INTEGER,
            FOREIGN KEY(animal_id) REFERENCES animais(id)
        )
    """)

    conn.commit()
    conn.close()


@app.context_processor
def inject_stats():
    conn = get_db()
    animais = conn.execute("SELECT COUNT(*) FROM animais").fetchone()[0]
    matrizes = conn.execute(
        "SELECT COUNT(*) FROM animais WHERE tipo = 'Matriz'"
    ).fetchone()[0]
    bezerros = conn.execute(
        "SELECT COUNT(*) FROM animais WHERE tipo = 'Bezerro'"
    ).fetchone()[0]
    total = conn.execute(
        "SELECT COALESCE(SUM(valor), 0) FROM custos"
    ).fetchone()[0]
    conn.close()

    return {
        "stats": {
            "animais": animais,
            "matrizes": matrizes,
            "bezerros": bezerros,
            "total": total
        }
    }


@app.route("/")
def index():
    conn = get_db()
    recentes = conn.execute(
        "SELECT * FROM animais ORDER BY id DESC LIMIT 5"
    ).fetchall()
    custos_recentes = conn.execute("""
        SELECT c.*, a.brinco
        FROM custos c
        LEFT JOIN animais a ON a.id = c.animal_id
        ORDER BY c.id DESC
        LIMIT 5
    """).fetchall()
    conn.close()

    return render_template(
        "index.html",
        recentes=recentes,
        custos_recentes=custos_recentes
    )


@app.route("/rebanho")
def rebanho():
    conn = get_db()
    animais = conn.execute(
        "SELECT * FROM animais ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template("rebanho.html", animais=animais)


@app.route("/rebanho/novo", methods=["GET", "POST"])
def novo_animal():
    if request.method == "POST":
        brinco = request.form.get("brinco", "").strip()
        tipo = request.form.get("tipo", "").strip()

        if not brinco or not tipo:
            flash("Preencha o brinco e o tipo do animal.", "error")
            return render_template("animal_form.html", animal=None)

        try:
            peso = float(request.form.get("peso") or 0)
        except ValueError:
            flash("O peso precisa ser um número válido.", "error")
            return render_template("animal_form.html", animal=None)

        conn = get_db()
        conn.execute("""
            INSERT INTO animais
            (brinco, tipo, raca, sexo, nascimento, peso, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            brinco,
            tipo,
            request.form.get("raca", "").strip(),
            request.form.get("sexo", ""),
            request.form.get("nascimento", ""),
            peso,
            request.form.get("observacoes", "").strip()
        ))
        conn.commit()
        conn.close()

        flash("Animal cadastrado com sucesso!", "success")
        return redirect(url_for("rebanho"))

    return render_template("animal_form.html", animal=None)


@app.route("/rebanho/editar/<int:id>", methods=["GET", "POST"])
def editar_animal(id):
    conn = get_db()
    animal = conn.execute(
        "SELECT * FROM animais WHERE id = ?", (id,)
    ).fetchone()

    if not animal:
        conn.close()
        flash("Animal não encontrado.", "error")
        return redirect(url_for("rebanho"))

    if request.method == "POST":
        try:
            peso = float(request.form.get("peso") or 0)
        except ValueError:
            conn.close()
            flash("O peso precisa ser um número válido.", "error")
            return render_template("animal_form.html", animal=animal)

        conn.execute("""
            UPDATE animais SET
                brinco = ?, tipo = ?, raca = ?, sexo = ?,
                nascimento = ?, peso = ?, observacoes = ?
            WHERE id = ?
        """, (
            request.form.get("brinco", "").strip(),
            request.form.get("tipo", ""),
            request.form.get("raca", "").strip(),
            request.form.get("sexo", ""),
            request.form.get("nascimento", ""),
            peso,
            request.form.get("observacoes", "").strip(),
            id
        ))
        conn.commit()
        conn.close()

        flash("Cadastro atualizado com sucesso!", "success")
        return redirect(url_for("rebanho"))

    conn.close()
    return render_template("animal_form.html", animal=animal)


@app.post("/rebanho/excluir/<int:id>")
def excluir_animal(id):
    conn = get_db()
    conn.execute("DELETE FROM custos WHERE animal_id = ?", (id,))
    conn.execute("DELETE FROM animais WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    flash("Animal excluído com sucesso.", "success")
    return redirect(url_for("rebanho"))


@app.route("/custos", methods=["GET", "POST"])
def custos():
    if request.method == "POST":
        try:
            animal_id = request.form.get("animal_id") or None
            data = request.form.get("data", "")
            categorias = [
                ("Manejo sanitário", "manejo_sanitario"),
                ("Suplementação mineral", "suplementacao"),
                ("Medicamentos", "medicamentos"),
                ("Alimentação", "alimentacao"),
            ]

            conn = get_db()
            adicionados = 0

            for categoria, campo in categorias:
                valor = float(request.form.get(campo) or 0)
                if valor > 0:
                    conn.execute("""
                        INSERT INTO custos
                        (descricao, categoria, data, valor, animal_id)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        categoria,
                        categoria,
                        data,
                        valor,
                        animal_id
                    ))
                    adicionados += 1

            conn.commit()
            conn.close()

            if adicionados == 0:
                flash("Informe pelo menos um custo maior que zero.", "error")
            else:
                flash("Custos registrados com sucesso!", "success")

            return redirect(url_for("custos"))

        except ValueError:
            flash("Digite apenas valores numéricos nos custos.", "error")

    conn = get_db()
    animais = conn.execute(
        "SELECT * FROM animais ORDER BY brinco"
    ).fetchall()
    registros = conn.execute("""
        SELECT c.*, a.brinco
        FROM custos c
        LEFT JOIN animais a ON a.id = c.animal_id
        ORDER BY c.id DESC
    """).fetchall()
    total = conn.execute(
        "SELECT COALESCE(SUM(valor), 0) FROM custos"
    ).fetchone()[0]
    conn.close()

    return render_template(
        "custos.html",
        animais=animais,
        registros=registros,
        total=total
    )


@app.post("/custos/excluir/<int:id>")
def excluir_custo(id):
    conn = get_db()
    conn.execute("DELETE FROM custos WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    flash("Lançamento excluído.", "success")
    return redirect(url_for("custos"))


@app.route("/relatorios")
def relatorios():
    conn = get_db()

    por_categoria = conn.execute("""
        SELECT categoria, SUM(valor) AS total
        FROM custos
        GROUP BY categoria
        ORDER BY total DESC
    """).fetchall()

    por_animal = conn.execute("""
        SELECT
            a.brinco,
            a.tipo,
            COALESCE(SUM(c.valor), 0) AS total
        FROM animais a
        LEFT JOIN custos c ON c.animal_id = a.id
        GROUP BY a.id
        ORDER BY total DESC
    """).fetchall()

    conn.close()

    return render_template(
        "relatorios.html",
        por_categoria=por_categoria,
        por_animal=por_animal
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

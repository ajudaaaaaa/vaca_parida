from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, g
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import timedelta
import os, secrets, hmac, time, math
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1", PERMANENT_SESSION_LIFETIME=timedelta(hours=8), MAX_CONTENT_LENGTH=1024*1024)
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
            quantidade REAL DEFAULT 0,
            animal_id INTEGER,
            FOREIGN KEY(animal_id) REFERENCES animais(id)
        )
    """)

    colunas = conn.execute("PRAGMA table_info(custos)").fetchall()
    nomes_colunas = [coluna["name"] for coluna in colunas]

    if "quantidade" not in nomes_colunas:
        conn.execute(
            "ALTER TABLE custos ADD COLUMN quantidade REAL DEFAULT 0"
        )

    conn.execute("""CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT UNIQUE NOT NULL, senha_hash TEXT NOT NULL)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS tentativas_login (usuario TEXT PRIMARY KEY, falhas INTEGER NOT NULL DEFAULT 0, bloqueado_ate REAL NOT NULL DEFAULT 0)""")
    # Migração segura: registros anteriores ficam sem dono até serem atribuídos.
    for tabela in ("animais", "custos"):
        campos = {c["name"] for c in conn.execute(f"PRAGMA table_info({tabela})")}
        if "usuario_id" not in campos:
            conn.execute(f"ALTER TABLE {tabela} ADD COLUMN usuario_id INTEGER REFERENCES usuarios(id)")
        conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{tabela}_usuario ON {tabela}(usuario_id)")
    conn.commit()
    conn.close()


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("usuario_id"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper


@app.before_request
def security_checks():
    if session.get("usuario_id"):
        with get_db() as conn:
            if not conn.execute("SELECT 1 FROM usuarios WHERE id=?", (session["usuario_id"],)).fetchone():
                session.clear()
                return redirect(url_for("login"))
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        sent = request.form.get("csrf_token", "") or request.headers.get("X-CSRF-Token", "")
        expected = session.get("csrf_token", "")
        if not expected or not hmac.compare_digest(sent, expected):
            abort(400, "Token de segurança inválido. Atualize a página e tente novamente.")


@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; script-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
    response.headers["Cache-Control"] = "no-store"
    if os.environ.get("COOKIE_SECURE") == "1":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("usuario_id"):
        return redirect(url_for("index"))
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip().lower()[:80]
        senha = request.form.get("senha", "")
        conn = get_db()
        limite = conn.execute("SELECT falhas, bloqueado_ate FROM tentativas_login WHERE usuario=?", (usuario,)).fetchone()
        if limite and limite["bloqueado_ate"] > time.time():
            conn.close()
            flash("Muitas tentativas. Aguarde 15 minutos.", "error")
            return render_template("login.html"), 429
        row = conn.execute("SELECT id, usuario, senha_hash FROM usuarios WHERE usuario=?", (usuario,)).fetchone()
        if row and check_password_hash(row["senha_hash"], senha):
            conn.execute("DELETE FROM tentativas_login WHERE usuario=?", (usuario,))
            conn.commit(); conn.close()
            session.clear(); session["usuario_id"] = row["id"]; session["usuario"] = row["usuario"]
            session["csrf_token"] = secrets.token_urlsafe(32); session.permanent = True
            return redirect(url_for("index"))
        falhas = (limite["falhas"] if limite else 0) + 1
        bloqueio = time.time()+900 if falhas >= 5 else 0
        conn.execute("INSERT INTO tentativas_login(usuario,falhas,bloqueado_ate) VALUES(?,?,?) ON CONFLICT(usuario) DO UPDATE SET falhas=excluded.falhas,bloqueado_ate=excluded.bloqueado_ate", (usuario, falhas, bloqueio))
        conn.commit(); conn.close()
        flash("Usuário ou senha inválidos.", "error")
    return render_template("login.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip().lower()
        senha = request.form.get("senha", "")
        confirmacao = request.form.get("confirmacao", "")
        if not (3 <= len(usuario) <= 80) or not all(c.isascii() and (c.isalnum() or c in "._-") for c in usuario):
            flash("Use de 3 a 80 caracteres: letras, números, ponto, hífen ou sublinhado.", "error")
        elif len(senha) < 12 or len(senha) > 128:
            flash("A senha deve ter de 12 a 128 caracteres.", "error")
        elif senha != confirmacao:
            flash("As senhas não coincidem.", "error")
        else:
            conn = get_db()
            try:
                conn.execute("INSERT INTO usuarios (usuario, senha_hash) VALUES (?, ?)", (usuario, generate_password_hash(senha)))
                conn.commit()
            except sqlite3.IntegrityError:
                flash("Esse nome de usuário já está em uso.", "error")
            else:
                flash("Conta criada! Entre com seu usuário e senha.", "success")
                return redirect(url_for("login"))
            finally:
                conn.close()
    return render_template("cadastro.html")


@app.post("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.context_processor
def inject_stats():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    if not session.get("usuario_id"):
        return {"stats": {"animais": 0, "matrizes": 0, "bezerros": 0, "total": 0}, "csrf_token": session["csrf_token"]}
    conn = get_db()
    animais = conn.execute("SELECT COUNT(*) FROM animais WHERE usuario_id=?", (session["usuario_id"],)).fetchone()[0]
    matrizes = conn.execute(
        "SELECT COUNT(*) FROM animais WHERE tipo = 'Matriz' AND usuario_id=?", (session["usuario_id"],)
    ).fetchone()[0]
    bezerros = conn.execute(
        "SELECT COUNT(*) FROM animais WHERE tipo = 'Bezerro' AND usuario_id=?", (session["usuario_id"],)
    ).fetchone()[0]
    total = conn.execute(
        "SELECT COALESCE(SUM(valor), 0) FROM custos WHERE usuario_id=?", (session["usuario_id"],)
    ).fetchone()[0]
    conn.close()

    return {
        "csrf_token": session["csrf_token"],
        "stats": {
            "animais": animais,
            "matrizes": matrizes,
            "bezerros": bezerros,
            "total": total
        }
    }


@app.route("/")
@login_required
def index():
    conn = get_db()
    recentes = conn.execute(
        "SELECT * FROM animais WHERE usuario_id=? ORDER BY id DESC LIMIT 5", (session["usuario_id"],)
    ).fetchall()
    custos_recentes = conn.execute("""
        SELECT c.*, a.brinco
        FROM custos c
        LEFT JOIN animais a ON a.id = c.animal_id AND a.usuario_id = c.usuario_id
        WHERE c.usuario_id=?
        ORDER BY c.id DESC
        LIMIT 5
    """, (session["usuario_id"],)).fetchall()
    conn.close()

    return render_template(
        "index.html",
        recentes=recentes,
        custos_recentes=custos_recentes
    )


@app.route("/rebanho")
@login_required
def rebanho():
    conn = get_db()
    animais = conn.execute(
        "SELECT * FROM animais WHERE usuario_id=? ORDER BY id DESC", (session["usuario_id"],)
    ).fetchall()
    conn.close()

    return render_template("rebanho.html", animais=animais)


@app.route("/rebanho/novo", methods=["GET", "POST"])
@login_required
def novo_animal():
    if request.method == "POST":
        brinco = request.form.get("brinco", "").strip()
        tipo = request.form.get("tipo", "").strip()

        if not brinco or not tipo:
            flash("Preencha o brinco e o tipo do animal.", "error")
            return render_template("animal_form.html", animal=None)

        try:
            peso = float(request.form.get("peso") or 0)
            if not math.isfinite(peso) or peso < 0: raise ValueError()
        except ValueError:
            flash("O peso precisa ser um número válido.", "error")
            return render_template("animal_form.html", animal=None)

        conn = get_db()
        conn.execute("""
            INSERT INTO animais
            (brinco, tipo, raca, sexo, nascimento, peso, observacoes, usuario_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            brinco,
            tipo,
            request.form.get("raca", "").strip(),
            request.form.get("sexo", ""),
            request.form.get("nascimento", ""),
            peso,
            request.form.get("observacoes", "").strip(),
            session["usuario_id"]
        ))
        conn.commit()
        conn.close()

        flash("Animal cadastrado com sucesso!", "success")
        return redirect(url_for("rebanho"))

    return render_template("animal_form.html", animal=None)


@app.route("/rebanho/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_animal(id):
    conn = get_db()
    animal = conn.execute(
        "SELECT * FROM animais WHERE id = ? AND usuario_id = ?", (id, session["usuario_id"])
    ).fetchone()

    if not animal:
        conn.close()
        flash("Animal não encontrado.", "error")
        return redirect(url_for("rebanho"))

    if request.method == "POST":
        try:
            peso = float(request.form.get("peso") or 0)
            if not math.isfinite(peso) or peso < 0: raise ValueError()
        except ValueError:
            conn.close()
            flash("O peso precisa ser um número válido.", "error")
            return render_template("animal_form.html", animal=animal)

        conn.execute("""
            UPDATE animais SET
                brinco = ?, tipo = ?, raca = ?, sexo = ?,
                nascimento = ?, peso = ?, observacoes = ?
            WHERE id = ? AND usuario_id = ?
        """, (
            request.form.get("brinco", "").strip(),
            request.form.get("tipo", ""),
            request.form.get("raca", "").strip(),
            request.form.get("sexo", ""),
            request.form.get("nascimento", ""),
            peso,
            request.form.get("observacoes", "").strip(),
            id, session["usuario_id"]
        ))
        conn.commit()
        conn.close()

        flash("Cadastro atualizado com sucesso!", "success")
        return redirect(url_for("rebanho"))

    conn.close()
    return render_template("animal_form.html", animal=animal)


@app.post("/rebanho/excluir/<int:id>")
@login_required
def excluir_animal(id):
    conn = get_db()
    conn.execute("DELETE FROM custos WHERE animal_id = ? AND usuario_id = ?", (id, session["usuario_id"]))
    conn.execute("DELETE FROM animais WHERE id = ? AND usuario_id = ?", (id, session["usuario_id"]))
    conn.commit()
    conn.close()

    flash("Animal excluído com sucesso.", "success")
    return redirect(url_for("rebanho"))


@app.route("/custos", methods=["GET", "POST"])
@login_required
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

            quantidade_suplementacao = float(
                request.form.get("quantidade_suplementacao") or 0
            )

            if not math.isfinite(quantidade_suplementacao) or quantidade_suplementacao < 0: raise ValueError()
            if animal_id and not conn.execute("SELECT id FROM animais WHERE id=? AND usuario_id=?", (animal_id, session["usuario_id"])).fetchone():
                conn.close(); abort(400, "Animal inválido")
            for categoria, campo in categorias:
                valor = float(request.form.get(campo) or 0)
                if not math.isfinite(valor) or valor < 0: raise ValueError()

                if valor > 0:
                    quantidade = (
                        quantidade_suplementacao
                        if campo == "suplementacao"
                        else 0
                    )

                    conn.execute("""
                        INSERT INTO custos
                        (descricao, categoria, data, valor, quantidade, animal_id, usuario_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        categoria,
                        categoria,
                        data,
                        valor,
                        quantidade,
                        animal_id,
                        session["usuario_id"]
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
        "SELECT * FROM animais WHERE usuario_id=? ORDER BY brinco", (session["usuario_id"],)
    ).fetchall()
    registros = conn.execute("""
        SELECT c.*, a.brinco
        FROM custos c
        LEFT JOIN animais a ON a.id = c.animal_id AND a.usuario_id = c.usuario_id
        WHERE c.usuario_id=?
        ORDER BY c.id DESC
    """, (session["usuario_id"],)).fetchall()
    total = conn.execute(
        "SELECT COALESCE(SUM(valor), 0) FROM custos WHERE usuario_id=?", (session["usuario_id"],)
    ).fetchone()[0]
    conn.close()

    return render_template(
        "custos.html",
        animais=animais,
        registros=registros,
        total=total
    )


@app.post("/custos/excluir/<int:id>")
@login_required
def excluir_custo(id):
    conn = get_db()
    conn.execute("DELETE FROM custos WHERE id = ? AND usuario_id = ?", (id, session["usuario_id"]))
    conn.commit()
    conn.close()

    flash("Lançamento excluído.", "success")
    return redirect(url_for("custos"))


@app.route("/relatorios")
@login_required
def relatorios():
    conn = get_db()

    por_categoria = conn.execute("""
        SELECT categoria, SUM(valor) AS total
        FROM custos
        WHERE usuario_id=?
        GROUP BY categoria
        ORDER BY total DESC
    """, (session["usuario_id"],)).fetchall()

    por_animal = conn.execute("""
        SELECT
            a.brinco,
            a.tipo,
            COALESCE(SUM(c.valor), 0) AS total
        FROM animais a
        LEFT JOIN custos c ON c.animal_id = a.id AND c.usuario_id = a.usuario_id
        WHERE a.usuario_id=?
        GROUP BY a.id
        ORDER BY total DESC
    """, (session["usuario_id"],)).fetchall()

    conn.close()

    return render_template(
        "relatorios.html",
        por_categoria=por_categoria,
        por_animal=por_animal
    )


init_db()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")

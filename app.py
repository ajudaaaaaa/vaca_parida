from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/custos", methods=["GET", "POST"])
def custos():
    resultado = None

    if request.method == "POST":
        manejo_sanitario = float(request.form["manejo_sanitario"])
        suplementacao = float(request.form["suplementacao"])
        medicamentos = float(request.form["medicamentos"])
        alimentacao = float(request.form["alimentacao"])

        custo_total = (
            manejo_sanitario
            + suplementacao
            + medicamentos
            + alimentacao
        )

        resultado = {
            "manejo_sanitario": manejo_sanitario,
            "suplementacao": suplementacao,
            "medicamentos": medicamentos,
            "alimentacao": alimentacao,
            "custo_total": custo_total
        }

    return render_template("custos.html", resultado=resultado)


if __name__ == "__main__":
    app.run(debug=True)
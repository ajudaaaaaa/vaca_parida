# Vaca Parida — site funcional

Aplicação Flask para controle de rebanho e custos de produção.

## Páginas

- Dashboard
- Rebanho: cadastrar, editar, pesquisar e excluir animais
- Custos: registrar e excluir lançamentos
- Relatórios: custos por categoria e por animal
- Banco SQLite criado automaticamente

## Como executar

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Depois abra:

http://127.0.0.1:5000

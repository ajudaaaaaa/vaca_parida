"""Crie um usuário inicial: python setup_admin.py"""
import getpass
from werkzeug.security import generate_password_hash
from app import get_db
usuario = input("Nome de usuário: ").strip().lower()
if not usuario or len(usuario)>80: raise SystemExit("Usuário inválido")
senha = getpass.getpass("Senha (mínimo 12 caracteres): ")
if len(senha)<12: raise SystemExit("Use pelo menos 12 caracteres")
confirmacao = getpass.getpass("Confirme a senha: ")
if senha != confirmacao: raise SystemExit("Senhas diferentes")
with get_db() as conn:
    conn.execute("INSERT INTO usuarios(usuario,senha_hash) VALUES(?,?)",(usuario,generate_password_hash(senha)))
print("Usuário criado. Não compartilhe a senha.")

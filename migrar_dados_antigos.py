"""Atribui registros legados sem dono a uma conta escolhida."""
from app import get_db

usuario = input("Usuário que é dono de TODOS os dados antigos: ").strip().lower()
with get_db() as conn:
    conta = conn.execute("SELECT id FROM usuarios WHERE usuario=?", (usuario,)).fetchone()
    if not conta:
        raise SystemExit("Conta não encontrada. Crie a conta primeiro.")
    a = conn.execute("SELECT COUNT(*) FROM animais WHERE usuario_id IS NULL").fetchone()[0]
    c = conn.execute("SELECT COUNT(*) FROM custos WHERE usuario_id IS NULL").fetchone()[0]
    print(f"Registros antigos sem dono: {a} animais e {c} custos")
    if input(f"Atribuir TODOS à conta {usuario}? Digite CONFIRMAR: ") != "CONFIRMAR":
        raise SystemExit("Cancelado; nenhum registro foi alterado.")
    conn.execute("UPDATE animais SET usuario_id=? WHERE usuario_id IS NULL", (conta["id"],))
    conn.execute("UPDATE custos SET usuario_id=? WHERE usuario_id IS NULL", (conta["id"],))
    conn.commit()
print("Atribuição concluída.")

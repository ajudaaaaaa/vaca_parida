# Vaca Parida — atualização visual e segurança

## Iniciar

```bash
pip install -r requirements.txt
python setup_admin.py
python app.py
```

Abra http://127.0.0.1:5000. Crie uma senha forte com no mínimo 12 caracteres.

## Hospedagem

Defina a variável de ambiente `SECRET_KEY` com uma chave aleatória persistente (por exemplo, gerada com `python -c "import secrets; print(secrets.token_hex(32))"`). Configure `COOKIE_SECURE=1` **somente com HTTPS**. Nunca habilite `FLASK_DEBUG=1` em produção. Instale HTTPS, configure backups seguros do banco e mantenha dependências atualizadas.

## Segurança implementada

- Login com senha armazenada em hash Werkzeug (sem texto puro).
- Rotas privadas, logout e sessão com duração de 8 horas.
- Proteção CSRF nos formulários POST.
- Bloqueio por usuário por 15 minutos após 5 falhas (para produção, complemente com limite por IP na borda).
- Cabeçalhos CSP, X-Frame-Options, nosniff, Referrer-Policy, cache-control.
- Cookies HttpOnly, SameSite=Lax; Secure em HTTPS quando configurado.
- SQL parametrizado e validação adicional de valores financeiros.

## Observações

O banco de dados original NÃO acompanha o ZIP para evitar exposição de dados reais. Faça backup do seu `vaca_parida.db` e coloque-o na pasta do projeto para preservar seus registros. O script cria somente as tabelas novas de autenticação. Esta implementação não substitui auditoria de segurança, HTTPS, monitoramento, backups e configuração adequada de produção. O bloqueio por usuário pode ser abusado para bloquear temporariamente outra conta; considere limites por IP e MFA antes de uso sensível em larga escala.

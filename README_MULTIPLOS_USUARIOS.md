# Cadastro de múltiplos usuários

Acesse `/cadastro` ou clique em **Criar conta** na tela de login. Cada usuário possui credenciais próprias e senha armazenada por hash.

**Atenção:** nesta versão, todas as contas acessam os MESMOS dados de rebanho e custos. Não é uma solução multiempresa/multipropriedade. Como o cadastro é público, qualquer pessoa que conheça a URL pode criar uma conta e acessar os dados compartilhados. **Não publique esta versão em produção com dados reais sem implementar aprovação de novos usuários ou convites e controles de permissão.**

Para rodar: `pip install -r requirements.txt` e `python app.py`. Em produção, configure `SECRET_KEY` persistente, HTTPS e `COOKIE_SECURE=1`. Preserve o arquivo `vaca_parida.db` existente (faça backup antes).

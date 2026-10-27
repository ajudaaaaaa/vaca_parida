# Rebanhos privados por usuário

Cada conta tem seu próprio rebanho, custos, painel e relatórios. Consultas e alterações verificam `usuario_id` no servidor, inclusive URLs de edição e exclusão.

## Banco antigo

Faça backup de `vaca_parida.db` antes da atualização. O aplicativo adiciona `usuario_id` às tabelas existentes sem apagar registros. **Registros antigos permanecem sem proprietário e não aparecem em nenhuma conta**, evitando vazamento entre usuários.

Para atribuir os dados antigos a uma conta específica, execute no diretório do projeto, após criar a conta:

```bash
python migrar_dados_antigos.py
```

O script solicita o nome da conta, mostra quantos registros sem dono existem e pede confirmação. Faça isso apenas se TODOS os registros antigos pertencerem àquela conta.

## Produção

Configure SECRET_KEY persistente, COOKIE_SECURE=1 com HTTPS, faça backup e execute testes antes de publicar. Cadastro aberto permite criação de contas, mas os dados são isolados.

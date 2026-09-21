# Sistema de Controle de Custo de Produção de Vaca Parida e Cria

🌐 **Aplicação Web Online:**
[COLOCAR AQUI O LINK DO PYTHONANYWHERE]

---

## Sobre o Projeto

Este projeto consiste no desenvolvimento de um sistema web para auxiliar produtores rurais no controle dos custos de produção de vacas paridas e suas crias até o desmame.

A aplicação permite registrar informações relacionadas às matrizes, bezerros, despesas de manejo e suplementação, além de realizar o controle e cálculo dos custos de produção.

O sistema foi desenvolvido com o objetivo de facilitar o acompanhamento financeiro da propriedade rural e auxiliar na tomada de decisões relacionadas à produção.

---

## Objetivo

Desenvolver uma aplicação web que possibilite:

* Cadastrar vacas (matrizes);
* Cadastrar bezerros;
* Associar o bezerro à sua matriz;
* Registrar despesas de manejo;
* Registrar despesas sanitárias;
* Registrar suplementação mineral;
* Registrar medicamentos;
* Atualizar registros;
* Excluir registros;
* Calcular o custo de produção;
* Consultar os custos relacionados às vacas e aos bezerros;
* Visualizar informações e históricos dos custos.

---

## Público-alvo

O sistema foi desenvolvido principalmente para:

* Pequenos produtores rurais;
* Administradores de fazendas;
* Técnicos agropecuários.

---

# Funcionalidades

## Cadastro

* Cadastro de vacas (matrizes);
* Cadastro de bezerros;
* Associação do bezerro à sua matriz.

## Controle de Custos

* Registro de despesas sanitárias;
* Registro de suplementação mineral;
* Registro de medicamentos;
* Registro de outras despesas relacionadas ao manejo;
* Atualização de registros;
* Exclusão de registros.

## Consultas

* Consulta de custos por vaca;
* Consulta de custos por bezerro;
* Consulta de despesas;
* Visualização do histórico de manejos.

## Cálculos

O sistema realiza o processamento dos dados cadastrados para auxiliar no acompanhamento do custo acumulado da produção da vaca parida e de sua cria.

---

# Histórias de Usuário

### Francisco Silva — Produtor Rural

> Como produtor rural, quero registrar as despesas da vaca parida e sua cria para acompanhar o custo de produção de cada bezerro.

### Orlando Oliveira — Administrador

> Como administrador da fazenda, quero consultar relatórios de custos para analisar os gastos relacionados às matrizes e suas crias.

### Felipe Santos — Técnico Agropecuário

> Como técnico agropecuário, quero registrar os manejos sanitários realizados para manter o histórico atualizado e contribuir para o controle correto dos custos.

---

# Tecnologias Utilizadas

O projeto foi desenvolvido utilizando:

* **Python**
* **Flask**
* **HTML**
* **CSS**
* **Git**
* **GitHub**
* **PlantUML**
* **PythonAnywhere**

O Git e o GitHub foram utilizados para controle de versão e organização do desenvolvimento do projeto.

O PlantUML foi utilizado para a criação dos diagramas da arquitetura.

O PythonAnywhere foi utilizado para disponibilizar a aplicação web publicamente.

---

# Metodologia

Durante o desenvolvimento foram utilizadas práticas de engenharia de software para organizar as etapas do projeto.

O desenvolvimento foi estruturado a partir de **Histórias de Usuário**, permitindo identificar as necessidades dos diferentes usuários do sistema.

O código foi versionado utilizando **Git e GitHub**, com organização das tarefas por meio do **GitHub Projects**.

A arquitetura do sistema foi documentada utilizando diagramas desenvolvidos em **PlantUML**.

Após o desenvolvimento, a aplicação foi disponibilizada na nuvem por meio do **PythonAnywhere**.

---

# Arquitetura do Sistema

A arquitetura do sistema foi planejada e documentada utilizando a linguagem **PlantUML**, permitindo representar os principais elementos envolvidos no funcionamento da aplicação.

## Diagrama de Contexto — C4 Nível 1

O Diagrama de Contexto representa uma visão geral do sistema e sua interação com o usuário principal.

![Diagrama de Contexto](contexto.png)

Arquivo PlantUML: `contexto.puml`

---

## Diagrama de Contêiner — C4 Nível 2

O Diagrama de Contêiner apresenta os principais componentes da aplicação e a forma como eles se relacionam para realizar o funcionamento do sistema.

![Diagrama C4 - Nível 2](c4_container.png)

Arquivo PlantUML: `c4_container.puml`

> **IMPORTANTE:** substituir `c4_container.png` pelo nome real do arquivo do diagrama C4 Nível 2 de vocês, caso ele tenha outro nome.

---

## Diagrama de Banco de Dados — DER

O Diagrama Entidade-Relacionamento representa a estrutura dos dados utilizados pelo sistema, incluindo informações relacionadas às vacas, bezerros, despesas e insumos.

![Diagrama de Banco de Dados](diagrama_banco.png)

Arquivo PlantUML: `diagrama_banco.puml`

---

## Fluxograma do Processo do Agro

O fluxograma representa o processo utilizado para o controle e cálculo dos custos relacionados à produção da vaca parida e sua cria.

![Fluxograma do Processo do Agro](fluxo_calculo.png)

Arquivo PlantUML: `fluxo_calculo.puml`

---

# Desenvolvedores

* **Emanuelle Cassol de Souza Godinho**
* **Luana Lopes Reis**
* **Pedro Manoel Rebelo Seti**

---

# Estrutura do Projeto

```text
projeto/
│
├── app.py
├── templates/
├── static/
├── docs/
│   ├── banner_snct.pdf
│   ├── banner_snct.png
│   └── c4_container.png
│
├── contexto.puml
├── diagrama_banco.puml
├── fluxo_calculo.puml
│
├── requirements.txt
└── README.md
```

> A estrutura acima deve ser ajustada caso os nomes dos arquivos e pastas do projeto sejam diferentes.

---

# Aplicação Online

A aplicação está hospedada no **PythonAnywhere** e pode ser acessada pelo link:

**[COLOCAR AQUI O LINK DO PYTHONANYWHERE]**

O sistema disponibiliza as principais funcionalidades de cadastro, consulta, atualização, exclusão e processamento dos dados relacionados ao controle de custos da produção.

---

# Documentação

Os arquivos relacionados à documentação e apresentação do projeto estão disponíveis na pasta `docs/`.

Entre os materiais estão:

* Banner científico/acadêmico;
* Diagrama C4;
* Imagens utilizadas na documentação.

---

# Equipe

**Emanuelle Cassol de Souza Godinho**
**Luana Lopes Reis**
**Pedro Manoel Rebelo Seti**

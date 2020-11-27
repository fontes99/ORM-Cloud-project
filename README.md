# ORM-Cloud-project
Este projeto consiste em um sistema de gerenciamento de tarefas ORM multi-cloud.

## Antes de tudo
Este projeto mexe com a *Amazon Web Services* (AWS), então, antes de tudo, é necessário configurar suas credenciais AWS. Além disso, é necessário instalar a biblioteca `boto3`.

A seção quickstart da documentação do `boto3` mostra como configura-lo. Siga os passos da documentação antes de começar.

# Estrutura de arquivos
```
config_scripts
├── configApp.sh
├── configDB.sh
└── configDJ.sh
src
├── client.py
└── misc.py
install.sh
main.py
pedro.py
task-list
README.md
```

# Como rodar

Para rodar o projeto, basta executar o arquivo `install.sh`

```bash
./install.sh
```

Para configurar o cliente `task-list` corretamente, é preciso fornecer a senha do superuser, porque são enviados dois arquivos para `/usr/bin/`

# Client

Depois de instalado. o projeto disponibilizará um client para gerenciar suas tarefas.

```bash
task-list
```

Para postagem de task, utilize o método `post` e preencha os campos.

OBS: a data precisa estar no formato (dd/mm/aaaa)
```bash
task-list post
```

Para listar todas as tasks, utilize o método `list`
```bash
task-list list
```
# Sobre

Investint é uma aplicação para análise de companhias brasileiras
de capital aberto registradas na CVM. A aplicação permite extrair
dados de arquivos FCA, DFP e ITR para armazená-los num banco de
dados, para que sejam então exibidos numa interface gráfica.

O banco de dados utilizado pela aplicação pode ser tanto um arquivo
SQLite3 ou um banco de dados SQL remoto, tal como MySQL e PostgreSQL.

# Instalação

A aplicação foi desenvolvida na linguagem Python, versão 3.7.
Certifique-se de que os executáveis da linguagem Python para a
versão 3.7 ou superior estão instalados antes de continuar para
as próximas etapas.

Faça uma cópia local deste repositório:

```sh
> git clone https://github.com/callmegiorgio/Investint.git
```

Opcionalmente, crie um ambiente virtual:

```sh
> python -m venv investint_env
> investint_env/Scripts/activate
```

Instale as dependências de código:

```sh
> pip install -r requirements.txt
```

Execute a aplicação:

```sh
> python -m investint
```

Ou passando um banco de dados SQLite3 como argumento:

```sh
> python -m investint 'db.sqlite3'
```

Para desativar a verbosidade dos comandos de banco de dados,
passe o parâmetro `-O`:

```sh
> python -O -m investint
```

# Compilação

Uma vez que tenha seguido as etapas da [seção anterior](#instalação),
instale PyInstaller:

```sh
> pip install pyinstaller
```

Crie uma cópia congelada do pacote `investint`, que será salvo em `build/lib/investint`:

```sh
> python setup.py build
```

Compile os arquivos em `build/lib/investint` para um executável em modo release:

```sh
> python -O -m PyInstaller .spec
```

Ou em modo debug:

```sh
> python -m PyInstaller .spec
```

Uma vez que a compilação termine, o arquivo executável `Investint` (ou `Investint.exe`)
deve existir no diretório `dist/debug` ou `dist/release`.
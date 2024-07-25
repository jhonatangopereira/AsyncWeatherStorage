# Async Weather Storage

Este documento descreve como configurar, rodar e testar um projeto FastAPI utilizando Docker e Docker Compose.

## Pré-requisitos

- Docker
- Docker Compose

## Instalação do Docker

### No Windows

1. Baixe o Docker Desktop para Windows no [site oficial do Docker](https://www.docker.com/products/docker-desktop).
2. Execute o instalador e siga as instruções na tela.
3. Após a instalação, inicie o Docker Desktop a partir do menu Iniciar.

### No macOS

1. Baixe o Docker Desktop para macOS no [site oficial do Docker](https://www.docker.com/products/docker-desktop).
2. Abra o arquivo .dmg e arraste o ícone do Docker para a pasta Aplicativos.
3. Inicie o Docker Desktop a partir do Launchpad.

### No Linux

Para distribuições baseadas em Debian/Ubuntu:

```bash
sudo apt-get update
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker

# Verifique a instalação
docker --version
```

## Estrutura do Projeto

A estrutura do projeto é a seguinte:

```lua
/your_project
|-- /app
|   |-- __init__.py
|   |-- main.py
|   |-- cities_reader.py
|-- requirements.txt
|-- Dockerfile
|-- Dockerfile.test
|-- docker-compose.yml
|-- test_app.py
```

## Configuração e Execução do Projeto

### Passo 1: Construir os contêineres

Na raiz do projeto, execute:

```bash
docker-compose build
```

### Passo 2: Iniciar o MongoDB e o serviço FastAPI

```bash
docker-compose up -d mongo app
```

### Passo 3: Verificar o funcionamento do serviço

Acesse `http://localhost:8000` no seu navegador. Você deve ver a documentação interativa do Swagger para a API.

## Execução dos Testes

### Passo 4: Rodar os testes

```bash
docker-compose run test
```

### Passo 5: Derrubar os contêineres

Após finalizar os testes, você pode derrubar os contêineres com o comando:

```bash
docker-compose down
```

## Notas Finais

Este projeto utiliza o FastAPI para criar uma API simples que coleta dados de clima de uma API externa e os armazena no MongoDB. Os testes são automatizados utilizando pytest e executados em um contêiner Docker separado.

Sinta-se à vontade para modificar e expandir este projeto conforme necessário para atender às suas necessidades específicas.

Trabalhar com PDF quase nunca é tão simples quando deveria ser. Toda vez que alguém aparece com um problema que envolve coletar dados de arquivos em PDF uma pequena fada cai morta em algum lugar.

O sofrimento não é com PDFs gerados digitalmente, para esses existem inúmeras soluções muito mais simples do que a tratada nesse texto. Porém quando precisamos consumir arquivos escaneados ou fotos transformadas em PDF, usar alguma tecnologia de OCR se torna uma ideia cada vez mais tentadora.

Azure Functions, AWS Lambda, GCP Cloud Functions são incríveis, muitas vezes parecem até boas de mais para serem verdade. É muito satisfatório fazer um projeto inteiro sem precisar se preocupar muito com a infraestrutura e todas as chatices que tradicionalmente estão associadas com a implementação.

Apesar de ser barato e simples, o serviço padrão muitas vezes deixa a desejar em personalização. Porém existe um meio termo, ao trocar da camada Serverless para um host dedicado usando containers, é possível criar o seu próprio ambiente do Azure Functions com bibliotecas e ferramentas que desejar.

Pensando em ampliar a funcionalidade do Azure Functions, construí uma imagem adicionando suporte ao Tesseract OCR e Poppler para permitir a transformação e leitura de fotos ou PDFs.

##Construindo a imagem

###Clonando repositório

No repositório abaixo esta tudo que é necessário para transformar um pdf em imagem e fazer a leitura do texto com OCR.
```
git clone https://github.com/sterndavi/Azure-Functions-Tesseract-Dockerfile.git
```

```
C:.
│   .gitignore
│   Dockerfile
│   host.json
│   readme.md
│   requirements.txt
│
├───.vscode
│       extensions.json
│
└───tesseract-teste
        function.json
        __init__.py
```
Com exceção do Dockerfile, todos os arquivos do repositório são idênticos ao padrão que são criados quando inicializamos um Function App pelo VS Code.

###Dockerfile

Agora finalmente vamos à estrela do nosso projeto, o arquivo de definição do ambiente.

Usamos como base a imagem do Azure Functions fornecida pela Microsoft. Em cima dela, instalamos Tesseract e Poppler, que são todos os pacotes e programas necessários.

```
# 0. imagem base do functions
FROM mcr.microsoft.com/azure-functions/python:4-python3.10

# 1. instalar Poppler para transformar pdfs em imagens com o Pdf2image
RUN apt-get update \
    && apt-get -y install poppler-utils \
    && apt-get clean

# 2. instalar o Tesseract em português
RUN apt-get update \
    && apt install tesseract-ocr-por -y

# 3. copiar o diretorio da function para imagem
COPY . /home/site/wwwroot

# 4. instalar os outros pacotes listados no requirements.txt
RUN cd /home/site/wwwroot && \
    pip install -r requirements.txt
```

Nesta imagem temos tudo que é necessário para transformar um pdf em texto usando OCR. Vale ressaltar que para situações mais desafiadoras, o ImageMagick seria uma ótima adição.

###Código de exemplo

Para testar a funcionalidade, preparei no repositório uma pequena função que serve como proof of concept.

A função abaixo usa um gatilho HTTP que toma como parâmetro a URL de um PDF qualquer, lê o seu conteúdo usando OCR e retorna o texto extraído para o client.

```
import logging
import azure.functions as func
import pytesseract as pt
import requests
import tempfile
import pdf2image as p2i

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request')

    url_pdf = req.params.get('pdf_url')

    temp = tempfile.gettempdir()

    file = requests.get(url_pdf).content

    with open(f'{temp}/pdf_file.pdf', 'wb') as foto:
        foto.write(file)
        foto.close()

    p2i.convert_from_path(
        f'{temp}/pdf_file.pdf',
        500,
        output_folder = f"{temp}",
        output_file = "pdfphoto"
        )

    image_t_string = pt.image_to_string(
        f"{temp}/pdfphoto0001-1.ppm", lang= "por", 
        )

    return func.HttpResponse(
             str(image_t_string),
             status_code=200
    )
```

##Implementação
###Pré-requisitos locais

   - Docker Desktop (docs);
   - Azure CLI (docs, ou ‘winget install “Azure CLI” ’ no Powershell);
   - Algum editor de texto.

###Pré-requisitos Azure

   - Azure Container Registry (É possível dar deploy pelo Github e pelo Docker Hub também);
   - Function App (Configurado para docker e utilizando algum app service plan);
   - Azure Storage Account (Obrigatório para criação do Function app).

###Executando a implementação

Para colocarmos nossa imagem dentro do Function App precisamos primeiro colocar a imagem no Container Registry.

Isso é possível usando o seguinte script com Azure CLI:
```
$acr_url = "<url do seu container registry>" # url do container registry
docker login $acr_url -u <usuário-do-container-registry> -p <senha-do-container-registry> #disponivel na aba de access keys do recurso
docker build --tag $acr_url/tesseract . # Construir a imagem
docker push $acr_url/tesseract:latest # Empurrar imagem pro registry
```

Depois de feito o upload da imagem para seu Container Registry, o último passo é ir no Function App na aba de Deployment Center e configurar as opções de implementação de acordo com a imagem que acabou de fazer upload.

Salvo as configurações, dentro de 5 minutos o seu Function app com Tesseract estará pronto para ser usado.

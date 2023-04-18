import requests
import mmh3
import webbrowser
import argparse
import codecs
import urllib.parse

# Importa a chave de API do Shodan
API_KEY = "CV4QjVBJ7FLw8YjTiKyLNRrOVEvpig1g"

# Configura o parser de argumentos
parser = argparse.ArgumentParser()
parser.add_argument("url", help="URL da página da web")
args = parser.parse_args()

# Adiciona o esquema padrão se não estiver presente na URL
parsed_url = urllib.parse.urlparse(args.url)
if not parsed_url.scheme:
    args.url = "https://" + args.url

# Solicita a página e extrai o conteúdo
response = requests.get(args.url)
response.encoding = response.apparent_encoding
html = response.content.decode(response.encoding)

# Encontra a URL do favicon
favicon_url = ""
for line in html.splitlines():
    if "rel=\"icon\"" in line:
        start = line.find("href=") + 6
        end = line.find("\"", start)
        favicon_url = line[start:end]
        break
    elif "link rel=\"shortcut icon\"" in line:
        start = line.find("href=") + 6
        end = line.find("\"", start)
        favicon_url = line[start:end]
        break

# Verifica se encontrou o favicon, se não tenta buscar em /favicon.ico
if not favicon_url:
    favicon_response = requests.get(args.url + "/favicon.ico")
    if favicon_response.status_code == 200:
        favicon_url = args.url + "/favicon.ico"

# Obtém o conteúdo do favicon e calcula o MurmurHash3
if favicon_url:
    favicon_response = requests.get(favicon_url, verify=False)
    favicon_content = favicon_response.content
    favicon_base64 = codecs.encode(favicon_content, 'base64')
    favicon_hash = mmh3.hash(favicon_base64)
    print("MurmurHash3 do favicon encontrado: {}".format(favicon_hash))
else:
    print("Favicon não encontrado.")
    favicon_hash = None

# Faz a consulta no Shodan
if favicon_hash:
    webbrowser.open(f"https://www.shodan.io/search?query=http.favicon.hash%3A{favicon_hash}")
    shodan_url = f"https://api.shodan.io/shodan/host/search?key={API_KEY}&query=http.favicon.hash%3A{favicon_hash}"
    response = requests.get(shodan_url)
    if response.status_code == 200:
        results = response.json()
        if results["total"] > 0:
            print("Foram encontrados {} resultados no Shodan para o hash {}.".format(results["total"], favicon_hash))
        else:
            print("Não foram encontrados resultados no Shodan para o hash {}.".format(favicon_hash))
    else:
        print("Não foi possível obter os resultados do Shodan.")
else:
    print("Não foi possível fazer a consulta no Shodan.")


import http.server
import socketserver
from urllib.parse import urlparse
import json

def open_file(filename):
    with open(filename, 'r') as f:
        mensaje = f.read()
        f.close()
    return mensaje

def search(busqueda= '', query='', object = '', limite='10'):
    resultados = []
    headers = {'User-Agent': 'http-client'}
    conn = http.client.HTTPSConnection("api.fda.gov")
    conn.request("GET", "/drug/label.json?search="+ busqueda+":"+ query +'&limit='+ limite , None, headers)
    r1 = conn.getresponse()
    print(r1.status, r1.reason)
    repos_raw = r1.read().decode("utf-8")
    conn.close()
    repos = json.loads(repos_raw)
    if 'error' in repos.keys():
        resultados.append(repos['error']['message'])
    else:
        for i in range(int(limite)):
            try:
                resultados.append(repos['results'][i]['openfda'][object][0])
            except KeyError:
                resultados.append('Desconocido')
    return resultados


def lists(object = '', limite='10'):
    resultados = []
    headers = {'User-Agent': 'http-client'}
    conn = http.client.HTTPSConnection("api.fda.gov")
    conn.request("GET", "/drug/label.json?limit="+ limite , None, headers)
    r1 = conn.getresponse()
    print(r1.status, r1.reason)
    repos_raw = r1.read().decode("utf-8")
    conn.close()
    repos = json.loads(repos_raw)
    if object:
        for i in range(int(limite)):
            try:
                resultados.append(repos['results'][i]['openfda'][object][0])
            except KeyError:
                resultados.append('Desconocido')
        return resultados
    else:
        return repos
def pagina_resultados(lista):
    mensaje = """
        <!doctype html>
        <html>
          <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
            <title>RESULTADOS DE LA BUSQUEDA:</title>
          </head>
           <body style='background-color: 63B7B6'>
              <h1 style="text-align:center">Resultados:</h1>
        """
    for i in range(len(lista)):
        mensaje += "<li>{}</li>\n".format(lista[i])


    mensaje+="""
           </body>
        </html>"""
    return mensaje
def error_404():
    mensaje = """<!doctype html>
    <html>
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <title>RESULTADOS DE LA BUSQUEDA:</title>
      </head>
       <body style='background-color: 63B7B6'>
          <h1>Error 404:</h1>
          <p> Recurso no encontrado </p>
       </body>
    </html>
          """

    return mensaje
# -- IP and the port of the server
IP = "localhost"  # Localhost means "I": your local machine
PORT = 8000
socketserver.TCPServer.allow_reuse_address = True

# HTTPRequestHandler class
class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    # GET
    def do_GET(self):
        # Send response status code
        flag = True
        if flag:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
        # Send headers


        # Send message back to client
        if self.path == '/':
            mensaje = open_file('pag_principal.html')
            self.wfile.write(bytes(mensaje, "utf8"))
        elif self.path == '/searchDrug':
            mensaje = open_file('formulario.html')
            self.wfile.write(bytes(mensaje, "utf8"))
        elif self.path == '/searchCompany':
            mensaje = open_file('empresas.html')
            self.wfile.write(bytes(mensaje, "utf8"))
        elif self.path == '/listDrugs':
            mensaje = open_file('listadroga.html')
            self.wfile.write(bytes(mensaje, "utf8"))
        elif self.path == '/listCompanies':
            mensaje = open_file('listacomp.html')
            self.wfile.write(bytes(mensaje, "utf8"))
        elif self.path == '/listWarnings':
            mensaje = open_file('listawarn.html')
            self.wfile.write(bytes(mensaje, "utf8"))
        elif self.path == '/secret':
            flag = False
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Hola"')
            self.end_headers()
        elif self.path == '/redirect':
            flag = False
            self.send_response(302)
            self.send_header('Location', 'http://localhost:' + str(PORT))
            self.end_headers()



        elif '?' in self.path:
            query = urlparse(self.path).query
            query_components = dict(qc.split('=') for qc in query.split('&'))
            if not query_components['limit']:
                query_components['limit'] = '10'

            if 'searchDrug' in self.path:
                resultados = search(busqueda ='active_ingredient', query = query_components['name'], object = 'brand_name', limite = query_components['limit'])
            elif 'searchCompany' in self.path:
                resultados = search(busqueda ='openfda.manufacturer_name', query = query_components['name'], object = 'manufacturer_name', limite = query_components['limit'])


            elif 'listDrugs' in self.path:
                resultados = lists(object = 'brand_name', limite = query_components['limit'])

            elif 'listCompanies' in self.path:
                resultados = lists(object = 'manufacturer_name', limite = query_components['limit'])

            elif 'listWarnings' in self.path:
                resultados = []
                info = lists(limite = query_components['limit'])
                for i in range(int(query_components['limit'])):
                    try:
                        resultados.append(info['results'][i]['warnings'][0])
                    except KeyError:
                        resultados.append('Desconocido')

            mensaje = pagina_resultados(resultados)
            self.wfile.write(bytes(mensaje, "utf8"))
        else:
            flag = False
            self.send_response(404)
            mensaje = error_404()
            self.wfile.write(bytes(mensaje, "utf8"))



        print("File served!")
        return

Handler = testHTTPRequestHandler

httpd = socketserver.TCPServer((IP, PORT), Handler)
print("serving at port", PORT)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
        pass

httpd.server_close()
print("")
print("Server stopped!")

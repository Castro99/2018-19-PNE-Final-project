import socketserver, http.server, requests, termcolor, json, sys
import traceback
from Seq import Seq

PORT = 8000

host = 'http://rest.ensembl.org'
URL = ["/info/species?", "/info/assembly", "/lookup/symbol/homo_sapiens/" "/overlap/region/human/{}:{}-{}?feature=gene",
             "/xrefs/symbol/homo_sapiens/{}", "/sequence/id/{}?expand=1"]
headers = {"Content-Type": "application/json"}

socketserver.TCPServer.allow_reuse_address = True

# this is the future html file that will be sent to the client
# It has blank spaces that will be filled later

with open('template.html', 'r') as f:
    template: str = f.read()

with open('Error.html', 'r') as f:
    templateError: str = f.read()


class TestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):

        termcolor.cprint(self.requestline, 'green')
        resource = self.path
        list_resource = resource[1:resource.find('?')]

        print(list_resource)

        try:
            if resource == '/':

                # HTTP Response
                resp = 200
                # The title of the html file is different in each case
                title = 'GENOME'
                h = 'Information for the human and other vertebrates genome'

                # This is the first html file that is sent to the client
                with open('home.html', 'r') as f:
                    content = f.read()

                # Include the information in the future html response text
                info = template.format(title, title, h, content)

            elif list_resource == 'listSpecies':

                resp = 200
                # Process the client's request using the request module
                link = host + URL[0]
                r = requests.get(link, headers=headers)
                json_code = r.json()

                # Limit to the length of the list selected by the user
                try:
                    if 'json=1' in resource:
                        # In case that the user hasn't introduced any limit while writing the URL in the browser
                        # otherwise, the limit will be established at 1
                        if 'limit' not in resource:
                            limit = len(json_code['species'])
                        else:
                            limit = resource.split('=')[1].split('&')[0]
                    else:
                        limit = resource.split('=')[1]
                # In case that the user hasn't introduced any limit while writing the URL in the browser
                except IndexError:
                    limit = len(json_code['species'])

                # If there is no limit entered, the limit used will be the species' list's length
                if limit == '':
                    limit = len(json_code['species'])

                add = ''
                dictionary = {}
                limit_passed = False

                if int(limit) > 199:
                    add += '<div class="alert alert-danger" role="alert"><h4 class="alert-heading">You surpass the maximun length of 199</h4>Maximun of species</div>'
                    limit = 199
                    limit_passed = True

                add += '<table class="table"><thead><tr><th scope="col">Species name</th><th scope="col">Normal name</th></tr></thead><tbody>'

                for i in range(int(limit)):

                    # I add the information in form of a string in case the user wants it like that and in form of a
                    # dictionary if the user wants a json
                    common = json_code['species'][i]['common_name']
                    #add += 'Species name: {} \nNormal name: {}\n\n'.format(json_code['spe'][i]['name'], normal)
                    add += '<tr><td>{}</td><td>{}</td></tr>'.format(json_code['species'][i]['name'], common)
                    dictionary.update([(str(i+1), {'common_name': common, 'scientific_name': json_code['species'][i]['name']})])

                add += '</tbody></table>'

                if limit_passed:
                    dictionary.update([('0', {'You surpass the maximun length of 199'})])

                # The title of the html file is different in each case
                title = 'Species'
                h = 'Available species on the database'

                # Include the information in the future html response text
                info = template.format(title, title, h, add)

            elif list_resource == 'karyotype' :

                resp = 200
                if 'json=1' in resource:
                    specie = resource.split('=')[1].split('&')[0]
                else:
                    specie = resource.split('=')[1]

                link = host + URL[1] + '/' + specie + "?"
                r = requests.get(link, headers=headers)

                # In case that the species' name is not on the database
                # the client will receive a response message indicating so
                dictionary = {}
                if r.ok:
                    json_code = r.json()
                    add = ''

                    if not json_code['karyotype']:
                        add = "Karyotipe not found"
                        dictionary.update([('Error', 'Karyotype not found')])
                    else:
                        add += '<div class="col-6">'
                        add += '<table class="table"><thead><tr><th scope="col">#</th><th scope="col">Chromosome</th></tr></thead><tbody>'

                        for i, code in enumerate(json_code['karyotype']):
                            #add += 'Chromosome number {}: {}\n'.format(str(i + 1), code)
                            add += '<tr><td>{}</td><td>{}</td></tr>'.format(str(i + 1), code)
                            dictionary.update([(str(i), code)])

                        add += '</tbody></table>'
                        add += '</div>'
                else:
                    add = 'Species name {} not found ""'.format(specie)
                    dictionary.update([('NOT FOUND', 'Species {} name not found'.format(specie))])

                # Like before, I include the title myself
                title = 'Karyotype'
                h = 'karyotype of {}'.format(resource.split('=')[1])
                info = template.format(title, title, h, add)

            elif list_resource == 'chromosomeLength':

                resp = 200
                # In this case, I receive two mandatory endpoints: "species" and "chromo"
                if 'json=1' in resource:
                    specie = resource.split('&')[0].split('=')[1].split('&')[0]
                    chromo = resource.split('&')[1].split('=')[1].split('&')[0]
                else:
                    specie = resource.split('&')[0].split('=')[1]
                    chromo = resource.split('&')[1].split('=')[1]
                # Process the request
                link = host + URL[1] + '/' + specie + '/' + chromo + '?'
                r = requests.get(link, headers=headers)

                dictionary = {}
                if r.ok:
                    json_code = r.json()
                    add = json_code['length']
                    dictionary.update([('length', json_code['length'])])
                else:
                    add = 'Specie "{}" chromosome "{}" not found'.format(specie, chromo)
                    dictionary.update([('Error', 'Specie {} chromosome {} not found'.format(specie, chromo))])

                # Include the information in my future html file
                title = 'Chromosome length'
                h = 'Introduce specie {} & chromosome length {}'.format(specie, chromo)
                info = template.format(title,title, h, add)


            else:
                # In the case that I get an endpoint different from the ones I have decided to use,
                # the client receives an error message
                resp = 404
                info = template.format("Error 404", "Error 404", "Página no encontrada", templateError.format("Página no encontrada", resource))


        except Exception as e:
            print(str(e))
            # If an exception is raised, I send back an error message
            resp = 500
            # Include the information in the future html response text
            info = template.format("Error", "Error", "Error de la aplicación", templateError.format("Error de la aplicación", str(e) + '\n' + ''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))))


        # Inicio Respuesta servidor web

        # Write the information in a response html file
        d = open('Response.html', 'w')
        d.write(info)
        d.close()

        # Read the information from that response html file
        d = open('Response.html', 'r')
        content = d.read()
        d.close()

        content_type = 'text/html'

        if 'json=1' in resource and resp == 200:
            content_type = 'application/json'
            content = dictionary

        # Send the headers and the response html
        self.send_response(resp)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', len(str.encode(content)))
        self.end_headers()

        self.wfile.write(str.encode(content))

        # Fin Respuesta servidor web


Handler = TestHandler

# Open the socket server
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Serving at PORT: ", PORT)

    # Main loop: Attend the client. Whenever there is a new
    # client, the handler is called
    try:
        httpd.serve_forever()
    except Exception as e:
            print(str(e))
    except KeyboardInterrupt:
        print("")
        print("Stoped by the user")
        httpd.server_close()

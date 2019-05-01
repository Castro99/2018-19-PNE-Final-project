import socketserver, http.server, requests, termcolor, json, sys
import traceback
from Seq import Seq

PORT = 8000

host = 'http://rest.ensembl.org'
URL = ["/info/species?", "/info/assembly", "/lookup/symbol/homo_sapiens/" "/overlap/region/human/{}:{}-{}?feature=gene",
             "/xrefs/symbol/homo_sapiens/{}", "/sequence/id/{}?expand=1"]
headers = {"Content-Type": "application/json"}

socketserver.TCPServer.allow_reuse_address = True

# We open the template where our results will be provided and also we open the error
#Both of them are just HTML files but they only have a call to a function that will be develop while running the server

with open('template.html', 'r') as f:
    template: str = f.read()

with open('Error.html', 'r') as f:
    templateError: str = f.read()

#Basic structure from Lesson 17 of JSON & API
# Class with our Handler. It is a called derived from BaseHTTPRequestHandler
# It means that our class inheritates all his methods and properties
class TestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        """This method is called whenever the client invokes the GET method
                in the HTTP protocol request"""

        # Print the request line
        termcolor.cprint(self.requestline, 'green')
        #Parser the path
        resource = self.path
        list_resource = resource[1:resource.find('?')]
        #Just to see if it working we will print the list_resource
        print(list_resource)

        try:
            if resource == '/':

                # --OK RESPONSE
                resp = 200
                # We define the title and header that will later be place in the template html
                title = 'GENOME'
                h = 'Information for the human and other vertebrates genome'

                # Will open the home html (Index) were the user must operate
                with open('home.html', 'r') as f:
                    content = f.read()

                # We fill the template html with the title and header previously define
                info = template.format(title, title, h, content)

            # --Perform of List species parameter
            elif list_resource == 'listSpecies':

                resp = 200
                # We established the connection between our project and the web page where all the information comes out
                link = host + URL[0]
                r = requests.get(link, headers=headers)
                json_code = r.json()

                # Now we develop the code if the user wants to limit the list (OPTIONAL) and other possible results
                try:
                    if 'json=1' in resource:

                        if 'limit' not in resource:
                            limit = len(json_code['species'])
                        else:
                            limit = resource.split('=')[1].split('&')[0]
                    else:
                        limit = resource.split('=')[1]

                except IndexError:
                    limit = len(json_code['species'])

                if limit == '':
                    limit = len(json_code['species'])

                # We will pick all the species print on the list and introduce in an array
                add = ''
                dictionary = {}
                limit_passed = False
                # Now we estblished the limit
                if int(limit) > 199:
                    # We develop and alert using bootstrap structure
                    add += '<div class="alert alert-danger" role="alert"><h4 class="alert-heading">You surpass the maximun length of 199</h4>Maximun of species</div>'
                    limit = 199
                    limit_passed = True
                    # We will intoduce our result with the form of a table
                add += '<table class="table"><thead><tr><th scope="col">Scientific name</th><th scope="col">Comman name</th></tr></thead><tbody>'

                for i in range(int(limit)):

                    # We perform our variables in the form of a table and introduce it in a dictionary (JSON)
                    common = json_code['species'][i]['common_name']
                    # We will intoduce our result with the form of a table
                    add += '<tr><td>{}</td><td>{}</td></tr>'.format(json_code['species'][i]['name'], common)
                    dictionary.update([(str(i+1), {'common_name': common, 'scientific_name': json_code['species'][i]['name']})])

                add += '</tbody></table>'
                #In the case you surpass the established limit you will be notified
                if limit_passed:
                    dictionary.update([('0', {'You surpass the maximun length of 199'})])
                # We define the title and header that will later be place in the template html
                title = 'Species'
                h = 'Available species on the database'
                # We fill the template html with the title and header previously define
                info = template.format(title, title, h, add)
            # --Perform of Chromosome length parameter
            elif list_resource == 'chromosomeLength':
                # --OK RESPONSE
                resp = 200
                # We define the variable specie and chromo for both outputs depending on what of them the user pick
                if 'json=1' in resource:
                    specie = resource.split('&')[0].split('=')[1].split('&')[0]
                    chromo = resource.split('&')[1].split('=')[1].split('&')[0]
                else:
                    specie = resource.split('&')[0].split('=')[1]
                    chromo = resource.split('&')[1].split('=')[1]
                # We established the connection between our project and the web page where all the information comes out (REQUEST)
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

                # We define the title and header that will later be place in the template html
                title = 'Chromosome length'
                h = 'Introduce specie {} & chromosome length {}'.format(specie, chromo)
                # We fill the template html with the title and header previously define
                info = template.format(title, title, h, add)

            # --Perform of Karyotipe parameter
            elif list_resource == 'karyotype' :
                #--OK RESPONSE
                resp = 200
                #We define the variable specie in booth cases depending on what of the two of them the user pick
                if 'json=1' in resource:
                    specie = resource.split('=')[1].split('&')[0]
                else:
                    specie = resource.split('=')[1]
                # We established the connection between our project and the web page where all the information comes out
                link = host + URL[1] + '/' + specie + "?"
                r = requests.get(link, headers=headers)

                # The user will be notified if the karyotipe of a specie is not found
                dictionary = {}
                if r.ok:
                    json_code = r.json()
                    add = ''

                    if not json_code['karyotype']:
                        add = "Karyotipe not found"
                        dictionary.update([('Error', 'Karyotype not found')])
                    else:
                        #Bootstrap structure to separate a row in two (col-6 half of a row)
                        add += '<div class="col-6">'
                        #Table for the chromosome and its number
                        add += '<table class="table"><thead><tr><th scope="col">Number(#)</th><th scope="col">Chromosome</th></tr></thead><tbody>'

                        for i, code in enumerate(json_code['karyotype']):
                            # Table with chromosome and its number
                            add += '<tr><td>{}</td><td>{}</td></tr>'.format(str(i + 1), code)
                            dictionary.update([(str(i), code)])
                        # We add the body of the table
                        add += '</tbody></table>'
                        add += '</div>'
                else:
                    # We perform our variables in the form of a table and introduce it in a dictionary (JSON)
                    add = 'Species name {} not found ""'.format(specie)
                    dictionary.update([('Warning', 'Species {} name not found'.format(specie))])

                # We define the title and header that will later be place in the template html
                title = 'Karyotype'
                h = 'karyotype of {}'.format(resource.split('=')[1])
                # We fill the template html with the title and header previously define
                info = template.format(title, title, h, add)

            elif list_resource == 'geneSeq':
                resp = 200
                if 'json=1' in resource:
                    gene = resource.split('=')[1].split('&')[0]
                else:
                    gene = resource.split('=')[1]
                link = host + URL[4].format(gene)
                dictionary = {}
                r = requests.get(link, headers=headers)

                json_code = r.json()
                id = json_code[0]['id']

                link = host + URL[5].format(id)
                r2 = requests.get(link, headers=headers)
                json_code2 = r2.json()

                add = json_code2['seq']
                dictionary.update([('sequence', json_code2['seq'])])

                title = 'Gene {} seq'.format(gene)
                h = 'Sequence of gene {}'.format(gene)
                info = template.format(title, title, h, add)

            elif list_resource == 'geneInfo':
                resp = 200
                if 'json=1' in resource:
                    gene = resource.split('=')[1].split('&')[0]
                else:
                    gene = resource.split('=')[1]
                link = host + URL[4].format(gene)
                dictionary = {}
                r = requests.get(link, headers=headers)

                json_code = r.json()
                id2 = json_code[0]['id']

                link = host + URL[5].format(id2)
                r2 = requests.get(link, headers=headers)
                json_code2 = r2.json()

                x = json_code2['desc'].split(':')
                chromo, start, end, id2, length = x[2], x[3], x[4], json_code2['id'], json_code2['id']

                add = "Start: {}\nEnd:{}\nLength: {}\nid: {}\nChromosome: {}".format(start, end, length, id2, chromo)
                dictionary.update(
                    [('start', start), ('end', end), ('length', length), ('id', id2), ('chromosome', chromo)])

                title = 'Gene {} inf'.format(gene)
                h = 'Information about gene {}'.format(gene)
                info = template.format(title, title, h, add)

            elif list_resource == 'geneCalc':
                resp = 200
                if 'json=1' in resource:
                    gene = resource.split('=')[1].split('&')[0]
                else:
                    gene = resource.split('=')[1]
                link = host + URL[4].format(gene)
                dictionary = {}
                r = requests.get(link, headers=headers)

                json_code = r.json()
                id3 = json_code[0]['id']

                link = host + URL[5].format(id3)
                r2 = requests.get(link, headers=headers)
                json_code2 = r2.json()

                seq = Seq(json_code2['seq'])
                length = seq.len()
                perc = [seq.perc('A'), seq.perc('C'), seq.perc('T'), seq.perc('G')]

                add = 'Length: {}\n  % A: {}%\n   % C: {}%\n  % T: {}%\n  % G: {}%'.format(
                    length, perc[0], perc[1], perc[2], perc[3])
                dictionary.update([('length', length), ('perc_A', perc[0] + '%'), ('perc_C', perc[1] + '%'),
                                   ("perc_T", perc[2] + '%'), ("perc_G", perc[3] + '%')])

                title = 'Gene {} calc'.format(gene)
                h = 'Calculations performed on gene {}'.format(gene)
                info = template.format(title, title, h, add)


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

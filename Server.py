import socketserver, http.server, requests, termcolor
import traceback
from Seq import Seq

PORT = 8000

host = 'http://rest.ensembl.org'
URLS = ["/overlap/region/human/{}:{}-{}?feature=gene","/xrefs/symbol/homo_sapiens/{}", "/sequence/id/{}?expand=1"]
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
                archive = template.format(title, title, h, content)

            # --Perform of List species parameter
            elif list_resource == 'listSpecies':

                resp = 200
                # We established the connection between our project and the web page where all the information comes out
                URL= "/info/species?"
                link = host + URL
                r = requests.get(link, headers=headers)
                json_code = r.json()

                # Now we develop the code if the user wants to limit the list (OPTIONAL) and other possible results
                try:
                    # We will take different ways depending of the json value
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

                # We will pick all the species print on the list and introduce in a dictionary
                add = ''
                dictionary = {}
                limit_passed = False
                # Now we estblished the limit
                if int(limit) > 199:
                    # We develop and alert using bootstrap structure
                    add += '<div class="alert alert-danger" role="alert"><h4 class="alert-heading">Maximun length of the list reached reached</h4>Maximun of species</div>'
                    limit = 199
                    limit_passed = True
                    # Now we perform a table the next add is just to establish the headers
                add += '<table class="table"><thead><tr><th scope="col">Scientific name</th><th scope="col">Comman name</th></tr></thead><tbody>'
                # We use a for in order to fulfil the information of every specie
                for i in range(int(limit)):

                    # We perform our variables in the form of a table and introduce it in a dictionary (JSON)
                    common = json_code['species'][i]['common_name']
                    # We will intoduce our result in the table with the next add
                    add += '<tr><td>{}</td><td>{}</td></tr>'.format(json_code['species'][i]['name'], common)
                    dictionary.update([(str(i+1), {'common_name': common, 'scientific_name': json_code['species'][i]['name']})])
                # We close the table
                add += '</tbody></table>'
                # In the case you surpass the established limit you will be notified
                if limit_passed:
                    dictionary.update([('0', {'You surpass the maximun length of 199'})])
                # We define the title and header that will later be place in the template html
                t = 'Species'
                head = 'Available species on the database'
                # We fill the template html with the title and header previously define
                archive = template.format(t, t, head, add)
            # --Perform of Chromosome length parameter
            elif list_resource == 'chromosomeLength':
                # --OK RESPONSE
                resp = 200
                # We define the variable specie and chromo for both outputs depending on what of them the user pick (Based on JSON values)
                if 'json=1' in resource:
                    specie = resource.split('&')[0].split('=')[1].split('&')[0]
                    chromo = resource.split('&')[1].split('=')[1].split('&')[0]
                else:
                    specie = resource.split('&')[0].split('=')[1]
                    chromo = resource.split('&')[1].split('=')[1]
                # We established the connection between our project and the web page where all the information comes out (REQUEST)
                URL = "/info/assembly"
                link = host + URL + '/' + specie + '/' + chromo + '?'
                r = requests.get(link, headers=headers)

                dictionary = {}
                if r.ok:
                    # We introduce the headers of the table where are results will be post
                    add = '<table class="table"><thead><tr><th scope="col">Length</th></tr></thead><tbody>'
                    json_code = r.json()
                    # We complete the table with the length
                    add +='<tr><td>{}</td></tr>'.format(json_code['length'])
                    dictionary.update([('length', json_code['length'])])
                else:
                    add = 'Specie "{}" chromosome "{}" not found'.format(specie, chromo)
                    dictionary.update([('Error', 'Specie {} chromosome {} not found'.format(specie, chromo))])

                # We define the title and header that will later be place in the template html
                t = 'Chromosome length'
                head = 'Introduce specie {} & chromosome length {}'.format(specie, chromo)
                # We fill the template html with the title and header previously define
                archive = template.format(t, t, head, add)

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
                URL = "/info/assembly"
                link = host + URL + '/' + specie + "?"
                r = requests.get(link, headers=headers)

                # The user will be notified if the karyotipe of a specie is not found
                dictionary = {}
                if r.ok:
                    json_code = r.json()
                    add = ''

                    if not json_code['karyotype']:
                        add = "Karyotype not found"
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
                t = 'Karyotype'
                head = 'karyotype of {}'.format(resource.split('=')[1])
                # We fill the template html with the title and header previously define
                archive = template.format(t, t, head, add)
            # --Perform of geneSeq parameter
            elif list_resource == 'geneList':
                #--OK RESPONSE

                resp = 200

                # We declared the variables (Its the same process as the one in chromosomeLength
                chromo = resource.split('&')[0].split('=')[1]
                start_point = resource.split('&')[1].split('=')[1]
                end_point = resource.split('&')[2].split('=')[1]

                # We established the connection between our project and the web page where all the information comes out
                link = URLS[0].format(chromo, start_point, end_point)
                dictionary = {}
                # I performed it with the try and except due to the previous declarations of the variables chromo, start_point & end_point
                try:
                    r = requests.get(host + link, headers=headers)
                    # Connection with the server
                    json_code = r.json()
                    add = ''
                    # Table for the Gene Number  and its Name
                    if list_resource == 'geneList':
                        add = '<table class="table"><thead><tr><th scope="col">Gene Number </th><th scope="col">External Name</th></tr></thead><tbody>'
                        for i in range(len(json_code)):
                            # Table with the Gene number and its Name
                            add += '<tr><td>{}</td><td>{}</td></tr>'.format(i, json_code[i]['external_name'])
                            dictionary.update([(str(i), json_code[i]['external_name'])])
                # As we use the 'TRY' we need and except or finally so i select the except and use it to perform the error
                except Exception:
                    add = 'No genes located in chromosome {} from start point {} & end point{}'.format(chromo, start_point, end_point)
                    dictionary.update([('WARNING', 'No genes located in chromosome {} from start point {} & end point{}'.format(chromo, start_point, end_point))])
                # We established a title for our template.html in case it is valid
                t = 'List of Genes'
                # We established a head for our template.html in case it is valid
                head = 'Gene list of chromosome {} from {} to {}'.format(chromo, start_point, end_point)
                archive = template.format(t,t, head, add)
            # --Perform of geneSeq parameter
            elif list_resource == 'geneSeq':
                #--OK RESPONSE
                resp = 200
                # We established different development for ex depending on the json value
                if 'json=1' in resource:
                    ex = resource.split('=')[1].split('&')[0]
                else:
                    ex = resource.split('=')[1]
                # We established the connection between our project and the web page where all the information comes out
                link1 = (host + URLS[1].format(ex))
                dictionary = {}
                #I performed it with the try and except due to the previous declarations of the variable ex
                try:
                    #Connection with the server (with ID)in order to be able to search Info
                    r = requests.get(link1, headers=headers)
                    json_code = r.json()
                    id = json_code[0]['id']

                    # We made it another time but this time with the intention of finding the request Info
                    link2 = (host + URLS[2].format(id))
                    r1 = requests.get(link2, headers=headers)
                    json_code1 = r1.json()

                    # As previously i perform the parameter  with try i have to use one 'IF' in this case with the parameter 'geneSeq' another time
                    if list_resource == 'geneSeq':
                        # We develop a table with only one head (SEQUENCE)
                        add = '<table class="table"><thead><tr><th scope="col">SEQUENCE</th></tr></thead><tbody>'
                        # Now we introduce the result in the table using another time the add
                        add +='<tr><td>{}</td></tr>'.format(json_code1['seq'])

                        dictionary.update([('sequence', json_code1['seq'])])
                        # We established a title for our template.html in case it is valid
                        t = 'Gene Sequence'
                        # We established a header for our template.html in case it is valid
                        head = 'Sequence of {}'.format(ex)


                # As we use the 'TRY' we need and except or finally so i select the except and use it to perform the error
                except Exception:
                    # We introduce what we want to introduce in the main part of our template.html in the case the gene enter is not valid and store it in a dictionary
                    add = 'No Gene {} Found'.format(ex)
                    dictionary.update([('WARNING', 'No Gene {} Found'.format(ex))])
                    # Give a title to the template.html in case of error
                    t = 'ERROR'
                    # Give a header to the template.html in case of error
                    head = 'Sequence of {} NOT FOUND!!!!!'.format(ex)
                archive = template.format(t,t, head, add)
            #--Perform of geneCalc parameter (Practically the same as the previous parameter)
            elif list_resource == 'geneCalc':
                #--OK RESPONSE
                resp = 200
                # We established different development for ex depending on the json value
                if 'json=1' in resource:
                    ex = resource.split('=')[1].split('&')[0]
                else:
                    ex = resource.split('=')[1]
                # We established the connection between our project and the web page where all the information comes out
                link1 = (host + URLS[1].format(ex))
                dictionary = {}

                try:
                    r = requests.get(link1, headers=headers)
                    #Connection with the server (with ID)in order to be able to search Info
                    json_code = r.json()
                    id = json_code[0]['id']

                    # We made it another time but this time with the intention of finding the request Info
                    link2 = (host + URLS[2].format(id))
                    r1 = requests.get(link2, headers=headers)
                    json_code1 = r1.json()
                    # We need at least one 'IF' so we use another time the variable 'geneCalc'
                    if list_resource == 'geneCalc':
                        # We import different function develop in the Seq.py and then when we introduce a correct gene it gives us the length and each percentage
                        seq = Seq(json_code1['seq'])
                        length = seq.len()
                        percentage = [seq.percentage('A'), seq.percentage('C'), seq.percentage('T'), seq.percentage('G')]
                        # Now we perform a table in the first add we introduce the headers and in the second is where our result will be post
                        add = '<table class="table"><thead><tr><th scope="col">LENGTH</th><th scope="col">A (%)</th><th scope="col">C (%)</th><th scope="col">T (%)</th><th scope="col">G (%)</th></tr></thead><tbody>'
                        add += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(length, percentage[0],percentage[1],percentage[2], percentage[3])
                        dictionary.update([('length', length), ('perc_A', percentage[0] + '%'), ('perc_C', percentage[1] + '%'),("perc_T", percentage[2] + '%'), ("perc_G", percentage[3] + '%')])
                        # Title in the case the gene introduce is valid(of template.html)
                        t = 'Gene Calculations'.format(ex)
                        # Header in the case the gene introduce is valid(of template html)
                        head = 'Calculations performed on gene {}'.format(ex)


                # If the gene t is noy in data base (we use it to perform the error
                except Exception:
                    # We introduce what we want to introduce in the main part of our template html in the case the gene enter is not valid and store it in a dictionary
                    add = 'No Gene {} Found'.format(ex)
                    dictionary.update([('WARNING', 'No Gene {} Found'.format(ex))])
                    # Give a title to the template.html in case of error
                    t = 'ERROR'
                    # Give a header to the template.html in case of error
                    head = 'Sequence of {} NOT FOUND!!!!!'.format(ex)
                archive = template.format(t, t, head, add)

            #--Perform of geneInfo parameter
            # Nearly the same as the previous ones
            elif list_resource == 'geneInfo':
                #--OK RESPONSE
                resp = 200
                # We established different development for ex depending on the json value
                if 'json=1' in resource:
                    ex = resource.split('=')[1].split('&')[0]
                else:
                    ex = resource.split('=')[1]
                # We established the connection between our project and the web page where all the information comes out
                link1 = (host + URLS[1].format(ex))
                dictionary = {}

                try:
                    r = requests.get(link1, headers=headers)
                    # Connection with the server (with ID)in order to be able to search Info
                    json_code = r.json()
                    id = json_code[0]['id']

                    # We made it another time but this time with the intention of finding the request Info
                    link2 = (host + URLS[2].format(id))
                    r1 = requests.get(link2, headers=headers)
                    json_code1 = r1.json()

                    # We need at least one 'IF' so we use another time the variable 'geneInfo'
                    if list_resource == 'geneInfo':
                        # We declared the diferent variables
                        st = json_code1['desc'].split(':')
                        chromo = st[2]
                        id = json_code1['id']
                        length = json_code1['id']
                        start_point = st[3]
                        end_point= st[4]
                        # We perform a table with their headers and results
                        add = '<table class="table"><thead><tr><th scope="col">Chromo</th><th scope="col">Id</th><th scope="col">Length</th><th scope="col">Start Point</th><th scope="col">End Point</th></tr></thead><tbody>'
                        add += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(chromo, id, length, start_point, end_point )
                        dictionary.update([('chromo', chromo), ('id', id), ('length', length), ('start', start_point), ('end', end_point)])
                        # We established a title for our template.html
                        t = 'Gene Information'
                        # We established a header for our template.html
                        head = 'Information about gene {}'.format(ex)




                except Exception:
                    # We introduce what we want to introduce in the main part of our template html in the case the gene enter is not valid and store it in a dictionary
                    add = 'No Gene {} Found'.format(ex)
                    dictionary.update([('WARNING', 'No Gene {} Found'.format(ex))])
                    # We give a title to our template.html in case of error
                    t = 'ERROR'
                    # We give a header to our template.html in case of error
                    head = 'Sequence of {} NOT FOUND!!!!!'.format(ex)
                archive = template.format(t,t, head, add)
            else:
                #If they use other endpoints
                resp = 404
                # To fill the template.html in case of principally wrong error
                archive = template.format("Error 404", "Error 404", "PAGE NOT FOUND", templateError.format("PAGE NOT FOUND", resource))


        except Exception as e:
            print(str(e))
            # In case another error appear
            resp = 500
            # We fill the template.html in case and unexpected error occur include a tracer that show the error and where it is
            archive = template.format("Error", "Error", "Error de la aplicación", templateError.format("Error de la aplicación", str(e) + '\n' + ''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))))


        # Beginning of web server answer

        #It write the Response.html
        d = open('Response.html', 'w')
        d.write(archive)
        d.close()

        # It read the Response.html
        d = open('Response.html', 'r')
        content = d.read()
        d.close()

        content_type = 'text/html'

        if 'json=1' in resource and resp == 200:
            content_type = 'application/json'
            content = dictionary

        # Send the headers with different contents  and the Request.html
        self.send_response(resp)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', len(str.encode(content)))
        self.end_headers()

        self.wfile.write(str.encode(content))

        # End of web server answer

# ------------------------
# - Server MAIN program
# ------------------------
# -- Set the new handler
Handler = TestHandler

# ---This open the socket server
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Serving at PORT: ", PORT)

    # ----Main loop: Attend the client. Whenever there is a new
    # ----client, the handler is called
    try:
        httpd.serve_forever()
        #--In order to see the error
    except Exception as e:
            print(str(e))
    except KeyboardInterrupt:
        print("")
        print("Stoped by the user")
        httpd.server_close()

import json
import configparser
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

config = configparser.ConfigParser()
config.read("ressources/application.ini")

class Handler(BaseHTTPRequestHandler):
    dico = [] 
    
    def do_GET(self):
        parsed_url = urlparse(self.path)
        
        if parsed_url.path == "/search":
            parameters = parse_qs(parsed_url.query)
            
            if 'query' in parameters:
                wantedWord = parameters['query'][0].lower()
                
                result = []
                for word in self.dico:
                    if word.lower().startswith(wantedWord):
                        result.append(word)

                limited_result = result[:config.getint('application', 'nbWords')]
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*') 
                self.end_headers()
                
                response_json = json.dumps(limited_result)
                self.wfile.write(response_json.encode('utf-8'))
                
            else:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
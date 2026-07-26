from http.server import HTTPServer
import configparser

from core.word_service import WordService
from apis.word_controller import Handler



def main(): 
    service = WordService()
    raw_words = service.read_files("dictionaries") 
    dico_global = service.order_by_alphabetic(raw_words)

    Handler.dico = dico_global

    config = configparser.ConfigParser()
    config.read("ressources/application.ini")

    host = config.get("server", "host")
    port = config.getint("server", "port")
    server = HTTPServer((host, port), Handler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    
    server.server_close()

if __name__ == "__main__":
    main()
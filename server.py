from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import getData

serverInfo = {
    "hostname": "localhost",
    "port": 8080
}

class myServer(BaseHTTPRequestHandler):
    def do_GET(self):
        #sending web interface contents (html, css, js, jquery)
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(open("website/index.html", "rb").read())
        elif self.path == "/script.js":
            self.send_response(200)
            self.send_header("Content-type", "application/javascript; charset=utf-8")
            self.end_headers()
            self.wfile.write(open("website/script.js", "rb").read())
        elif self.path == "/styles.css":
            self.send_response(200)
            self.send_header("Content-type", "text/css; charset=utf-8")
            self.end_headers()
            self.wfile.write(open("website/styles.css", "rb").read())
        elif self.path == "/favicon":
            self.send_response(200)
            self.send_header("Content-type", "image/vnd.microsoft.icon")
            self.end_headers()
            self.wfile.write(open("website/favicon.ico", "rb").read())
        elif self.path == "/icons/usb.svg":
            self.send_response(200)
            self.send_header("Content", "image/svg+xml")
            self.end_headers()
            self.wfile.write(open("icons/usb.svg", "rb").read())
        #sending list of collected data to web interface
        elif self.path == "/data":
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(bytes(getData.getData(), "utf-8"))
        else:
            self.send_error(404)
        
            

if __name__ == "__main__":
    webServer = HTTPServer((serverInfo["hostname"], serverInfo["port"]), myServer)
    print(time.asctime(), "Server started at http://%s:%s" % (serverInfo["hostname"], serverInfo["port"]))

    try: 
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print(time.asctime(), "Server Stopped.")

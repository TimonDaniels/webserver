import os
import socket
import time
from dataclasses import dataclass
from http.client import HTTPException

HOST = "localhost"
PORT = 8080
WEBSITE_DATA_DIR = "website_data"


@dataclass(frozen=True)
class HTTPRequest():
    method: str
    path: str
    version: str
    headers: dict[str, str]

def handle_request(request: HTTPRequest) -> str:
    path = request.path
    status_line = "HTTP/1.1 200 OK"
    
    # get content type based on the path
    if path.endswith(".css"):
        content_type = "text/css"
    elif path.endswith(".js"):
        content_type = "application/javascript"
    elif path.endswith(".png"):
        content_type = "image/png"
    elif path.endswith(".jpg") or path.endswith(".jpeg"):
        content_type = "image/jpeg"
    elif path.endswith(".gif"):
        content_type = "image/gif"
    else: 
        content_type = "text/html"

    # Load the HTML content 
    if path.endswith(".css") or path.endswith(".js") or path.endswith(".png") or path.endswith(".jpg") or path.endswith(".jpeg") or path.endswith(".gif"):
        try:
            with open(os.path.join(WEBSITE_DATA_DIR, path.lstrip('/')), "r") as f:
                html_content = f.read()
        except FileNotFoundError:
            status_line = "HTTP/1.1 404 Not Found"
            html_content = "<html><body><h1>404 Not Found</h1><p>The requested resource was not found on the server.</p></body></html>"
    
    else:
        try:
            match path:
                case "/":
                    with open(os.path.join(WEBSITE_DATA_DIR, "index.html"), "r") as f:
                        html_content = f.read()
                case "/contact":
                    with open(os.path.join(WEBSITE_DATA_DIR, "contact.html"), "r") as f:
                        html_content = f.read()
                case "/properties":
                    with open(os.path.join(WEBSITE_DATA_DIR, "properties.html"), "r") as f:
                        html_content = f.read()
                case "/property-details":
                    with open(os.path.join(WEBSITE_DATA_DIR, "property-details.html"), "r") as f:
                        html_content = f.read()
                case _:
                    status_line = "HTTP/1.1. 404 page not found"
                    html_content = "<html><body><h1>404 Not Found</h1><p>The requested resource was not found on the server.</p></body></html>"
        except:
            status_line = "HTTP/1.1 500 Internal Server Error"
            html_content = "<html><body><h1>500 Internal Server Error</h1><p>There was an error processing your request.</p></body></html>"
   
    # create the response
    content_length = len(html_content)
    response = f"{status_line}\r\nContent-Type: {content_type}\r\nContent-Length: {content_length}\r\n\r\n{html_content}"
    return response

def parse_request(data: bytes) -> HTTPRequest:
    """
    Parses the HTTP request data bytes from a socket.recv() call
    and returns an HTTPRequest object and headers.
    """
    data_str = data.decode('utf-8')
    lines = data_str.split('\r\n')

    # get the request line
    request_line = lines.pop(0)
    method, path, version = request_line.split()
    match method:
        case "GET":
            print(f"GET request for {path}")
        case "POST":
            print(f"POST request for {path}")
        case "PUT":
            print(f"PUT request for {path}")
        case "DELETE":
            print(f"DELETE request for {path}")
    
    # convert headers to a dictionary
    headers = {}
    for line in lines:
        if line == '':
            break
        key, value = line.split(': ', 1)
        headers[key] = value
    print("Headers:")
    for key, value in headers.items():
        print(f"{key}: {value}")

    request = HTTPRequest(method, path, version, headers)
    return request



if __name__ == "__main__":
    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the host and port
    s.bind((HOST, PORT))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print(f"Server started at {HOST}:{PORT}...")

    s.listen(5)
    print(f"Server is listening on {HOST}:{PORT}...")
    while True:
        try:
            # Accept a connection
            conn, addr = s.accept()
            print(f"Connection from {addr} has been established!")

            # Receive client request
            data = conn.recv(1024)
            print("Data received from client:", data.decode('utf-8'))
            request = parse_request(data)
            if not data:
                print("No data received, closing connection.")
                conn.close()
                continue

            # Handle the request
            response = handle_request(request)

            # Send a response
            conn.sendall(response.encode('utf-8'))
            print("Response sent to client.")

        except socket.error as e:
            print("Error occurred:", e)
            time.sleep(1)
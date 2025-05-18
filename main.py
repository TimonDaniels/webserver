import socket
import time
from dataclasses import dataclass
from http.client import HTTPException

HOST = "localhost"
PORT = 8080


@dataclass(frozen=True)
class HTTPRequest():
    method: str
    path: str
    version: str
    

def handle_request(request: HTTPRequest, headers: dict[str, str]) -> str:
    path = request.path

    match path:
        case "/":
            with open("index.html", "r") as f:
                html_content = f.read()
        case "/contact":
            with open("contact.html", "r") as f:
                html_content = f.read()
        case "/properties":
            with open("properties.html", "r") as f:
                html_content = f.read()
        case "/property-details":
            with open("property-details.html", "r") as f:
                html_content = f.read()
        case _:
            raise HTTPException(404, "Not Found", "The requested resource was not found on the server.")


def parse_request(data: bytes) -> tuple[HTTPRequest, dict[str, str]]:
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
    request = HTTPRequest(method, path, version)
    
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

    return request, headers



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
            request, headers = parse_request(data)
            if not data:
                print("No data received, closing connection.")
                conn.close()
                continue

            print(f"Received data: {request}")

            # Send a response
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nHello, World!"
            conn.sendall(response.encode('utf-8'))
            print("Response sent to client.")

        except socket.error as e:
            print("Error occurred:", e)
            time.sleep(1)
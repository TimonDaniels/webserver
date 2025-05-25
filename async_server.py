import os
import socket
import asyncio
import aiofiles
from dataclasses import dataclass

HOST = "localhost"
PORT = 8080
WEBSITE_DATA_DIR = "website_data"


@dataclass(frozen=True)
class HTTPRequest():
    method: str
    path: str
    version: str
    headers: dict[str, str]

async def read_file_async(path: str, mode: str = 'rb') -> bytes:
    """Asynchronously load a file and return its content as bytes."""
    assert isinstance(path, str), "path must be of type str"

    try:
        async with aiofiles.open(path, mode) as f:
            content = await f.read()
        return content
    except FileNotFoundError:
        raise FileNotFoundError(f"File {path} not found in {WEBSITE_DATA_DIR}")


def read_file_sync(path: str, mode: str = 'rb') -> bytes:
    assert isinstance(path, str), "path must be of type str"

    try:
        with open(path, mode) as f:
            content = f.read()
        return content
    except FileNotFoundError:
        raise FileNotFoundError(f"File {path} not found in {WEBSITE_DATA_DIR}")


async def handle_request(request: HTTPRequest) -> str:
    assert isinstance(request, HTTPRequest), "request must be an instance of HTTPRequest"

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

    if path.endswith(".css") or path.endswith(".js") or path.endswith(".png") or path.endswith(".jpg") or path.endswith(".jpeg") or path.endswith(".gif"):
        try:
            file_path = os.path.join(WEBSITE_DATA_DIR, path.lstrip('/'))
            html_content_bytes = read_file_sync(file_path, 'rb')
        except FileNotFoundError:
            status_line = "HTTP/1.1 404 Not Found"
            html_content_bytes = "<html><body><h1>404 Not Found</h1><p>The requested resource was not found on the server.</p></body></html>".encode('utf-8')
        assert isinstance(html_content_bytes, bytes), "html_content must be of type bytes"
    
    else:
        try:
            if path == '/':
                file_path = os.path.join(WEBSITE_DATA_DIR, "index.html")
                html_content = read_file_sync(file_path, 'r')
            elif path.endswith(".html"):
                file_path = os.path.join(WEBSITE_DATA_DIR, path.lstrip('/'))
                html_content = read_file_sync(file_path, 'r')
            else:
                status_line = "HTTP/1.1. 404 page not found"
                html_content = "<html><body><h1>404 Not Found</h1><p>The requested resource was not found on the server.</p></body></html>"
        except:
            status_line = "HTTP/1.1 500 Internal Server Error"
            html_content = "<html><body><h1>500 Internal Server Error</h1><p>There was an error processing your request.</p></body></html>"
        html_content_bytes = html_content.encode('utf-8')
        assert isinstance(html_content_bytes, bytes), "html_content must be of type bytes"

    # create the response
    content_length = len(html_content_bytes)
    response = f"{status_line}\r\nContent-Type: {content_type}\r\nContent-Length: {content_length}\r\n\r\n".encode('utf-8') + html_content_bytes 

    assert isinstance(response, bytes), "response must be of type bytes"
    return response


async def parse_request(data: bytes) -> HTTPRequest:
    """
    Parses the HTTP request data bytes from a socket.recv() call
    and returns an HTTPRequest object and headers.
    """
    assert isinstance(data, bytes), "data must be of type bytes"
    assert len(data) > 0, "data must not be empty"

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
        case _:
            print(f"Unknown request method: {method}")
    
    # convert headers to a dictionary
    headers = {}
    for line in lines:
        if line == '':
            break
        key, value = line.split(': ', 1)
        headers[key] = value
    assert len(headers) > 0, "headers must not be empty"

    print("Headers:")
    for key, value in headers.items():
        print(f"{key}: {value}")

    request = HTTPRequest(method, path, version, headers)
    return request


async def handle_client_connection(conn, addr):
    """Handle individual client connection asynchronously"""
    try:
        print(f"Connection from {addr} has been established!")
        
        # Run blocking socket operations in thread pool
        loop = asyncio.get_event_loop()
        
        # Receive data
        data = await loop.run_in_executor(None, conn.recv, 1024)
        if not data:
            print("No data received, closing connection.")
            conn.close()
            return
            
        print("Data received from client:", data.decode('utf-8'))
        
        # Parse and handle request (these are already async)
        request = await parse_request(data)
        response = await handle_request(request)
        
        # Send response
        await loop.run_in_executor(None, conn.sendall, response)
        print("Response sent to client.")
        
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        conn.close()


async def accept_connections():
    """Main server loop"""
    # Create socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.listen(100)
    
    print(f"Server started at {HOST}:{PORT}...")
    print(f"Server is listening on {HOST}:{PORT}...")
    
    loop = asyncio.get_event_loop()
    
    try:
        while True:
            # Accept connection in thread pool (blocking operation)
            conn, addr = await loop.run_in_executor(None, s.accept)
            
            # Handle connection asynchronously
            asyncio.create_task(handle_client_connection(conn, addr))
            
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    finally:
        s.close()


if __name__ == "__main__":
    asyncio.run(accept_connections())
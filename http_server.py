from http.server import HTTPServer, BaseHTTPRequestHandler
from FaceTracker import FaceTracker
import threading

HOST = "127.0.0.1"
PORT = 8000

face_tracker = FaceTracker()

class RequestHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()
        
        message = face_tracker.get_data()
        
        self.wfile.write(bytes(message, "UTF-8"))


server = HTTPServer((HOST, PORT), RequestHandler)
server_thread = threading.Thread(target=server.serve_forever)
print(f"Server started on {HOST}:{PORT}")
server_thread.start()

# Start the face tracking thread
face_tracking_thread = threading.Thread(target=face_tracker.startTracking)
face_tracking_thread.start()


server_thread.join()
face_tracking_thread.join()
server.server_close()

print("Server closed!")

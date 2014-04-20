import sublime, sublime_plugin;
from threading import Thread
import json
import subprocess
import os

try:
  import BaseHTTPServer
except ImportError:
  import http.server as BaseHTTPServer


def open(directory):
  if sublime.platform() == 'windows':
    subprocess.Popen([sublime.executable_path(), '.'], cwd=directory, shell=True)
  else:
    subprocess.call([os.path.join(os.path.dirname(sublime.executable_path()), '../SharedSupport/bin/subl'), directory])


class ConnectionHandler(BaseHTTPServer.BaseHTTPRequestHandler):

  def do_GET(self):
    print('Received: heartbeat1')
    self.send_response(200)
    self.send_header('Content-type',  'application/json')
    self.send_header('Access-Control-Allow-Origin',  '*')
    self.end_headers()


    return

  def do_POST(self):
    self.data_string = self.rfile.read(int(self.headers['Content-Length']))
    self.send_response(201)
    self.send_header('Content-type',  'application/json')
    self.send_header('Access-Control-Allow-Origin',  '*')
    self.end_headers()

    # grab the data form the post
    data = json.loads(self.data_string.decode("utf-8"))
    a = [x.rstrip() for x in data['txt'].split("\n")]
    data['txt'] = '\n'.join(a)

    # make a new window
    sublime.run_command("new_window")
    active_window = sublime.active_window()
    # make a new file
    active_window.new_file()

    # add the new text to the file
    active_window.run_command("cs_add_text", {"txt": data["txt"]})

    return

class csAddTextCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    self.view.insert(edit, 0, args['txt'])

print("Staring CodeSnippets server on port " + str(7878))

server = BaseHTTPServer.HTTPServer(('', 7878), ConnectionHandler)
Thread(target=server.serve_forever).start()

def plugin_unloaded():
  print("Closing CodeSnippets server")
  server.shutdown()
  server.server_close()

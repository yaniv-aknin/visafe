from subprocess import Popen, PIPE
import os

class TextUnchanged(Exception):
    pass

def edit(text, output_filename):
    _vim(text, 'vim - -n -c "file %s"' % (output_filename,))
    if not os.path.isfile(output_filename):
        raise TextUnchanged('file left unchanged')

def view(text):
    _vim(text, 'view -')

def _vim(text, command_line):
    process = Popen(command_line, stdin=PIPE, shell=True)
    process.communicate(text)
    process.wait()

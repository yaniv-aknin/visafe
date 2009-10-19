from subprocess import Popen, PIPE
from itertools import chain
import warnings

from backports.collections import OrderedDict

class GPGOperationFailed(Exception):
    def __init__(self, retval, status):
        self.retval = retval
        self.status = status
    def __str__(self):
        return "gpg returned %d; conversation transcript:\n%s" % (self.retval, "\n".join(self.status))

def run_gpg(passphrase, *additional_args):
    # FIXME: if you bother to lose the controlling terminal you can hide the annoying gpg messages from tty_printf
    basic_args = ('gpg', '--passphrase-fd 0', '--status-fd 2')
    command_line = " ".join(chain(basic_args, additional_args))
    process = Popen(command_line, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate(passphrase + '\n')
    status = parse_gpg_status_messages(stderr)
    retval = process.poll()
    if retval != 0:
        raise GPGOperationFailed(retval, status)
    return stdout

def parse_gpg_status_messages(text):
    result = OrderedDict()
    for line in text.splitlines():
        parts = line.split(' ')
        if parts[0] != '[GNUPG:]':
            continue
        code, parameters = parts[1], parts[2:]
        # FIXME: I don't know if the codes can repeat themselves and currently I don't care,
        #         so I'll just warn and hope for the best
        if code in result:
            warnings.warn(UserWarning('code %s appears more than once in gpg status output' % (code,)))
        result[code] = parameters
    return result

def decrypt_file(passphrase, filename):
    return run_gpg(passphrase, '--decrypt', filename)

def encrypt_file(passphrase, source_filename, destintation_filename):
    run_gpg(passphrase, '--symmetric', '--output %s' % (destintation_filename,), source_filename)

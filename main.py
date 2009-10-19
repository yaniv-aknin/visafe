import os
import getpass

import argparse

from crypto import encrypt_file, decrypt_file, GPGOperationFailed
import utils
import vim

SUCCESS = 0
FAILURE = 1

def validate_runtime_environment():
    # TODO: do we have /dev/shm?
    # TODO: are there stale visafe entries in /dev/shm?
    pass

def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='filename to edit securely')
    parser.add_argument('-v', '--view', help='view only', action='store_true')
    options = parser.parse_args(argv[1:])
    if not os.path.isfile(options.filename):
        parser.error('no such file %s' % (options.filename,))
    return options

def main(options):
    for attempt in (1,2,3):
        try:
            passphrase = getpass.getpass('Enter the passphrase to decrypt %s: ' % (options.filename,))
            cleartext = decrypt_file(passphrase, filename=options.filename)
            break
        except GPGOperationFailed, error:
            if 'DECRYPTION_FAILED' in error.status:
                print("Wrong password; try again.")
            else:
                print("Unknown error; %s" % (error,))
    else:
        print("Wrong passphrase.")
        return FAILURE

    if options.view:
        vim.view(cleartext)
        return SUCCESS

    temporary_filename = utils.get_temporary_filename('visafe')
    try:
        vim.edit(cleartext, output_filename=temporary_filename)
    except vim.TextUnchanged:
        return SUCCESS

    utils.remove_with_backup(options.filename)
    encrypt_file(passphrase, source_filename=temporary_filename, destintation_filename=options.filename)
    # TODO: make sure temporary_filename was really deleted
    return SUCCESS

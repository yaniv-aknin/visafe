import getpass
import os

def get_temporary_filename(application_name):
    return '/dev/shm/%s-%s-%d' % (application_name, getpass.getuser(), os.getpid())

def remove_with_backup(original_filename):
    full_path = os.path.realpath(original_filename)
    dirname, filename = os.path.dirname(full_path), os.path.basename(full_path)
    backup_filename = os.path.join(dirname, '.' + filename + '.bak')
    if os.path.isfile(backup_filename):
        os.remove(backup_filename)
    os.rename(original_filename, backup_filename)

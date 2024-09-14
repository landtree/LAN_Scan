import os

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

def main():
    # Instantiate a dummy authorizer for managing 'virtual' users
    authorizer = DummyAuthorizer()
    #pull this in from an INI created from the GUI
    #Hardcoded for now
    pictureStorage = "D:\\scan_images"
    
    #create the scanner username
    #probably should change to a different username for production
    authorizer.add_user('scan','scanner',pictureStorage,perm='elradfmwMT')

    # Instantiate FTP handler class
    handler = FTPHandler
    handler.authorizer = authorizer

    # Define a customized banner (string returned when client connects)
    handler.banner = "Scanner Connected"

    # Instantiate FTP server class and listen on 0.0.0.0:2121
    address = ('0.0.0.0', 2121)
    server = FTPServer(address, handler)
    

    # set a limit for connections
    server.max_cons = 5
    server.max_cons_per_ip = 256

    # start ftp server
    server.serve_forever()

if __name__ == '__main__':
    main()
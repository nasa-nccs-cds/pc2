from pc2.app.core import PC2Core

if __name__ == "__main__":

    settings = dict(server=dict( type="rest", host="127.0.0.1", port="5000", API="wps", route="wps/cwt") )
    pc2 = PC2Core(settings)
    client = pc2.getClient()
    response = client.capabilities( "process")
    print( response["xml"] )


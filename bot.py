import telebot
import config
import logging
import cherrypy
from bot_loader import bot


WEBHOOK_HOST = '5.23.48.22'

WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')

WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate

WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key

# Quick'n'dirty SSL certificate generation:

#

# openssl genrsa -out webhook_pkey.pem 2048

# openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem

#

# When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply

# with the same value in you put in WEBHOOK_HOST


WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)

WEBHOOK_URL_PATH = "/%s/" % config.TOKEN

# logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

# own custom logger
cool_logger = logging.getLogger('bot_logger')


# WebhookServer, process webhook calls

class WebhookServer(object):
    
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and 'content-type' in cherrypy.request.headers and \
                cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)


# bot initialization



if __name__ == '__main__':
    
    print(bot.message_handlers)
    
    # Remove webhook, it fails sometimes the set if there is a previous webhook
    
    bot.remove_webhook()
    
    # Set webhook
    
    bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH, certificate=open(WEBHOOK_SSL_CERT, 'r'))
    
    # Disable CherryPy requests log
    
    access_log = cherrypy.log.access_log
    
    for handler in tuple(access_log.handlers):
        access_log.removeHandler(handler)
    
    # Start cherrypy server
    
    cherrypy.config.update({
        
        'server.socket_host': WEBHOOK_LISTEN,
        
        'server.socket_port': WEBHOOK_PORT,
        
        'server.ssl_module': 'builtin',
        
        'server.ssl_certificate': WEBHOOK_SSL_CERT,
        
        'server.ssl_private_key': WEBHOOK_SSL_PRIV
        
    })
    #
    cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})

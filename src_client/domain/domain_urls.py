from domain.kb_domain.handler import KbHandler, ChatHandler, ChatHistoryHandler
from domain.md_domain.handler import MdHandler

urls = []
urls += KbHandler.urls
urls += MdHandler.urls
urls += ChatHandler.urls
urls += ChatHistoryHandler.urls

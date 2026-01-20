import logging
from datetime import datetime

from domain.base_domain.BaseHandler import BaseHandler, BaseApiHandler
from domain.kb_domain.dao import ChatDao, ChatHistoryDao
from domain.kb_domain.serv.ChatServ import knowledge_base_chat
from util import IDUtil


class AiChatHandler(BaseHandler):
    need_login = False

    async def get(self, *args, **kwargs):
        self.set_header('Content-Type', 'text/event-stream')
        self.set_header('Cache-Control', 'no-cache')
        self.set_header('Connection', 'keep-alive')
        self.set_header("Access-Control-Allow-Origin", "*")  # 允许跨域请求
        _msg = self.get_arg('msg') or ''
        _chat_id = self.get_arg('chat_id') or ''
        _doc_id = self.get_arg('doc_id') or ''
        _knowledge_base_id = self.get_arg('knowledge_base_id') or ''
        _stream = True
        _model_name = 'deepseek-v3-250324'
        _temperature = 0.7
        _max_tokens = 12288
        await knowledge_base_chat(self, _msg, _chat_id, _knowledge_base_id, _doc_id, _model_name, _temperature,
                                  _max_tokens, _stream)


class AiAddChatHandler(BaseApiHandler):
    need_login = False

    def myget(self):
        pass

    def mypost(self):
        try:
            # _chat_id = self.get_arg('chat_id')
            _chat_id = IDUtil.get_long()
            _customer_id = self.get_arg('customer_id')
            _chat_name = self.get_arg('chat_name')
            _chat_type = self.get_arg('chat_type')
            if not _chat_id or not _customer_id or not _chat_name or not _chat_type:
                self.write({'success': False, 'msg': '参数不完整'})
                return
            ChatDao.insert(
                {'chat_id': _chat_id, 'customer_id': _customer_id, 'chat_name': _chat_name, 'chat_type': _chat_type,
                 'create_time': datetime.now()})
            self.write({'success': True, 'msg': '添加成功', 'data': _chat_id})
        except Exception as e:
            logging.error("添加聊天记录失败: %s\n%s", str(e))
            self.write({'success': False, 'msg': '添加失败'})


class AiChatListHandler(BaseApiHandler):
    need_login = False

    def myget(self):
        try:
            _chat_type = self.get_arg('chat_type')
            _chatList = ChatDao.get_all({'chat_type': _chat_type})
            self.write({'success': True, 'msg': '聊天记录查询成功', 'data': _chatList})
        except Exception as e:
            logging.error("聊天记录查询失败: %s\n%s", str(e))
            self.write({'success': False, 'msg': '聊天记录查询'})


class AiDelChatHandler(BaseApiHandler):
    need_login = False

    def myget(self):
        try:
            _chat_id = self.get_arg('chat_id')
            if not _chat_id:
                self.write({'success': False, 'msg': '缺少 chat_id 参数'})
                return
            record = ChatDao.get_by_id(_chat_id)
            if not record:
                self.write({'success': False, 'msg': '记录不存在'})
                return
            ChatDao.delete(_chat_id)
            ChatHistoryDao.delete_by_chat(_chat_id)
            self.write({'success': True, 'msg': '删除成功'})
        except Exception as e:
            logging.error("删除聊天记录失败: %s\n%s", str(e))
            self.write({'success': False, 'msg': '删除失败'})


urls = [
    ('/api/chat/aichat', AiChatHandler),
    ('/api/chat/addChat', AiAddChatHandler),
    ('/api/chat/chatList', AiChatListHandler),
    ('/api/chat/delChat', AiDelChatHandler),
]

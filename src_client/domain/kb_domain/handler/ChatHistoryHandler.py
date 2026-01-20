import datetime
import logging

from domain.base_domain.BaseHandler import BaseApiHandler
from domain.kb_domain.dao import ChatHistoryDao
from util import IDUtil


class AiAddChatHistoryHandler(BaseApiHandler):
    need_login = False

    def myget(self):
        pass

    def mypost(self):
        try:
            # _chat_history_id = self.get_arg('chat_history_id')
            _chat_history_id = IDUtil.get_long()
            _chat_id = self.get_arg('chat_id')
            _chat_index = self.get_arg('chat_index')
            _role_name = self.get_arg('role_name')
            _message = self.get_arg('message')
            if not _chat_id or not _chat_id or not _chat_index or not _role_name or not _message:
                self.write({'success': False, 'msg': '参数不完整'})
                return
            ChatHistoryDao.insert(
                {'chat_history_id': _chat_history_id, 'chat_id': _chat_id, 'chat_index': _chat_index,
                 'role_name': _role_name,
                 'message': _message, 'create_time': datetime.datetime.now()})
            self.write({'success': True, 'msg': '添加成功'})
        except Exception as e:
            logging.error("添加聊天记录失败: %s\n%s", str(e))
            self.write({'success': False, 'msg': '添加失败'})


class AiChatHistoryListHandler(BaseApiHandler):
    need_login = False

    def myget(self):
        try:
            _chat_id = self.get_arg('chat_id')
            _ChatHistoryList = ChatHistoryDao.get_by_chatId(_chat_id)
            self.write({'success': True, 'msg': '查询成功', 'data': _ChatHistoryList})
        except Exception as e:
            logging.error("添加聊天记录失败: %s\n%s", str(e))
            self.write({'success': False, 'msg': '查询失败'})


urls = [
    ('/api/chatHistory/addChatHistory', AiAddChatHistoryHandler),
    ('/api/chatHistory/chatHistoryList', AiChatHistoryListHandler),
]

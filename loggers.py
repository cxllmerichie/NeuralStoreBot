from apidevtools import logman
import os


log: logman.Logger = logman.add(os.path.join('logs', 'log.log'))
search: logman.Logger = logman.add(os.path.join('logs', 'search.log'))
dntrade: logman.Logger = logman.add(os.path.join('logs', 'dntrade.log'))


class OpenAI(dict):
    def __getitem__(self, chat_id: int) -> logman.Logger:
        if chat_id not in self:
            self[chat_id] = logman.add(os.path.join('logs', 'openai', f'{chat_id}.log'))
        return super().__getitem__(chat_id)


openai: OpenAI = OpenAI()

import os


class Auth:
    """
    通用的 auth 类，用来管理所有的 auth
    目前还没想好怎么设计，主要是因为，没确定不同机器人的 auth 是否一样
    """
    def __init__(self, auth: str=None):
        # 设定 auth，可不传，默认从环境变量中获取
        if auth:
            self.auth = auth
        else:
            self.auth = os.environ.get("NOTION_AUTH")

    def getAuth(self):
        return self.auth
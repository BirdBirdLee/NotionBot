from notion_client import Client
import datetime
import time
import iso8601


class JournalBot:
    """
    日记机器人
    目前实现的主要功能是，传入代码
    """
    base_url = "https://api.notion.com/v1/"

    def __init__(self, auth, database_id):
        self.auth = auth
        self.notion = Client(auth=auth)
        self.database_id = database_id
        self.database_url = self.base_url + "databases/" + database_id

    def get_database(self):
        """
        获取数据库信息
        :return:
        """
        res = self.notion.request(path=self.database_url, method="GET")
        return res


    def find_page_with_blank_name(self):
        """
        获取 Name （title）为空的 pages
        :return:
        """
        data = {
            "filter": {
                "property": "Name",
                "text": {
                    "is_empty": True
                }
            }
        }
        res = self.notion.request(path=self.database_url + '/query', method="POST", body=data)
        return res['results']


    def update_page_name_by_page_id(self, page_id, name):
        """
        根据 page_id 更新某个 page 的 name
        :param page_id:
        :param name:
        :return:
        """
        url = self.base_url + 'pages/' + page_id

        data = {
            "properties": {
                "Name": {
                    "title": [
                        {
                            "type": "text",
                            "text": {
                                "content": name
                            }
                        }
                    ]
                }
            }
        }
        res = self.notion.request(path=url, body=data, method="PATCH")
        return res

    def formatISO2str(self, iso_time, timezone=8):
        """
        将 iso8601 时区转化为 2021年08月25日 形式，并处理时区（Notion API 默认是 UTC0）
        :param iso_time:
        :param timezone:
        :return:
        """
        # iso8601 读取
        datetime_UTC = iso8601.parse_date(iso_time)
        # 时区转换
        datetime_real = datetime_UTC + datetime.timedelta(hours=timezone)
        # 格式化
        date = datetime_real.strftime("%Y年%m月%d日")
        return date

    def update_page_name_by_page(self, page, name=''):
        '''
        修改某页面的名称，若不传 name，则默认将格式化的 created 作为名字
        :param page:
        :param name:
        :return:
        '''
        page_id = page['id']
        if name == '' or name is None:
            # Notion API 的时区默认是零时区，所以要处理一下时间
            iso8601_time = page['created_time']
            name = self.formatISO2str(iso8601_time)
        return self.update_page_name_by_page_id(page_id, name)

    def update_history_pages_name(self, pages):
        """
        将所有传入的 page 的 Name 设为创立日期，格式：2021年08月24日
        :param pages:
        :return:
        """
        for page in pages:
            self.update_page_name_by_page(page)

    def update_blank_pages_name(self):
        """
        更新所有 Name 为空的 page，设 Name 为创立日期，格式：2021年08月24日
        :param pages:
        :return:
        """
        self.update_history_pages_name(self.find_page_with_blank_name())


    def create_journal(self):
        """
        遍历数据库所有 page 的 Name，若没有与今天日期相同的，认为今天的日记未被创立，新建当日日记
        :return:
        """
        if self.if_exist_today_journal():
            return None
        url = self.base_url + 'pages'
        data = {
            "parent": {
                "database_id": self.database_id
            },
            "properties": {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": ""
                            }
                        }
                    ]
                }
            }
        }
        res = self.notion.request(path=url, method="POST", body=data)
        today = datetime.datetime.now().strftime("%Y年%m月%d日")
        print(today, "的日记已创立")
        return res


    def if_exist_today_journal(self):
        """
        判断今天的日记是否已经存在
        方法：遍历数据库所有 page 的 Name，看是否与当天日期相同的
        :return:
        """
        today = datetime.datetime.now().strftime("%Y年%m月%d日")
        # print(today)
        data = {
            "filter": {
                "property": "Name",
                # "is_empty": True
                "text": {
                    "equals": today
                }
            }
        }
        res = self.notion.request(path=self.database_url + '/query', method="POST", body=data)
        if len(res['results']) > 0:
            return True
        else:
            return False

    def auto_create_and_rename(self):
        """
        整个创建日历、重命名日历的流程
        :return:
        """
        # 先扫描一遍数据库，把空Name改了。防止出现手动创立无名日记未被及时改名的情况
        print("日记机器人已启动")
        self.update_blank_pages_name()
        # 判断当日日记是否存在，不存在则新建
        page_new = self.create_journal()
        # 再改名一次，把刚刚创立的无名的日记的名字改了
        if page_new:
            today = datetime.datetime.now().strftime("%Y年%m月%d日")
            self.update_page_name_by_page(page=page_new, name=today)


if __name__ == '__main__':
    auth = "这里填机器人的 token "
    # 也可以把参数配在环境变量里面
    # auth = os.environ.get("NOTION_AUTH")
    database_id = "这里填 database id"
    journal_bot = JournalBot(auth=auth, database_id=database_id)

    # 运行一次，使用定时脚本每天唤醒，需自行实现定时执行功能
    journal_bot.auto_create_and_rename()

    # 利用 sleep　一直执行，每隔三小时运行一次
    # while True:
    #     journal_bot.auto_create_and_rename()
    #     time.sleep(3 * 3600)
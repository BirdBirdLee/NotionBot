from bot.journal import JournalBot
import time
import os

if __name__ == '__main__':
    auth = os.environ.get("NOTION_AUTH")
    database_id = "28fe61c6656c4b0cba72a220aa3754c0"
    journal_bot = JournalBot(auth=auth, database_id=database_id)
    journal_bot.auto_create_and_rename()
    print("日记建立和改名都已完成")

    # while True:
    #     journal_bot.auto_create_and_rename()
    #     time.sleep(3 * 3600)
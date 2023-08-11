from typing import List, Dict
import logging
import re
import time
import asyncio
from mastoBot.configManager import ConfigAccessor
from mastoBot.mastoBot import MastoBot, handleMastodonExceptions


class MyBot(MastoBot):
    @handleMastodonExceptions
    def processMention(self, mention: Dict):
        api_status = self.getStatus(mention.get("status"))
        api_account = self.getAccount(mention.get("account"))
        content = api_status.get("content")

        # Check for report tag
        report_pattern = r"(.*?)(?<!\S)\$report\b\s*(.*)</p>"
        report_match = re.search(report_pattern, content)

        # If report message
        if report_match:
            before_report = report_match.group(1).strip()
            report_message = report_match.group(2).strip()
            logging.info(f"⛔ \t Report message received: {report_message}")

            template_data = {
                "creator": api_account.get("acct"),
                "reported_post_id": mention.get("status"),
                "reported_post_url": api_status.get("url"),
                "report_message": report_message,
            }

            try:
                output = self.getTemplate("report.txt", template_data)
                self._api.status_post(status=output, visibility="direct")
            except Exception as e:
                logging.critical("❗ \t Error posting status message")
                raise e
        else:
            # Check boost and favourite configs
            shouldReblog = self.shouldReblog(mention.get("status"))
            shouldFavourite = self.shouldFavorite(mention.get("status"))
            altTextTestPassed = self.altTextTestPassed(mention.get("status"), "boosts")

            # Check boost
            if shouldReblog:
                try:
                    self.reblogStatus(mention.get("status"))
                except Exception as e:
                    logging.warning(f"❗ \t Status could not be boosted")
                    logging.error(e)
            elif not altTextTestPassed:
                template_data = {"account": api_account.get("acct")}

                try:
                    output = self.getTemplate("missing_alt_text.txt", template_data)
                    self._api.status_post(status=output, visibility="direct")
                except Exception as e:
                    logging.critical("❗ \t Error sending missing-alt-text message")
                    raise e

            # Check favourite
            if shouldFavourite:
                try:
                    self.favoriteStatus(mention.get("status"))
                except Exception as e:
                    logging.warning(f"❗ \t Status could not be favourited")
                    logging.error(e)

        logging.info(f"📬 \t Mention processed: {mention.get('id')}")
        self.dismissNotification(mention.get("id"))

    @handleMastodonExceptions
    def processReblog(self, reblog: Dict):
        self.dismissNotification(reblog.get("id"))

    @handleMastodonExceptions
    def processFavourite(self, favourite: Dict):
        self.dismissNotification(favourite.get("id"))

    @handleMastodonExceptions
    def processFollow(self, follow: Dict):
        # Get latest account from the Mastodon API
        api_account = self.getAccount(follow.get("account"))
        account = api_account.get("acct")

        template_data = {"account": account}

        # Generate the welcoming message from the template
        try:
            output = self.getTemplate("new_follow.txt", template_data)
            self._api.status_post(status=output, visibility="direct")
        except Exception as e:
            logging.critical("❗ \t Error posting Status")
            raise e

        logging.info(f"📭 \t Follow processed: {follow.get('id')}")
        self.dismissNotification(follow.get("id"))

    @handleMastodonExceptions
    def processPoll(self, poll: Dict):
        self.dismissNotification(poll.get("id"))

    @handleMastodonExceptions
    def processFollowRequest(self, follow_request: Dict):
        self.dismissNotification(follow_request.get("id"))

    @handleMastodonExceptions
    def processUpdate(self, update: Dict) -> None:
        self.dismissNotification(update.get("id"))

if __name__ == "__main__":
    config = ConfigAccessor("config.yml")
    credentials = ConfigAccessor("credentials.yml")
    bot = MyBot(credentials=credentials, config=config)
    
    async def bot_loop():
        await bot.run()
        
    async def timer():
        while True:
            logging.info('tick')
            await asyncio.sleep(5)
        
    async def main():
        await asyncio.gather(bot_loop(), timer())

    while True:
        try:
            asyncio.run(main())
        except:
            time.sleep(10)
            pass

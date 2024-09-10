from fastapi.concurrency import asynccontextmanager
import redis
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler

from app.schemas.exceptions import BotExpiredException
from app.schemas.wechat import WxBot
from app.utils.redis_util import add_bot_to_redis, get_random_bot_from_redis
from app.utils.wechat import autoReply
from contextlib import contextmanager

from app.config import Settings

settings = Settings()

redis_client = redis.StrictRedis(host=settings.REDIS_HOST,
                                 port=settings.REDIS_PORT,
                                 db=0,
                                 password=settings.REDIS_PASSWORD)


@contextmanager
def bot_context_manager():
    try:
        bot: WxBot | None = get_random_bot_from_redis()
        if bot is None or bot.is_offline:
            yield None
            return
        yield bot
    except BotExpiredException:
        bot.is_offline = True
        print(f'bot {bot.wechat_id} is offline')
    except Exception as e:
        print(f'fail:{e}')
    finally:
        if bot:
            add_bot_to_redis(bot)


def repeat_task():
    with bot_context_manager() as bot:
        if bot is None:
            print('None bot can use')
            return
        autoReply(bot)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
    # repeat task every 10 seconds
    scheduler.add_job(func=repeat_task, trigger="interval", seconds=1, max_instances=1000)
    scheduler.start()
    yield


app = FastAPI(lifespan=lifespan)

import redis
import json
from app.config import Settings
from app.schemas.wechat import WxBot

settings = Settings()

# 连接到 Redis 服务器
redis_client = redis.StrictRedis(host=settings.REDIS_HOST,
                                 port=settings.REDIS_PORT,
                                 db=1,
                                 password=settings.REDIS_PASSWORD)


def save_message_to_redis(message, wechat_id):
    session_key = f"conversation_history:{wechat_id}"
    # 将消息对象转换为 JSON 字符串
    message_json = json.dumps(message)
    # 将消息推送到 Redis 列表中
    redis_client.rpush(session_key, message_json)


def get_conversation_history_from_redis(wechat_id):
    session_key = f"conversation_history:{wechat_id}"
    # 从 Redis 获取最新的20条消息
    messages_json = redis_client.lrange(session_key, -20, -1)
    # 将每个消息的 JSON 字符串转换回字典对象
    messages = [json.loads(m) for m in messages_json]
    return messages


def add_bot_to_redis(wxbot: WxBot):
    try:
        data_json = json.dumps(wxbot.model_dump())
        redis_client.set(f'wxbot:{wxbot.wechat_id}', data_json)
    except Exception as e:
        print(f'add bot to redis error {e}')
        return False
    return True


def remove_bot_from_redis(wxbot: WxBot):
    try:
        redis_client.delete(f'wxbot:{wxbot.wechat_id}')
    except Exception as e:
        print(f'remove bot from redis error {e}')
        return False
    return True


def get_random_bot_from_redis():
    wxbot_keys = redis_client.keys('wxbot:*')
    if len(wxbot_keys) == 0:
        print('no bot in redis')
        return None
    wxbot_key = wxbot_keys[0]
    wxbot_json = redis_client.get(wxbot_key)
    wxbot = WxBot.model_validate_json(wxbot_json)
    remove_bot_from_redis(wxbot)
    print(f'wxbot:{wxbot.wechat_id}')
    return wxbot

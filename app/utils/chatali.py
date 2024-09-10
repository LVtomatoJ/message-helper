from http import HTTPStatus
import random
import dashscope

from app.utils.redis_util import get_conversation_history_from_redis, save_message_to_redis

from app.config import Settings

setings = Settings()

prop = {
    "role": "system",
    "content": "你叫王银者"
    }


def call_with_messages(message, wechat_id):
    send_messages = []
    history_messages = get_conversation_history_from_redis(wechat_id=wechat_id)
    #  添加历史上下文
    send_messages += history_messages
    # 添加提示词
    # send_messages.append(prop)
    # 添加问题
    question_message = {"role": "user", "content": message}
    save_message_to_redis(question_message, wechat_id)
    send_messages.append(question_message)

    response = dashscope.Generation.call(
        dashscope.Generation.Models.qwen_plus,
        api_key=setings.QIANWEN_API_KEY,
        messages=send_messages,
        result_format="message",  # 将返回结果格式设置为 message
        seed=random.randint(1, 10000),
        enable_search=True,  # 开启搜索功能
        top_k=50,
        top_p=0.95,
        temperature=1
    )
    if response.status_code == HTTPStatus.OK:
        # 记录回答
        anser = {"role": "assistant",
                 "content": response.output.choices[0].message.content}
        save_message_to_redis(anser, wechat_id)
        return response.output.choices[0].message.content
    else:
        print('Error: 阿里云qwen请求出错')


if __name__ == "__main__":
    call_with_messages()

from datetime import datetime, timedelta
import requests

from app.schemas.wechat import MessageListResp, SendMessageResp, WxBot
from app.utils.chatali import call_with_messages

from app.config import Settings

settings = Settings()

base_url = settings.BOT_URL

last_reply_time = datetime.now()


def autoReply(wxbot: WxBot):
    private_text_msg, group_text_msg = get_messages(wxbot)
    print(f'private_text_msg:{private_text_msg}')
    print(f'group_text_msg:{group_text_msg}')
    for msg in private_text_msg:
        text_content = call_with_messages(msg.content.str,
                                          msg.from_user_name.str)
        send_message(wxbot, text_content, msg.from_user_name.str)
    if group_text_msg:
        global last_reply_time
        msg = group_text_msg[0]
        msg_text = msg.content.str.split(':\n')[1]
        if msg_text.startswith('Q'):
            question = msg_text[1:]
            text_content = call_with_messages(question,
                                              msg.from_user_name.str)
            send_message(wxbot, text_content, msg.from_user_name.str)
        elif datetime.now() - last_reply_time > timedelta(minutes=5):
            last_reply_time = datetime.now()
            send_message(wxbot, '搞笑鸡', msg.from_user_name.str)


def get_messages(wxbot: WxBot):
    url = base_url + f"/v1/message/NewSyncHistoryMessage?key={wxbot.key}&uuid={wxbot.uuid}"

    data = {"Scene": 1}
    try:
        anser = requests.post(url, json=data)
        if anser.status_code != 200:
            print("Error: 账号断开连接")
            return [], []
        anser = anser.json()
        model_anser = MessageListResp.model_validate(anser)
        if model_anser.Code != 200:
            print("Error: 请求出错")
            print(model_anser.Text)
            return [], []
        if model_anser.Data is None or model_anser.Data.AddMsgs is None:
            print("Info: 无消息")
            return [], []
        private_text_msg = [
            msg for msg in model_anser.Data.AddMsgs
            if msg.msg_type == 1  # 文本消息
            and msg.to_user_name.str == wxbot.wechat_id  # 消息发送者是自己
            and msg.from_user_name.str.startswith("wxid_")  # 不是群聊
        ]
        group_text_msg = [
            msg for msg in model_anser.Data.AddMsgs if msg.msg_type == 1
            and msg.to_user_name.str == wxbot.wechat_id  # 消息发送者是自己
            and msg.from_user_name.str.endswith('@chatroom')  # 是群聊
        ]
        print(f'add msg list:{model_anser.Data.AddMsgs}')
        return private_text_msg, group_text_msg
    except Exception as e:
        print(f"Error: {e}")
        return [], []


def send_message(wxbot: WxBot, text_content: str, to_wechat_id: str):
    url = f"{base_url}/v1/message/SendTextMessage?key={wxbot.key}&uuid={wxbot.uuid}"
    data = {"MsgItem": [{"ToUserName": to_wechat_id, "TextContent": text_content}]}
    try:
        anser = requests.post(url, json=data).json()
        model_anser = SendMessageResp.model_validate(anser)
        if model_anser.Code == 200 and model_anser.Data[0].isSendSuccess:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

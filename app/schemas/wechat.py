from typing import Union
from pydantic import BaseModel


class WxBaseResp(BaseModel):
    Code: int
    Text: str


class StrModel(BaseModel):
    str: str


class WxbotV3AddMsgInfo(BaseModel):
    msg_id: int
    from_user_name: StrModel
    to_user_name: StrModel
    msg_type: int  # 1是文本3是图片
    content: StrModel


class MessageListData(BaseModel):
    AddMsgs: Union[list[WxbotV3AddMsgInfo], None]


class MessageListResp(WxBaseResp):
    Data: Union[MessageListData, None]


class WxBot(BaseModel):
    uuid: str
    key: str
    wechat_id: str
    is_offline: bool


class SendMessageData(BaseModel):
    isSendSuccess: bool


class SendMessageResp(WxBaseResp):
    Data: list[SendMessageData]

class BotExpiredException(Exception):
    def __init__(self, message="Bot Expired"):
        self.message = message
        super().__init__(self.message)

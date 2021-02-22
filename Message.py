from MessageType import MESSAGE_TYPE_BWTWEEN_NODES


class MessageBetweenNodes:
    def __init__(self):
        self.type = None
        self.content = None

    def build(self, content: str, type: MESSAGE_TYPE_BWTWEEN_NODES):
        self.type = type
        self.content = content

    def build_from_str(self, s: str):
        pass
    # TODO

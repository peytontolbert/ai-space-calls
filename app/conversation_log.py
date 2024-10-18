class ConversationLog:
    def __init__(self):
        self.messages = []
        self.system_prompt = ""

    def add_message(self, name, content):
        self.messages.append({"name": name, "content": content})

    def get_log(self):
        return self.messages

    def clear(self):
        self.messages = []

    def set_system_prompt(self, prompt):
        self.system_prompt = prompt

    def get_system_prompt(self):
        return self.system_prompt

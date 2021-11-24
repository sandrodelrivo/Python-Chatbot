import openai_wrapper
import json
from loguru import logger


class Chatbot:

    WORKING_MEMORY_CHARACTER_LIMIT = 800

    conversation_header = 'The following is a conversation between a friendly AI chatbot named {0} ' \
                          'and a human named {1}. {0} is happy and excited and wants to talk.\n\n'

    conversation_start = '{0}: Hello! I am glad to talk to you!\n' \
                         '{1}: Thanks!\n' \
                         '{0}: What do you want to talk about?\n' \
                         '{1}:'

    working_memory = ''
    name = 'Chatty'
    user_name = 'Jon'
    file_path = 'data.json'

    def __init__(self):
        pass

    def birth(self, name='Chatty', user_name='Jon', file_path='data.json'):

        # birth bot and initialize its JSON to store its data

        self.file_path=file_path

        # Blank Chatbot
        data = {
            'Name': name,
            'User Name': user_name,
            'Conversation Memories': [],
        }

        with open(file_path, 'w') as file_object:  # open the file in write mode
            json.dump(data, file_object)

    def __set_file_path(self, file_path=''):

        if file_path == '':
            file_path = self.file_path

        return file_path

    def __get_memories(self, file_path=''):

        file_path = self.__set_file_path(file_path)

        with open(file_path, 'r') as file_object:  # open the file in read mode
            data = json.load(file_object)

        return data["Conversation Memories"]

    async def __search_memories(self, message, file_path=''):

        file_path = self.__set_file_path(file_path)

        print(file_path)

        memories = self.__get_memories(file_path)

        print("memories:", memories)

        search = await openai_wrapper.search(message, memories)

        return memories[search.data[0].document]

    # save the conversation as a memory fragment
    def __save_memory(self, memory, file_path=''):

        file_path = self.__set_file_path(file_path)

        logger.debug("Character limit has been reached. Saving conversation as a memory...")

        data_file = open(file_path, 'r')

        data = json.load(data_file)

        data_file.close()

        data['Conversation Memories'].append(memory)

        write_file = open(file_path, 'w')

        json.dump(data, write_file)

    # append the user's message to working memory before passing to GPT-3 for call
    def __append_message_to_wm(self, message):

        self.working_memory += " " + message + "\n" + self.name + ":"

    def __append_response_to_wm(self, response):

        self.working_memory += response + "\n" + self.user_name + ":"

    def wake_and_init(self, file_path='chatty_data.json'):

        with open(file_path, 'r') as file_object:
            data = json.load(file_object)

        self.name = data['Name']
        self.user_name = data['User Name']
        self.file_path = file_path

        self.conversation_header = self.conversation_header.replace("{0}", self.name)
        self.conversation_header = self.conversation_header.replace("{1}", self.user_name)

        self.conversation_start = self.conversation_start.replace("{0}", self.name)
        self.conversation_start = self.conversation_start.replace("{1}", self.user_name)

        self.working_memory = self.conversation_start

    def __reset_working_memory(self):
        self.working_memory = self.conversation_start

    async def message(self, message, response_length=144):

        # setup bot working memory
        self.__append_message_to_wm(message)

        # semantic search over memory
        search = await self.__search_memories(message)

        # finalize conversation prompt
        prompt = self.conversation_header + search + "\n" + self.working_memory

        response = await openai_wrapper.completion(prompt, engine='davinci', stop="\n")

        self.__append_response_to_wm(response.choices[0].text)

        if len(self.working_memory) > self.WORKING_MEMORY_CHARACTER_LIMIT:
            self.__save_memory(self.working_memory)
            self.__reset_working_memory()

        return response

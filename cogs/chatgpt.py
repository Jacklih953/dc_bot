import openai
import os
from collections import deque
import discord
import asyncio
from discord.ext import commands
from datetime import datetime
from asgiref.sync import sync_to_async
import io, base64
import json
import tiktoken

openai.api_key = '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'

with open(os.path.join("setup\consolution.txt"),"r",encoding = 'utf-8') as f:
    consol = f.read()



class Chatgpt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.debug = bot.debug
        self.conversation = Conversation(limit=6)

    @commands.hybrid_command(name='story')
    async def _story(self,ctx, prompt:str):
        # try:
        await ctx.defer()
        self.conve = deque(maxlen=5)

        messages = self.conversation.prepare_prompt(prompt)

        resopnse = await self.game_generation(messages)
        self.conversation.append_response(resopnse)

        hint = self.summarize(resopnse)
        img_b64 = self.dalle_gan(hint)
        print(self.conversation)
        await ctx.channel.send(resopnse,file = discord.File(io.BytesIO(base64.b64decode(img_b64)),filename='1.png'))
        await asyncio.sleep(2)
        #except:
        #return await ctx.send("broken")

    async def game_generation(self, messages):
        if self.debug:
            response = "This is a test message from game_generation()."
        else:
            completion = await sync_to_async(openai.ChatCompletion.create)(
                model = 'gpt-3.5-turbo',
                messages = messages
            )
            response = completion.choices[0].message.content
        return response

    def dalle_gan(self, hint):
        if self.debug:
            with open("D:\pythonwork\dc_bot\image_saved\demo0.jpg",'rb') as image_file:
                image_bytes = image_file.read()
                img_b64 = base64.b64encode(image_bytes).decode('utf-8')
        else:
            result = openai.Image.create(
                prompt = hint,
                n=1,
                size = "1024x1024",
                response_format="b64_json"
            )
            img_b64 = result['data'][0]["b64_json"]
        
        return img_b64

    def summarize(self, prompt):
        if self.debug:
            hint = "This is a test message from summarize()."
        else:
            messages = [{'role': 'system', 'content':'Summarize the scene description in the input content into a single sentence.'}]
            messages.append({'role': 'user', 'content': prompt})
            completion = openai.ChatCompletion.create(
                model = 'gpt-3.5-turbo',
                messages = messages,
            )

            hint = completion.choices[0].message.content
        return hint

class Conversation:
    def __init__(self, limit=5, debug=False) -> None:
        self.debug = debug
        self.messages = deque(maxlen=limit)
    def prepare_prompt(self, prompt):
        '''Get the user input and append it to prompt body. Return the prompt body.'''
        self.messages.append({"role": "user", "content": prompt})
        return list(self.messages)
    
    def append_response(self, response):
        '''Get the assistant response and append it to prompt body.'''
        self.messages.append({"role": "assistant", "content": response})
    
    def __len__(self):
        return num_tokens_from_messages(self.messages)
    
    def __repr__(self) -> str:
        return json.dumps(list(self.messages), indent=4, ensure_ascii=False)
    
    def __str__(self) -> str:
        return json.dumps(list(self.messages), indent=4, ensure_ascii=False)

def num_tokens_from_messages(messages, model="gpt-3.5-turbo"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":  # note: future models may deviate from this
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")

async def setup(client):
    await client.add_cog(Chatgpt(client))
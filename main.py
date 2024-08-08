import discord
from discord import app_commands
from chat import GeminiChatBot, ClaudeChatBot, EnhancedClaudeChatBot, DocumentHandler, Del_quote
from logger import ChatLog
from config import BOT_TOKEN, GOOGLE_API_KEY, ANTHROPIC_API_KEY, GEMINI_MODEL_NAME, CLAUDE_MODEL_NAME, INSTRUCTION, DB_FILE, TEMPERAURE, MAX_OUTPUT_TOKENS, COMMAND_TO_FILE

# 必要なモジュールとクラスをインポートする


class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

        new_activity = f"テスト"
        await client.change_presence(activity=discord.Game(new_activity))
        
        self.logger = ChatLog(DB_FILE)
        self.gemini_chatbot = GeminiChatBot(GEMINI_MODEL_NAME, GOOGLE_API_KEY, INSTRUCTION)
        # self.document_handler = DocumentHandler()
        self.claude_chatbot = EnhancedClaudeChatBot(CLAUDE_MODEL_NAME, ANTHROPIC_API_KEY, INSTRUCTION, COMMAND_TO_FILE, TEMPERAURE, MAX_OUTPUT_TOKENS)
        # self.claude_chatbot = ClaudeChatBot(CLAUDE_MODEL_NAME, ANTHROPIC_API_KEY, INSTRUCTION, TEMPERAURE, MAX_OUTPUT_TOKENS)

        await tree.sync()

    # Discordクライアントの設定と初期化を行う
    # ボットがオンラインになったときに呼び出されるon_readyメソッドを定義する
    # ログ、チャットボット、ドキュメントハンドラーを初期化する

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

        msg_id = message.id
        msg_content = message.content
        author = message.author.name
        author_id = message.author.id
        channel_id = message.channel.id
        timestamp = message.created_at

        if isinstance(message.channel, discord.TextChannel):
            channel = message.channel.name
        else:
            channel = str(message.channel)
    
        print(f'[{timestamp}] {channel} - {author}: {msg_content}', type(timestamp))

        # メッセージを受信したときに呼び出されるon_messageメソッドを定義する
        # メッセージの情報を取得し、ログに出力する

        if message.content.startswith('$') and (message.author != client.user):
            await message.channel.typing()  

            l_messages = self.logger.get_latest_messages(channel_id, count=10)
            
            l_chatlog = []
            """
            for i in l_messages:
                if i[2] == str(client.user).split("#")[0]:
                    l_chatlog.append({"role":"model", "parts":[i[1]], "username":i[2]})
                else:
                    if i[1][0]!="$":
                        l_chatlog.append({"role":"user", "parts":[i[1]], "username":i[2]})
                    else:
                        l_chatlog.append({"role":"user", "parts":[i[1][1:]], "username":i[2]})
            """

            l_temp = []
            b_first = True
            i_rooped = 0
            message_edited = None
            for talk in self.claude_chatbot.chat(msg_content, l_chatlog):
                print(talk, end='')
                l_temp.append(talk)
                i_rooped += 1

                if b_first:
                    message_edited = await message.channel.send('考え中…。')
                    b_first = False
                    await message.channel.typing()
                elif i_rooped % 10 == 0:
                    await message_edited.edit(content = "".join(l_temp))
                    await message.channel.typing()  

            await message_edited.edit(content = Del_quote("".join(l_temp)))
            await message_edited.add_reaction("\N{WINKING FACE}")

            self.logger.add_message(msg_id, msg_content, author, author_id, channel, channel_id, timestamp)

        # '$'で始まるメッセージに対して、チャットボットとの会話を行う
        # 最新のメッセージを取得し、チャットログを作成する
        # チャットボットからの応答をリアルタイムで編集しながら表示する
        # 最後に応答が完了したら、ウィンク絵文字をリアクションとして追加する
        # メッセージをログに追加する

        else:
            self.logger.add_message(msg_id, msg_content, author, author_id, channel, channel_id, timestamp)
            return

    # '$'で始まらないメッセージはログに追加するだけで何もしない

    async def on_message_edit(self, before, after):
        msg_id = after.id
        msg_content = after.content
        author = after.author.name
        author_id = after.author.id
        channel_id = after.channel.id
        timestamp = after.created_at

        if isinstance(after.channel, discord.TextChannel):
            channel = after.channel.name
        else:
            channel = str(after.channel)

        # print(str(after.id), after.content, after.edited_at)

        self.logger.update_message_content(msg_id, msg_content)

    # メッセージが編集されたときに呼び出されるon_message_editメソッドを定義する
    # 編集後のメッセージの情報を取得し、ログを更新する

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
tree = app_commands.CommandTree(client)

# Discordクライアントのインテントを設定し、クライアントとコマンドツリーを初期化する

@tree.command(name='chat_gemini', description='Gemini ChatBotと会話します')
async def chat_gemini(interaction: discord.Interaction, text: str):
    await interaction.response.defer()
    l_messages = client.logger.get_latest_messages(interaction.channel_id, count=10)
    
    l_chatlog = []
    for i in l_messages:
        if i[2] == str(client.user).split("#")[0]:
            l_chatlog.append({"role":"model", "parts":[i[1]], "username":i[2]})
        else:
            l_chatlog.append({"role":"user", "parts":[i[1]], "username":i[2]})
    
    l_temp = []
    for talk in client.gemini_chatbot.chat(text, l_chatlog):
        l_temp.append(talk)
    
    await interaction.followup.send("".join(l_temp))

# /chat_geminiコマンドを定義する
# Gemini ChatBotとの会話を行う
# 最新のメッセージを取得し、チャットログを作成する
# チャットボットからの応答を送信する

@tree.command(name='chat_claude', description='Claude ChatBotと会話します')
async def chat_claude(interaction: discord.Interaction, text: str):
    await interaction.response.defer() # 応答を遅延させる
    l_messages = client.logger.get_latest_messages(interaction.channel_id, count=10)
    
    l_chatlog = []
    for i in l_messages:
        if i[2] == str(client.user).split("#")[0]:
            l_chatlog.append({"role":"model", "parts":[i[1]], "username":i[2]})
        else:
            l_chatlog.append({"role":"user", "parts":[i[1]], "username":i[2]})
    
    l_temp = []
    for talk in client.claude_chatbot.chat(text, l_chatlog):
        l_temp.append(talk)
    
    await interaction.followup.send("".join(l_temp))

# /chat_claudeコマンドを定義する
# Claude ChatBotとの会話を行う
# 最新のメッセージを取得し、チャットログを作成する
# チャットボットからの応答を送信する

@tree.command(name='viewlog', description='ログを表示します')
async def viewlog(interaction: discord.Interaction):
    await interaction.response.send_message("こんにちは")
    i_channel_id = interaction.channel_id
    print(i_channel_id, type(i_channel_id))
    l_messages = client.logger.get_latest_messages(i_channel_id)
    print(len(l_messages))
    for i in l_messages:
        print({"role":"user", "parts":i[1]})

# /viewlogコマンドを定義する
# ログを表示する（実装は不完全）

@tree.command(name='showlog', description='直近のログを表示します')
async def showlog(interaction: discord.Interaction, count: int = 10):
    await interaction.response.defer(ephemeral=True)  # 応答を遅延させ、実行したユーザーにのみ表示する
    i_channel_id = interaction.channel_id
    print(i_channel_id, type(i_channel_id))
    l_messages = client.logger.get_latest_messages(i_channel_id, count)
    print(len(l_messages))
    log_text = ""
    for i in reversed(l_messages):
        author_name = i[2]
        if author_name == client.user.name:
            author_name = "BOT"
        log_text += f"{author_name}: {i[1]}\n"
    
    if log_text:
        await interaction.followup.send(f"直近の{count}件のログ:\n{log_text}", ephemeral=True)
    else:
        await interaction.followup.send("ログがありません。", ephemeral=True)

# /showlogコマンドを定義する
# 直近のログを指定された件数分表示する
# ログがある場合は、ユーザー名とメッセージ内容を含むログテキストを送信する
# ログがない場合は、ログがないことを示すメッセージを送信する

if __name__=="__main__":
    client.run(BOT_TOKEN)

# プログラムのエントリーポイント
# Discordクライアントを起動する
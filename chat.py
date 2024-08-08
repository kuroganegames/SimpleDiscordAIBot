import google.generativeai as genai
from anthropic import Anthropic

class ChatBot:
    def __init__(self, model_name, api_key, instruction, temperature=0.5, max_output_tokens=2048):
        self.model_name = model_name
        self.api_key = api_key
        self.instruction = instruction
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

    def chat(self, text, l_chatlog=[]):
        raise NotImplementedError("Subclass must implement abstract method")

class GeminiChatBot(ChatBot):
    def chat(self, text, l_chatlog=[]):
        genai.configure(api_key=self.api_key)
        
        generation_config = {
            "temperature": self.temperature,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": self.max_output_tokens,
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
        ]

        model = genai.GenerativeModel(model_name=self.model_name,
                                      generation_config=generation_config,
                                      safety_settings=safety_settings)

        reply_template = {
            "role":"user",
            "type":"question",
            "username":"ユーザー",
            "content": "天気は？",
        }

        inst_prompt = f"{self.instruction}以下の最後の会話ログを元に返答してください。"
        
        l_chatlog.reverse()
        text_merged = ""
        for i_chatlog in l_chatlog:
            if i_chatlog["role"] == "model":
                reply_template["role"] = "model"
                reply_template["type"] = "answer"
                reply_template["username"] = "KuroBot"
                reply_template["content"] = i_chatlog["parts"][0]
                text_merged += "出力:{}\n".format(str(reply_template))
            else:
                reply_template["role"] = "user"
                reply_template["type"] = "question"
                reply_template["username"] = i_chatlog["username"]
                reply_template["content"] = i_chatlog["parts"][0]
                text_merged += "メッセージ:{}\n".format(str(reply_template))
            
        text_merged = inst_prompt + "\n" + text_merged + "出力:{\"role\":\"model\", \"type\",:\"answer\", \"username\":\"KuroBot\", \"content\":\""

        response = model.generate_content(text_merged, stream=True)
        response_text = "" 
        for chunk in response:
            try:
                if chunk:
                    content = chunk.text
                    if content:
                        response_text += content
                        yield content
            except:
                pass

class ClaudeChatBot(ChatBot):
    def chat(self, text, l_chatlog=[], additional_instruction=""):
        if text.startswith("$"):
            text = text[1:]
        client = Anthropic(api_key=self.api_key)

        l_chatlog.reverse()
        messages = []
        for i_chatlog in l_chatlog:
            messages.append({
                "role": i_chatlog["role"],
                "content": i_chatlog["parts"][0],
            })
        
        messages.append({
            "role": "user", 
            "content": "{}\n{}".format(self.instruction+additional_instruction, text),
        })

        """
        stream = client.messages.create(
            max_tokens=1024,
            messages=messages,
            model=self.model_name,
            stream=True,
        )

        response_text = ""
        for event in stream:
            chunk = event.type
            if chunk:
                response_text += chunk
                yield chunk
        """ 
        with client.messages.stream(
                max_tokens=self.max_output_tokens,
                messages=messages,
                model=self.model_name,
                temperature=self.temperature,
                system=self.instruction,
            ) as stream:
            response_text = ""
            for text in stream.text_stream:
                response_text += text
                yield text


class DocumentHandler:
    def __init__(self):
        self.documents = {
            "anthropic-tools": """
            [Full text of anthropic-tools.md, not pasted here for brevity]
            """,
            # Add more documents here as needed
        }

    def get_document(self, doc_name):
        return self.documents.get(doc_name, None)

# ドキュメントを管理するDocumentHandlerクラスを定義する
# ドキュメントの内容を辞書形式で保持し、名前で取得できるようにする
    
def documentLoader(dir_path):
    try:
        if dir_path == None:
            return "Document not found.", False
        else:
            with open(dir_path, "r", encoding="utf-8") as f:
                document = f.read()
                return document, True
    except:
        return "Document not found.", False

def Del_quote(text):
    if "```" == text[:3]:
        return text[3:-3]
    else:
        return text
    
class EnhancedClaudeChatBot(ClaudeChatBot):
    def __init__(self, model_name, api_key, instruction, command_to_file, temperature=0.5, max_output_tokens=2048):
        super().__init__(model_name, api_key, instruction, temperature, max_output_tokens)
        # self.document_handler = DocumentHandler()

        self.command_to_file = command_to_file
    
    def chat(self, text, l_chatlog=[]):
        doc_name = ""
        document = ""
        additional_instruction = ""
        doc_load_success = False

        command = text[:2]
        question = text[2:]
        if command in self.command_to_file:
            doc_name = self.command_to_file[command]["file"]
            additional_instruction = self.command_to_file[command]["instruction"]
            document, doc_load_success = documentLoader(doc_name)
            

        #if text.startswith(\"$u\"):
        #    doc_name = r\"G:\devs\python\discord\geminibot\docs\UdonSharp_u2022.md\"
        #    document, doc_load_success = documentLoader(doc_name)

        
        
        # document = self.document_handler.get_document(doc_name)
        if doc_load_success:
            print(f"Document '{doc_name}' was loaded.")
            text = f"""
            <question>
            {question}
            </question>

            <doc>
            {document}
            </doc>
            """

            print("<question>\n{}\n</question>\n\n<doc>{}</doc>".format(question, document[:150]))
        else:
            print(f"Document '{doc_name}' not found.")
            text = question


        return super().chat(text, l_chatlog, additional_instruction=additional_instruction)

# ClaudeChatBotを拡張したEnhancedClaudeChatBotクラスを定義する
# ドキュメントを参照しながらチャットできるように機能を追加する
BOT_TOKEN = ""
GEMINI_MODEL_NAME = "gemini-1.0-pro-latest"
GOOGLE_API_KEY = ""
CLAUDE_MODEL_NAME = "claude-3-haiku-20240307"
ANTHROPIC_API_KEY = ""
INSTRUCTION = "Respond only in Japanese. Responses should be in Discord format with markdown.\n"
DB_FILE = "logtest1.db"
TEMPERAURE = 0.5
MAX_OUTPUT_TOKENS = 2048
COMMAND_TO_FILE = {
                "$u": {
                    "file":r"docs\UdonSharp_u2022.md",
                    "instruction":"UdonSharpのドキュメントを参照してください。",
                    "model":"claude-3-haiku-20240307",
                    "api_key":ANTHROPIC_API_KEY
                    },
                "$sonnet": {
                    "file":None,
                    "instruction":None,
                    "model":"claude-3-sonnet-20240229",
                    "api_key":ANTHROPIC_API_KEY
                    },
                "$opus": {
                    "file":None,
                    "instruction":None,
                    "model":"claude-3-opus-20240229",
                    "api_key":ANTHROPIC_API_KEY
                    },
                # Add more command-file mappings here as needed
                }
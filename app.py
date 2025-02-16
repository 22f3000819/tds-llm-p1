# app.py
# /// script
# dependencies = [
#   "requests",
#   "fastapi",
#   "uvicorn",
#   "python-dateutil",
#   "pandas",
#   "db-sqlite3",
#   "scipy",
#   "pybase64",
#   "python-dotenv",
#   "httpx",
#   "markdown",
#   "duckdb",
#   "beautifulsoup4",
#   "pillow",
#   "faster-whisper",
# ]
# ///

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from application.tasksA import *
from application.tasksB import *
import requests
from dotenv import load_dotenv
import os
import re
import httpx
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


app = FastAPI()
load_dotenv()

@app.get("/ask")
def ask(prompt: str):
    result = get_completions(prompt)
    return result

openai_api_chat  = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions" # for testing
openai_api_key = os.getenv("AIPROXY_TOKEN")

headers = {
    "Authorization": f"Bearer {openai_api_key}",
    "Content-Type": "application/json",
}

function_definitions_llm = [
    {
        "name": "A1",
        "description": "Run a Python script from a given URL, passing an email as the argument.",
        "parameters": {
            "type": "object",
            "properties": {
                "script_url": {"type": "string", "pattern": r"https?://.*\.py"},
            },
            "required": ["script_url"]
        }
    },
    {
        "name": "A2",
        "description": "Format a markdown file using a specified version of Prettier.",
        "parameters": {
            "type": "object",
            "properties": {
                "prettier_version": {"type": "string", "pattern": r"prettier@\d+\.\d+\.\d+"},
                "filename": {"type": "string", "pattern": r".*/(.*\.md)"}
            },
            "required": ["prettier_version", "filename"]
        }
    },
    {
        "name": "A3",
        "description": "Count the number of occurrences of a specific weekday in a date file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "pattern": r"/data/.*dates.*\.txt"},
                "targetfile": {"type": "string", "pattern": r"/data/.*/(.*\.txt)"},
                "weekday": {"type": "integer", "pattern": r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)"}
            },
            "required": ["filename", "targetfile", "weekday"]
        }
    },
    {
        "name": "A4",
        "description": "Sort a JSON contacts file and save the sorted version to a target file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.json)",
                },
                "targetfile": {
                    "type": "string",
                    "pattern": r".*/(.*\.json)",
                }
            },
            "required": ["filename", "targetfile"]
        }
    },
    {
        "name": "A5",
        "description": "Retrieve the most recent log files from a directory and save their content to an output file.",
        "parameters": {
            "type": "object",
            "properties": {
                "log_dir_path": {
                    "type": "string",
                    "pattern": r".*/logs",
                    "default": "/data/logs"
                },
                "output_file_path": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/logs-recent.txt"
                },
                "num_files": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 10
                }
            },
            "required": ["log_dir_path", "output_file_path", "num_files"]
        }
    },
    {
        "name": "A6",
        "description": "Generate an index of documents from a directory and save it as a JSON file.",
        "parameters": {
            "type": "object",
            "properties": {
                "doc_dir_path": {
                    "type": "string",
                    "pattern": r".*/docs",
                    "default": "/data/docs"
                },
                "output_file_path": {
                    "type": "string",
                    "pattern": r".*/(.*\.json)",
                    "default": "/data/docs/index.json"
                }
            },
            "required": ["doc_dir_path", "output_file_path"]
        }
    },
    {
        "name": "A7",
        "description": "Extract the sender's email address from a text file and save it to an output file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/email.txt"
                },
                "output_file": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/email-sender.txt"
                }
            },
            "required": ["filename", "output_file"]
        }
    },
    {
        "name": "A8",
        "description": "Generate an image representation of credit card details from a text file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/credit-card.txt"
                },
                "image_path": {
                    "type": "string",
                    "pattern": r".*/(.*\.png)",
                    "default": "/data/credit-card.png"
                }
            },
            "required": ["filename", "image_path"]
        }
    },
    {
        "name": "A9",
        "description": "Find similar comments from a text file and save them to an output file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/comments.txt"
                },
                "output_filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/comments-similar.txt"
                }
            },
            "required": ["filename", "output_filename"]
        }
    },
    {
        "name": "A10",
        "description": "Identify high-value (gold) ticket sales from a database and save them to a text file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.db)",
                    "default": "/data/ticket-sales.db"
                },
                "output_filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/ticket-sales-gold.txt"
                },
                "query": {
                    "type": "string",
                    "pattern": "SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'"
                }
            },
            "required": ["filename", "output_filename", "query"]
        }
    },
    {
        "name": "B1",
        "description": "Check if filepath starts with /data",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "pattern": r".*",
                    # "description": "Filepath must start with /data to ensure secure access."
                }
            },
            "required": ["filepath"]
        }
    },
    {
        "name": "B3",
        "description": "Download content from a URL and save it to the specified path.",
        "parameters": {
            "type": "object",
            "properties": {
                "api_url": {
                    "type": "string",
                    "pattern": r"https?://.*",
                    "description": "URL to download content from."
                },
                "save_path": {
                    "type": "string",
                    "pattern": r".*/.*",
                    "description": "Path to save the downloaded content."
                }
            },
            "required": ["url", "save_path"]
        }
    },
    {
        "name": "B4",
        "description": "Clone a Git repository, optionally modify files, commit changes, and push if needed.",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_url": {
                    "type": "string",
                    "pattern": "https?://.*",
                    "description": "URL of the Git repository to clone."
                },
                "repo_path": {
                    "type": "string",
                    "pattern": ".*/.*",
                    "description": "Path to clone the repository into. If not provided, defaults to /data/{repo_name}.",
                    "default": None
                },
                "commit_message": {
                    "type": "string",
                    "description": "Commit message for the changes.",
                    "default": "Updated files"
                },
                "file_changes": {
                    "type": "array",
                    "description": "List of files to modify before committing.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Relative path of the file to modify."
                            },
                            "content": {
                                "type": "string",
                                "description": "New content to write into the file."
                            }
                        },
                        "required": ["file_path", "content"]
                    },
                    "default": []
                },
                "push_changes": {
                    "type": "boolean",
                    "description": "Whether to push the commit to the remote repository.",
                    "default": False
                }
            },
            "required": ["repo_url"]
        }
    },
    {
        "name": "B5",
        "description": "Execute a SQL query on a specified database file and save the result to an output file.",
        "parameters": {
            "type": "object",
            "properties": {
                "db_path": {
                    "type": "string",
                    "pattern": r".*/(.*\.db)",
                    "description": "Path to the SQLite database file."
                },
                "query": {
                    "type": "string",
                    "description": "SQL query to be executed on the database."
                },
                "output_filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "description": "Path to the file where the query result will be saved."
                }
            },
            "required": ["db_path", "query", "output_filename"]
        }
    },
    {
        "name": "B6",
        "description": "Scrape a website and extract data in different formats.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "pattern": "https?://.*",
                    "description": "URL of the website to scrape."
                },
                "output_filename": {
                    "type": "string",
                    "pattern": ".*/.*",
                    "description": "Path to save the extracted content."
                },
                "extract_mode": {
                    "type": "string",
                    "enum": ["html", "text", "json", "element"],
                    "description": "Extraction mode: 'html' (full page), 'text' (clean text), 'json' (if API), or 'element' (specific parts).",
                    "default": "html"
                },
                "element_selector": {
                    "type": "string",
                    "description": "CSS selector to extract specific elements (required if extract_mode='element').",
                    "nullable": True
                },
                "headers": {
                    "type": "object",
                    "description": "Optional request headers (e.g., User-Agent).",
                    "nullable": True
                }
            },
            "required": ["url", "output_filename", "extract_mode"]
        }
    },
    {
        "name": "B7",
        "description": "Compress or resize an image while optionally changing its format.",
        "parameters": {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Path to the input image file."
                },
                "output_path": {
                    "type": "string",
                    "description": "Path to save the processed image."
                },
                "resize": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    },
                    "minItems": 2,
                    "maxItems": 2,
                    "description": "Target size as [width, height] while maintaining aspect ratio."
                },
                "format": {
                    "type": "string",
                    "enum": ["JPEG", "PNG", "WEBP"],
                    "description": "Optional format to convert the image to. Defaults to the input image format."
                },
                "quality": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Quality factor (for JPEG format only). Defaults to 85."
                }
            },
            "required": ["image_path", "output_path"]
        }
    },
    {
        "name": "B8",
        "description": "Transcribe an audio file using the faster-whisper model.",
        "parameters": {
            "type": "object",
            "properties": {
                "audio_path": {
                    "type": "string",
                    "pattern": r".*/(.*\.mp3)",
                    "description": "Path to the MP3 file to be transcribed."
                },
                "output_filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "description": "Path to the text file where the transcription will be saved."
                },
                "model_size": {
                    "type": "string",
                    "enum": ["tiny", "base", "small", "medium"],
                    "description": "The size of the faster-whisper model to use. Defaults to 'small'."
                },
                "language": {
                    "type": "string",
                    "description": "Optional language code (e.g., 'en' for English). If not provided, auto-detection will be used."
                }
            },
            "required": ["audio_path", "output_filename"]
        }
    },
    {
        "name": "B9",
        "description": "Convert a Markdown file to HTML and save the result to the specified output path.",
        "parameters": {
            "type": "object",
            "properties": {
                "md_path": {
                    "type": "string",
                    "pattern": ".*/(.*\\.md)",
                    "description": "Path to the Markdown file to be converted."
                },
                "output_path": {
                    "type": "string",
                    "pattern": ".*/.*",
                    "description": "Path where the converted file will be saved."
                },
                "extensions": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Optional list of Markdown extensions to enable, such as 'extra', 'codehilite', or 'toc'."
                }
            },
            "required": ["md_path", "output_path"]
        }
    }
]

def get_completions(prompt: str):
    with httpx.Client(timeout=20) as client:
        response = client.post(
            f"{openai_api_chat}",
            headers=headers,
            json=
                {
                    "model": "gpt-4o-mini",
                    "messages": [
                                    {"role": "system", "content": "You are a function classifier that extracts structured parameters from queries. The queries may be in any language. If in filepaths do not start with /data/, do not append /data/ at the beginning of filepaths by yourself. Send the exact path given only."},
                                    {"role": "user", "content": prompt}
                                ],
                    "tools": [
                                {
                                    "type": "function",
                                    "function": function
                                } for function in function_definitions_llm
                            ],
                    "tool_choice": "auto"
                },
        )
    print(response.json()["choices"][0]["message"]["tool_calls"][0]["function"])
    return response.json()["choices"][0]["message"]["tool_calls"][0]["function"]


# Placeholder for task execution
@app.post("/run")
async def run_task(task: str):
    try:
        print('Trying to execute task')
        # Placeholder logic for executing tasks
        # Replace with actual logic to parse task and execute steps
        # Example: Execute task and return success or error based on result
        # llm_response = function_calling(tast), function_name = A1
        response = get_completions(task)
        print(response)
        task_code = response['name']
        arguments = response['arguments']

        print('identifying task')
        if "A1"== task_code:
            print('task a1 identified')
            await A1(**json.loads(arguments))
            print('task a1 done')
        if "A2"== task_code:
            await A2(**json.loads(arguments))
        if "A3"== task_code:
            A3(**json.loads(arguments))
        if "A4"== task_code:
            A4(**json.loads(arguments))
        if "A5"== task_code:
            A5(**json.loads(arguments))
        if "A6"== task_code:
            A6(**json.loads(arguments))
        if "A7"== task_code:
            A7(**json.loads(arguments))
        if "A8"== task_code:
            A8(**json.loads(arguments))
        if "A9"== task_code:
            await A9(**json.loads(arguments))
        if "A10"== task_code:
            A10(**json.loads(arguments))


        if "B1"== task_code:
            B1(**json.loads(arguments))
        if "B3" == task_code:
            B3(**json.loads(arguments))
        if "B4" == task_code:
            B4(**json.loads(arguments))
        if "B5" == task_code:
            B5(**json.loads(arguments))
        if "B6" == task_code:
            B6(**json.loads(arguments))
        if "B7" == task_code:
            B7(**json.loads(arguments))
        if "B8" == task_code:
            B8(**json.loads(arguments))
        if "B9" == task_code:
            B9(**json.loads(arguments))
        return {"message": f"{task_code} Task '{task}' executed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Placeholder for file reading
@app.get("/read", response_class=PlainTextResponse)
async def read_file(path: str = Query(..., description="File path to read")):
    try:
        with open(path, "r") as file:
            return file.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
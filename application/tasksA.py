from fastapi import HTTPException
import sqlite3
import subprocess
from dateutil.parser import parse
from datetime import datetime
import json
from pathlib import Path
import os
import requests
import shutil
from scipy.spatial.distance import cosine
from dotenv import load_dotenv
import numpy as np
from .tasksB import B1
load_dotenv()

AIPROXY_TOKEN = os.getenv('AIPROXY_TOKEN')

async def A1(email="22f3000819@ds.study.iitm.ac.in", script_url="https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"):
    try:
        # Check if `uv` is installed
        if not shutil.which("uv"):
            print("uv is not installed. Installing uv...")
            install_process = subprocess.run(
                ["pip", "install", "uv"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if install_process.returncode != 0:
                raise HTTPException(status_code=500, detail=f"Failed to install uv: {install_process.stderr}")

        print("uv is installed. Running script...")

        process = subprocess.Popen(
            ["uv", "run", script_url, email],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print(f"Error running script: {stderr}")
            raise HTTPException(status_code=500, detail=f"Error running script: {stderr}")

        print("Script executed successfully")
        return {"message": "Script executed successfully", "stdout": stdout}

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Subprocess error: {e.stderr}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# A1()
async def A2(prettier_version="prettier@3.4.2", filename="/data/format.md"):
    B1(filepath=filename)
    command = ["npx", "--yes", prettier_version, "--write", filename]
    try:
        subprocess.run(command, check=True)
        print("Prettier executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

def A3(filename='/data/dates.txt', targetfile='/data/dates-wednesdays.txt', weekday=2):
    input_file = filename
    output_file = targetfile
    weekday = weekday
    weekday_count = 0
    B1(filepath=input_file)
    B1(filepath=targetfile)
    with open(input_file, 'r') as file:
        weekday_count = sum(1 for date in file if parse(date).weekday() == int(weekday)-1)


    with open(output_file, 'w') as file:
        file.write(str(weekday_count))

def A4(filename="/data/contacts.json", targetfile="/data/contacts-sorted.json"):
    B1(filepath=filename)
    B1(filepath=targetfile)
    # Load the contacts from the JSON file
    with open(filename, 'r') as file:
        contacts = json.load(file)

    # Sort the contacts by last_name and then by first_name
    sorted_contacts = sorted(contacts, key=lambda x: (x['last_name'], x['first_name']))

    # Write the sorted contacts to the new JSON file
    with open(targetfile, 'w') as file:
        json.dump(sorted_contacts, file, indent=4)

def A5(log_dir_path='/data/logs', output_file_path='/data/logs-recent.txt', num_files=10):
    B1(filepath=log_dir_path)
    B1(filepath=output_file_path)
    log_dir = Path(log_dir_path)
    output_file = Path(output_file_path)

    # Get list of .log files sorted by modification time (most recent first)
    log_files = sorted(log_dir.glob('*.log'), key=os.path.getmtime, reverse=True)[:num_files]

    # Read first line of each file and write to the output file
    with output_file.open('w') as f_out:
        for log_file in log_files:
            with log_file.open('r') as f_in:
                first_line = f_in.readline().strip()
                f_out.write(f"{first_line}\n")

def A6(doc_dir_path='/data/docs', output_file_path='/data/docs/index.json'):
    B1(filepath=doc_dir_path)
    B1(filepath=output_file_path)
    docs_dir = doc_dir_path
    output_file = output_file_path
    index_data = {}
    print(docs_dir, output_file)
    # Walk through all files in the docs directory
    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md'):
                # print(file)
                file_path = os.path.join(root, file)
                # Read the file and find the first occurrence of an H1
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('# '):
                            # Extract the title text after '# '
                            title = line[2:].strip()
                            # Get the relative path without the prefix
                            relative_path = os.path.relpath(file_path, docs_dir).replace('\\', '/')
                            index_data[relative_path] = title
                            break  # Stop after the first H1
    # Write the index data to index.json
    # print(index_data)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=4)

def A7(filename='/data/email.txt', output_file='/data/email-sender.txt'):
    B1(filepath=filename)
    B1(filepath=output_file)
    # Read the content of the email
    with open(filename, 'r') as file:
        email_content = file.readlines()

    sender_email = "sujay@gmail.com"
    for line in email_content:
        if "From" == line[:4]:
            sender_email = (line.strip().split(" ")[-1]).replace("<", "").replace(">", "")
            break

    # Get the extracted email address

    # Write the email address to the output file
    with open(output_file, 'w') as file:
        file.write(sender_email)

import base64
def png_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode('utf-8')
    return base64_string

def A8(filename='/data/credit_card.txt', image_path='/data/credit_card.png'):
    print('checking filename')
    B1(filepath=filename)
    print('checking image path')
    B1(filepath=image_path)
    # Construct the request body for the AIProxy call
    print('creating body')
    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "There may be multiple lines of texts in the image. Extract the line which has 8 or 12 or 16 digits one after the other and may have space in between. Then extract those 16 digits 1 by 1 from the left and create a string of length 16 having only those digits. Return only that string of digits and no other additional text. Just the string of digits."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{png_to_base64(image_path)}"
                        }
                    }
                ]
            }
        ]
    }
    print('creating headers')
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }
    print('making request')
    # Make the request to the AIProxy service
    response = requests.post("http://aiproxy.sanand.workers.dev/openai/v1/chat/completions",
                             headers=headers, data=json.dumps(body))
    print(f'got response {response.status_code}')
    # Extract the credit card number from the response
    result = response.json()
    # print(result); return None
    card_number = result['choices'][0]['message']['content'].replace(" ", "")
    print('writing to file')
    # Write the extracted card number to the output file
    with open(filename, 'w') as file:
        file.write(card_number)
    print('written')
# A8()

def get_embeddings(texts):
    """Fetch embeddings for a batch of texts in a single request."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }
    data = {
        "model": "text-embedding-3-small",
        "input": texts  # Send all comments at once
    }
    response = requests.post("http://aiproxy.sanand.workers.dev/openai/v1/embeddings", headers=headers, data=json.dumps(data))
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=f"Embeddings API request failed with status {response.status_code}: {response.text}")
    return np.array([emb["embedding"] for emb in response.json()["data"]])

async def A9(filename='/data/comments.txt', output_filename='/data/comments-similar.txt'):
    B1(filepath=filename)
    B1(filepath=output_filename)
    """Find the most similar pair of comments using embeddings."""
    print('Reading comments...')
    with open(filename, 'r') as f:
        comments = [line.strip() for line in f.readlines()]

    print(f'Total comments: {len(comments)}')

    if len(comments) < 2:
        print("Not enough comments to compare.")
        return

    print('Fetching embeddings in a single request...')
    embeddings = get_embeddings(comments)
    similarity = np.dot(embeddings, embeddings.T)
    # Create mask to ignore diagonal (self-similarity)
    np.fill_diagonal(similarity, -np.inf)
    # Get indices of maximum similarity
    i, j = np.unravel_index(similarity.argmax(), similarity.shape)
    expected = "\n".join(sorted([comments[i], comments[j]]))
    with open(output_filename, 'w') as f:
        f.write(expected)

    print('Task completed.')

def A10(filename='/data/ticket-sales.db', output_filename='/data/ticket-sales-gold.txt', query="SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'"):
    B1(filepath=filename)
    B1(filepath=output_filename)
    # Connect to the SQLite database
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()

    # Calculate the total sales for the "Gold" ticket type
    cursor.execute(query)
    total_sales = cursor.fetchone()[0]

    # If there are no sales, set total_sales to 0
    total_sales = total_sales if total_sales else 0

    # Write the total sales to the file
    with open(output_filename, 'w') as file:
        file.write(str(total_sales))

    # Close the database connection
    conn.close()

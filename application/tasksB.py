# Phase B: LLM-based Automation Agent for DataWorks Solutions

# B1 & B2: Security Checks
import os
from fastapi import HTTPException
from urllib.parse import urlparse
import subprocess
import requests
from bs4 import BeautifulSoup
import json

def B1(filepath):
    abs_path = os.path.abspath(filepath)
    if not abs_path.startswith('/data/'):
        raise HTTPException(status_code=403, detail='Access to files outside /data is prohibited.')

# B3: Fetch Data from an API
def B3(api_url, save_path):
    B1(save_path)
    import csv
    import io
    import xml.etree.ElementTree as ET
    import yaml
    try:
        response = requests.get(api_url)
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=f"API request failed with status {response.status_code}: {response.text}")  # Raise an error for bad responses (4xx and 5xx)
        
        content_type = response.headers.get("Content-Type", "").lower()
        
        if "application/json" in content_type:
            data = response.json()
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        
        elif "text/xml" in content_type or "application/xml" in content_type:
            tree = ET.ElementTree(ET.fromstring(response.text))
            tree.write(save_path)
        
        elif "text/csv" in content_type:
            csv_reader = csv.reader(io.StringIO(response.text))
            with open(save_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(csv_reader)
        
        elif "text/plain" in content_type:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(response.text)
        
        elif "html" in content_type:
            soup = BeautifulSoup(response.text, "html.parser")
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(soup.prettify())  # Save a prettified HTML file
        
        elif "application/x-yaml" in content_type or "text/yaml" in content_type:
            yaml_data = yaml.safe_load(response.text)
            with open(save_path, "w", encoding="utf-8") as f:
                yaml.dump(yaml_data, f, default_flow_style=False)
        
        elif "application/pdf" in content_type or "image/" in content_type or "application/octet-stream" in content_type:
            with open(save_path, "wb") as f:
                f.write(response.content)  # Save binary data as a file
        
        else:
            with open(save_path, "wb") as f:
                f.write(response.content)  # Fallback for unknown formats
        
        print(f"Data saved to {save_path}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")

def run_command(command, cwd=None):
    """Helper function to execute a shell command and check for errors."""
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(command)}\nError: {result.stderr}")
    return result.stdout.strip()

def get_repo_name(repo_url):
    """Extracts the repository name from the URL."""
    return os.path.splitext(os.path.basename(urlparse(repo_url).path))[0]

def B4(repo_url, repo_path=None, commit_message="Updated files", file_changes=None, push_changes=False):
    """Clones a Git repository, makes changes, commits, and optionally pushes."""

    # Set default repo_path if not provided
    if repo_path is None:
        repo_name = get_repo_name(repo_url)
        repo_path = f"/data/{repo_name}"
    else:
        B1(repo_path)

    # Ensure repo_path exists
    os.makedirs(repo_path, exist_ok=True)

    # Clone the repository
    run_command(["git", "clone", repo_url, repo_path])

    # Apply file changes if provided
    if file_changes:
        for change in file_changes:
            file_path = os.path.join(repo_path, change["file_path"])
            with open(file_path, "w") as f:
                f.write(change["content"])
            
            # Add the modified file to git
            run_command(["git", "add", change["file_path"]], cwd=repo_path)

    # Commit the changes
    run_command(["git", "commit", "-m", commit_message], cwd=repo_path)

    # Optionally push the changes
    if push_changes:
        run_command(["git", "push"], cwd=repo_path)

# B5: Run SQL Query
def B5(db_path, query, output_filename):
    B1(db_path)
    import sqlite3, duckdb
    # Ensure database file exists
    if not os.path.isfile(db_path):
        raise FileNotFoundError(f"Database file not found: {db_path}")

    # Choose correct database engine
    if db_path.endswith('.db') or db_path.endswith('.sqlite') or db_path.endswith('.sqlite3'):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(query)
        result = cur.fetchall()
        conn.close()
    elif db_path.endswith('.duckdb'):
        conn = duckdb.connect(database=db_path, read_only=False)
        result = conn.execute(query).fetchall()
        conn.close()
    else:
        raise ValueError("Unsupported database type. Use a SQLite (.db) or DuckDB (.duckdb) file.")

    # Save result in a readable format
    with open(output_filename, 'w') as file:
        for row in result:
            file.write("\t".join(map(str, row)) + "\n")  # Tab-separated for readability

    return result

# B6: Web Scraping
def B6(url, output_filename, extract_mode="html", element_selector=None, headers=None):
    """
    Scrape a website and extract data based on the given mode.
    
    Args:
        url (str): The URL to scrape.
        output_filename (str): File path to save the extracted content.
        extract_mode (str): Extraction mode - 'html', 'text', 'json', or 'element'.
        element_selector (str, optional): CSS selector for extracting specific elements.
        headers (dict, optional): Custom headers for requests (e.g., User-Agent).
    """
    B1(filepath=output_filename)
    try:
        response = requests.get(url, headers=headers or {}, timeout=10)
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=f"API request failed with status {response.status_code}: {response.text}")

        if extract_mode == "json":
            try:
                data = response.json()  # Extract JSON data
            except ValueError as v:
                raise HTTPException(status_code=400, detail=f"{v}")
        
        elif extract_mode == "element":
            if not element_selector:
                raise HTTPException(status_code=400, detail="element_selector must be provided for element extraction.")
            soup = BeautifulSoup(response.text, "html.parser")
            data = "\n".join([el.get_text(strip=True) for el in soup.select(element_selector)])
        
        elif extract_mode == "text":
            soup = BeautifulSoup(response.text, "html.parser")
            data = soup.get_text(separator="\n", strip=True)  # Extract readable text
        
        else:  # Default to raw HTML
            data = response.text

        with open(output_filename, "w", encoding="utf-8") as file:
            file.write(data if isinstance(data, str) else json.dumps(data, indent=4))

        return data

    except requests.RequestException as e:
        raise HTTPException(status_code=response.status_code, detail=f"API request failed: {e}")

# B7: Image Processing
def B7(image_path, output_path, resize=None, format=None, quality=None):
    from PIL import Image
    
    B1(image_path)
    B1(output_path)
    
    img = Image.open(image_path)
    
    # Default format: Keep original
    if not format:
        format = img.format  # Use input image format if none is provided
    
    # Ensure valid quality value for JPEG
    if format.upper() == "JPEG":
        quality = quality if quality is not None else 85  # Default to 85 if not provided

    # Convert incompatible modes
    if format.upper() == "JPEG" and img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Resize while keeping aspect ratio
    if resize:
        img.thumbnail(resize)  # Maintains aspect ratio
    
    # Save with correct parameters
    save_kwargs = {"quality": quality} if format.upper() == "JPEG" else {}
    img.save(output_path, format=format, **save_kwargs)


# B8: Audio Transcription
def B8(audio_path, output_filename, model_size="small", language_code=None):
    from faster_whisper import WhisperModel

    B1(audio_path)
    B1(output_filename)
    model = WhisperModel(model_size, device="cpu")  # Allowing different model sizes
    segments, _ = model.transcribe(audio_path, language=language_code)
    transcript = " ".join(segment.text for segment in segments)

    with open(output_filename, "w") as file:
        file.write(transcript)


# B9: Markdown to HTML Conversion
def B9(md_path, output_path, extensions=None):
    import markdown
    B1(md_path)
    B1(output_path)
    if extensions is None:
        extensions = ["extra", "codehilite", "toc"]  # Some common extensions

    with open(md_path, "r", encoding="utf-8") as file:
        html = markdown.markdown(file.read(), extensions=extensions)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(html)
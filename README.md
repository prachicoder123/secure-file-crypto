# Secure File Encryption & Decryption Tool

A password-based file encryption/decryption web app using **AES-256-GCM**, with a simple local UI you run in VS Code.

## Tech Stack
- **Python 3** + **Flask** — local web server / UI
- **cryptography** library — AES-256-GCM encryption, PBKDF2-HMAC-SHA256 key derivation
- HTML / CSS / JS — front end

## How it works
- Your password is never stored. It's run through **PBKDF2-HMAC-SHA256** (200,000 iterations) with a random 16-byte salt to derive a 256-bit AES key.
- Files are encrypted with **AES-256-GCM**, which provides both confidentiality *and* integrity — if a file is corrupted or tampered with, or the password is wrong, decryption fails safely with a clear error instead of returning garbage data.
- Each encrypted `.enc` file stores: a format header, the random salt, a random nonce, and the ciphertext (with its authentication tag). The salt/nonce are safe to store alongside the ciphertext — only the password can derive the correct key.
- Uploaded files are processed in memory/temp folders and deleted from the server immediately after each operation — nothing lingers on disk.

## Project Structure
```
secure-file-crypto/
├── app.py                
├── crypto_utils.py        
├── requirements.txt       
├── templates/
│   └── index.html          
├── static/
│   ├── style.css            
│   └── script.js            
├── uploads/                 
├── encrypted/                
└── decrypted/                 
```

## Setup & Run in VS Code

### 1. Open the project
Open the `secure-file-crypto` folder in VS Code: `File → Open Folder…`

### 2. Open a terminal in VS Code
`Terminal → New Terminal` (or `` Ctrl+` ``)

### 3. Create a virtual environment (recommended)
```bash
python -m venv venv
```
Activate it:
- **Windows**: `venv\Scripts\activate`
- **macOS/Linux**: `source venv/bin/activate`

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the app
```bash
python app.py
```
You should see:
```
Secure File Encryption & Decryption Tool
Running at: http://127.0.0.1:5000
```

### 6. Open it in your browser
Go to **http://127.0.0.1:5000** (Ctrl/Cmd-click the link in the VS Code terminal, or paste it into your browser).

### 7. Use it
- **Encrypt tab**: choose any file, enter a password, click **Encrypt File** → downloads `yourfile.ext.enc`
- **Decrypt tab**: choose the `.enc` file, enter the *same* password, click **Decrypt File** → downloads the original file

## Notes
- If port 5000 is already in use, change the port at the bottom of `app.py` (`app.run(host="127.0.0.1", port=5000, ...)`) to something like `5001`.
- Max upload size is capped at 100 MB by default — change `MAX_FILE_SIZE_MB` in `app.py` if you need more.
- This is a Flask **development server**, fine for local/personal use. Don't expose it to the public internet as-is.
- Forgetting the password means the file **cannot** be recovered — there is no backdoor by design.

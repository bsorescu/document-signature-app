import os
from flask import Flask, request, render_template, send_file
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends.openssl import backend as openssl_backend
from cryptography.hazmat.primitives.serialization import load_pem_public_key

app = Flask(__name__)

# Load OpenSSL engine
openssl_backend.activate_builtin_random()
openssl_backend.activate_osrandom_engine()
openssl_backend.activate_engine('pkcs11', 'pkcs11_section')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sign', methods=['POST'])
def sign_document():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        file_content = file.read()
        
        # Sign the document using the USB token
        try:
            private_key = openssl_backend.load_private_key_from_token('pkcs11:token=MyToken')
            signature = private_key.sign(
                file_content,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Save the signature
            signature_path = f"signatures/{file.filename}.sig"
            os.makedirs(os.path.dirname(signature_path), exist_ok=True)
            with open(signature_path, "wb") as f:
                f.write(signature)
            
            return send_file(signature_path, as_attachment=True)
        except Exception as e:
            return f"Error signing document: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
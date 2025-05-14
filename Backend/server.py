from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from facenet_pytorch import InceptionResnetV1, MTCNN
from web3 import Web3
from web3.exceptions import ContractLogicError
import base64
import hashlib
import json
import logging
from scipy.spatial.distance import cosine
import torch

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.DEBUG)

mtcnn = MTCNN(thresholds=[0.7, 0.7, 0.7], min_face_size=50, keep_all=False, device='cpu')
resnet = InceptionResnetV1(pretrained='vggface2').eval()

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
if not w3.is_connected():
    app.logger.error("Failed to connect to Ganache at http://127.0.0.1:7545")
    raise Exception("Ganache not running")
contract_address = "0x4d443D90Ab4361329C63Cd3150835183E5c94843"  # Update after redeploy
with open('../blockchain/build/contracts/FaceRegistry.json') as f:
    abi = json.load(f)['abi']
contract = w3.eth.contract(address=contract_address, abi=abi)
account = w3.eth.accounts[0]

registered_embeddings = {}

def preprocess_image(image):
    img = cv2.resize(image, (160, 160))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.convertScaleAbs(img, alpha=1.3, beta=10)
    return img

def process_image(image_data):
    try:
        app.logger.debug("Decoding image data")
        img = base64.b64decode(image_data.split(',')[1])
        np_img = np.frombuffer(img, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        if img is None:
            app.logger.debug("Failed to decode image")
            return None
        img = preprocess_image(img)
        app.logger.debug("Detecting faces with MTCNN")
        faces = mtcnn(img)
        if faces is None or len(faces) == 0:
            app.logger.debug("No face detected, retrying with lower thresholds")
            mtcnn_temp = MTCNN(thresholds=[0.5, 0.5, 0.5], min_face_size=30, keep_all=False)
            faces = mtcnn_temp(img)
            if faces is None or len(faces) == 0:
                app.logger.debug("Still no face detected")
                return None
        face = faces[0]
        app.logger.debug(f"Face tensor shape: {face.shape}")
        if face.shape[0] != 3:
            app.logger.debug(f"Face has {face.shape[0]} channels, converting to RGB")
            face = torch.stack([face.squeeze(0)] * 3, dim=0)
        embedding = resnet(face.unsqueeze(0)).detach().numpy()[0]
        app.logger.debug(f"Embedding generated: {embedding[:5]}... (length: {len(embedding)})")
        return embedding
    except Exception as e:
        app.logger.error(f"Error in process_image: {str(e)}")
        return None

def embedding_to_hash(embedding):
    return hashlib.sha256(embedding.tobytes()).hexdigest()

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        app.logger.debug(f"Received registration data: {data.keys()}")
        image = data.get('image')
        name = data.get('name')
        age = data.get('age')
        gender = data.get('gender')

        if not all([image, name, age, gender]):
            app.logger.error("Missing required fields")
            return jsonify({'message': 'Missing required fields'}), 400

        app.logger.debug(f"Processing age: {age}")
        age = int(age)
        app.logger.debug("Processing image for face detection")
        embedding = process_image(image)
        if embedding is None:
            app.logger.error("Face detection failed")
            return jsonify({'message': 'Face not detected'}), 400
        
        face_hash = embedding_to_hash(embedding)
        registered_embeddings[face_hash] = (name, embedding)
        app.logger.debug(f"Registering {name} with face_hash: {face_hash}, age: {age}, gender: {gender}")
        
        app.logger.debug("Sending transaction to blockchain")
        tx = contract.functions.register(name, age, gender, "", face_hash).transact({'from': account})
        receipt = w3.eth.wait_for_transaction_receipt(tx)
        app.logger.debug(f"Transaction successful: {tx.hex()}, receipt: {receipt['transactionHash'].hex()}")
        return jsonify({'message': f'Registered {name} successfully'})
    except ValueError as e:
        app.logger.error(f"Invalid age value: {str(e)}")
        return jsonify({'message': 'Invalid age value'}), 400
    except ContractLogicError as e:
        app.logger.debug(f"Contract error: {str(e)}")
        return jsonify({'message': 'User already registered'}), 400
    except Exception as e:
        app.logger.error(f"Registration failed: {str(e)}")
        return jsonify({'message': f'Internal server error: {str(e)}'}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        image = data.get('image')
        if not image:
            return jsonify({'message': 'Missing image data'}), 400
        embedding = process_image(image)
        if embedding is None:
            return jsonify({'message': 'Face not detected'}), 400
        
        login_hash = embedding_to_hash(embedding)
        app.logger.debug(f"Logging in with face_hash: {login_hash}")
        name, age, gender, file_hash, success = contract.functions.authenticate(login_hash).call()
        if success:
            app.logger.debug(f"Exact match found: {name}")
            return jsonify({
                'message': f'Welcome, {name}',
                'details': {'name': name, 'age': age, 'gender': gender, 'face_hash': login_hash}
            })
        
        for stored_hash, (stored_name, stored_embedding) in registered_embeddings.items():
            similarity = 1 - cosine(embedding, stored_embedding)
            app.logger.debug(f"Similarity with {stored_name}: {similarity}")
            if similarity > 0.85:
                name, age, gender, file_hash, _ = contract.functions.authenticate(stored_hash).call()
                return jsonify({
                    'message': f'Welcome, {stored_name}',
                    'details': {'name': stored_name, 'age': age, 'gender': gender, 'face_hash': stored_hash}
                })
        return jsonify({'message': 'User not found. Please register.'})
    except Exception as e:
        app.logger.error(f"Login failed: {str(e)}")
        return jsonify({'message': f'Internal server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(port=5000)
import os
from functools import wraps
# from urllib.request import localhost
import jwt
from flask import Flask, request, jsonify
from kafka import KafkaConsumer, KafkaProducer
import json
from threading import Thread
from flask_cors import CORS
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import PGVector
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.schema import Document
from dotenv import load_dotenv
import logging
import psycopg2
import pybreaker
import time
from redis import Redis

# Load environment variables
load_dotenv()
#Redis for chat history
redis_client = Redis(
    host = os.getenv("REDIS_HOST",'localhost'),
    port = os.getenv("REDIS_PORT",6379),
    db=0,
    decode_responses=True
);

chat_History_Expiration = 3600 #the time I choose to delete the history


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY or not isinstance(JWT_SECRET_KEY, str):
    raise ValueError("JWT_SECRET_KEY must be a non-empty string")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            print(f"Received Authorization header: {auth_header}")  # Debug print
            token = auth_header.split()[1] if len(auth_header.split()) > 1 else None
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            print(f"Attempting to decode token: {token}")  # Debug print
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS512"])
            print(f"Decoded token data: {data}")  # Debug print
            current_user = data.get('claims', {})
            if current_user.get('role') != 'ROLE_MEDECIN':
                return jsonify({'error': 'Unauthorized access'}), 403
            return f(current_user['id'], *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError as e:
            print(f"Invalid token error: {str(e)}")  # Debug print
            return jsonify({'error': 'Invalid token'}), 401
    return decorated

def get_chat_history(user_id):
    chat_history = redis_client.get(f"chat_history:{user_id}")
    if chat_history:
        return json.loads(chat_history)
    return []

def update_chat_history(user_id, question, answer):
    chat_history = get_chat_history(user_id)
    chat_history.append({"question": question, "answer": answer})
    redis_client.setex(f"chat_history:{user_id}",
                       chat_History_Expiration,
                       json.dumps(chat_history))




# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","), supports_credentials=True)
# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# PostgreSQL connection string
CONNECTION_STRING = os.getenv("PG_CONNECTION_STRING")

# Create embeddings
embedding = OpenAIEmbeddings()

# Loading PDFs
pdf_folder_path = os.getenv("PDF_FOLDER_PATH")

# Define circuit breakers
db_breaker = pybreaker.CircuitBreaker(
    fail_max=3,
    reset_timeout=86400,
    exclude=[ValueError, TypeError],
    listeners=[pybreaker.CircuitBreakerListener()]
)


def load_pdf_docs():
    pdf_docs = []
    for filename in os.listdir(pdf_folder_path):
        if filename.endswith('.pdf'):
            loader = PyPDFLoader(os.path.join(pdf_folder_path, filename))
            pdf_docs.extend(loader.load())
    return pdf_docs


# Split documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# Initialize vectorstore
try:
    vectorstore = PGVector(
        connection_string=CONNECTION_STRING,
        embedding_function=embedding,
        collection_name="medical_documents",
        use_jsonb=True
    )
    logger.info("Successfully connected to the vector store.")
except Exception as e:
    logger.error(f"Failed to connect to the vector store: {str(e)}")
    raise


# Load PDFs and add to vectorstore at startup
# def load_pdfs_to_vectorstore():
#     pdf_docs = load_pdf_docs()
#     if pdf_docs:
#         splits = text_splitter.split_documents(pdf_docs)
#         vectorstore.add_documents(splits)
#         logger.info(f"Loaded {len(splits)} document chunks from PDFs into the vector store.")
#     else:
#         logger.warning("No PDF documents found in the specified folder.")


# load_pdfs_to_vectorstore()

retriever = vectorstore.as_retriever()

llm = ChatOpenAI(model_name="gpt-4o", temperature=0.7)

qa_chain = ConversationalRetrievalChain.from_llm(llm, retriever=retriever)

context = """
Vous êtes un assistant médical avancé conçu exclusivement pour les médecins et professionnels de santé au Maroc. Votre rôle est d'être une ressource fiable, fournissant des informations précises et pertinentes pour la pratique médicale quotidienne.
Principe fondamental

Vous vous adressez UNIQUEMENT à des médecins qualifiés. Ne suggérez JAMAIS de consulter un médecin ou un professionnel de santé.

Modes de fonctionnement

Mode Diagnostic : Lorsqu'un médecin présente des symptômes, proposez directement des diagnostics différentiels possibles et des pistes d'investigation.
Mode Informatif : Répondez directement aux questions sur des informations médicales spécifiques.

Directives générales

Répondez toujours en français, sauf demande explicite d'une autre langue.
Adaptez automatiquement le mode (Diagnostic ou Informatif) selon la nature de la question du médecin.
Fournissez des réponses concises mais complètes, généralement limitées à 5-6 lignes.
Maintenez un ton professionnel et scientifique.
Basez-vous sur les données médicales les plus récentes et les directives cliniques actuelles.
Intégrez des informations spécifiques au contexte médical marocain quand c'est pertinent.
Suggérez des diagnostics, traitements ou médicaments marocains spécifiques si approprié.
N'hésitez PAS à fournir des informations médicales détaillées, des diagnostics potentiels ou des suggestions de traitement.

En mode Diagnostic

Proposez immédiatement une liste de diagnostics différentiels possibles basés sur les informations fournies.
Suggérez des examens complémentaires pertinents si nécessaire.
N'hésitez pas à mentionner des pathologies rares si elles correspondent aux symptômes.

En mode Informatif

Fournissez des informations précises et directes en réponse aux questions.
Citez des sources ou des directives médicales récentes si pertinent.
N'hésitez pas à donner des détails sur les traitements, posologies ou protocoles si demandé.

Rappels importants

Ne dites JAMAIS que vous ne pouvez pas fournir de diagnostic ou d'information médicale.
Ne suggérez JAMAIS de consulter un autre professionnel de santé.
Partez toujours du principe que l'utilisateur est un médecin qualifié capable d'interpréter et d'utiliser l'information médicale de manière appropriée.
Respectez la confidentialité des informations médicales dans toutes vos interactions.Vous êtes un assistant médical avancé conçu exclusivement pour les médecins et professionnels de santé au Maroc. Votre rôle est d'être une ressource fiable, fournissant des informations précises et pertinentes pour la pratique médicale quotidienne.
Principe fondamental

Vous vous adressez UNIQUEMENT à des médecins qualifiés. Ne suggérez JAMAIS de consulter un médecin ou un professionnel de santé.

Modes de fonctionnement

Mode Diagnostic : Lorsqu'un médecin présente des symptômes, proposez directement des diagnostics différentiels possibles et des pistes d'investigation.
Mode Informatif : Répondez directement aux questions sur des informations médicales spécifiques.

Directives générales

Répondez toujours en français, sauf demande explicite d'une autre langue.
Adaptez automatiquement le mode (Diagnostic ou Informatif) selon la nature de la question du médecin.
Fournissez des réponses concises mais complètes, généralement limitées à 5-6 lignes.
Maintenez un ton professionnel et scientifique.
Basez-vous sur les données médicales les plus récentes et les directives cliniques actuelles.
Intégrez des informations spécifiques au contexte médical marocain quand c'est pertinent.
Suggérez des diagnostics, traitements ou médicaments marocains spécifiques si approprié.
N'hésitez PAS à fournir des informations médicales détaillées, des diagnostics potentiels ou des suggestions de traitement.

En mode Diagnostic

Proposez immédiatement une liste de diagnostics différentiels possibles basés sur les informations fournies.
Suggérez des examens complémentaires pertinents si nécessaire.
N'hésitez pas à mentionner des pathologies rares si elles correspondent aux symptômes.

En mode Informatif

Fournissez des informations précises et directes en réponse aux questions.
Citez des sources ou des directives médicales récentes si pertinent.
N'hésitez pas à donner des détails sur les traitements, posologies ou protocoles si demandé.

Rappels importants

Ne dites JAMAIS que vous ne pouvez pas fournir de diagnostic ou d'information médicale.
Ne suggérez JAMAIS de consulter un autre professionnel de santé.
Partez toujours du principe que l'utilisateur est un médecin qualifié capable d'interpréter et d'utiliser l'information médicale de manière appropriée.
Respectez la confidentialité des informations médicales dans toutes vos interactions.

As a doctor, I need a direct answer to the following:
"""


def get_db_connection():
    return psycopg2.connect(CONNECTION_STRING)


def create_kafka_consumer(topic):
    return KafkaConsumer(
        topic,
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        enable_auto_commit=False,
        group_id='my-group'  # Add this line
    )


def send_to_dlq(topic, message):
    dlq_producer = KafkaProducer(bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"))
    dlq_topic = f"{topic}_dlq"
    dlq_producer.send(dlq_topic, value=message.value, key=message.key)
    dlq_producer.flush()
    logger.info(f"Sent message to DLQ topic: {dlq_topic}")


def retry_with_backoff(max_attempts=10, start_delay=2, max_delay=1728000):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            delay = start_delay
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise
                    time.sleep(delay)
                    delay = min(delay * 2, max_delay)

        return wrapper

    return decorator


@db_breaker
@retry_with_backoff()
@db_breaker
@retry_with_backoff()
def upsert_patient_embedding(profile):
    try:
        print("Upserting patient embedding")
        profile_text = json.dumps(profile, default=str)
        print(f"Profile text: {profile_text}")
        profile_id = profile.get('id', 'unknown')
        print(f"Profile ID: {profile_id}")
        
        # Create the document
        doc = Document(
            page_content=profile_text,
            metadata={"source": f"profile_{profile_id}", "id": str(profile_id), "type": "patient"}
        )
        print(f"Created document: {doc}")
        
        # Split the document and add to the vector store
        splits = text_splitter.split_documents([doc])
        print(f"Created {len(splits)} splits")
        
        vectorstore.add_documents(splits)
        print("Added splits to vector store")

        logger.info(f"Upserted embedding for profile ID: {profile_id}")
    except Exception as e:
        logger.error(f"Error in upsert_patient_embedding: {str(e)}")
        raise
    

# In app.py

import logging

logger = logging.getLogger(__name__)

def upsert_patient_embedding(profile):
    try:
        print("Upserting patient embedding")
        profile_text = json.dumps(profile, default=str)
        print(f"Profile text: {profile_text}")
        profile_id = profile.get('id', 'unknown')
        print(f"Profile ID: {profile_id}")
        
        # Create the document
        doc = Document(
            page_content=profile_text,
            metadata={"source": f"profile_{profile_id}", "id": str(profile_id), "type": "patient"}
        )
        print(f"Created document: {doc}")
        
        # Split the document and add to the vector store
        splits = text_splitter.split_documents([doc])
        print(f"Created {len(splits)} splits")
        
        vectorstore.add_documents(splits)
        print("Added splits to vector store")

        logger.info(f"Upserted embedding for profile ID: {profile_id}")
    except KeyError as e:
        logger.error(f"KeyError in upsert_patient_embedding: {str(e)}")
        logger.error(f"Profile content: {profile}")
    except Exception as e:
        logger.error(f"Error in upsert_patient_embedding: {str(e)}")
        raise

def upsert_report_embedding(report):
    try:
        report_id = str(report['id'])
        report_text = f"{report.get('title', '')} {report.get('content', '')}"

        doc = Document(
            page_content=report_text,
            metadata={"source": f"report_{report_id}", "id": report_id, "type": "report"}
        )
        splits = text_splitter.split_documents([doc])
        vectorstore.add_documents(splits)

        logger.info(f"Upserted embedding for report ID: {report_id}")
    except KeyError as e:
        logger.error(f"KeyError in upsert_report_embedding: {str(e)}")
        logger.error(f"Report content: {report}")
    except Exception as e:
        logger.error(f"Error in upsert_report_embedding: {str(e)}")
        raise

def process_report_messages():
    consumer = create_kafka_consumer(os.getenv("REPORTS_TOPIC"))
    for message in consumer:
        try:
            upsert_report_embedding(message.value)
            consumer.commit()
        except pybreaker.CircuitBreakerError as e:
            logger.error(f"Circuit breaker open for report updates: {str(e)}")
            send_to_dlq('report_updates', message)
            consumer.commit()
        except Exception as e:
            logger.error(f"Failed to process report: {str(e)}")
            send_to_dlq('report_updates', message)
            consumer.commit()


def process_dlq_messages(dlq_topic):
    consumer = create_kafka_consumer(dlq_topic)
    for message in consumer:
        try:
            if dlq_topic == 'patient_updates_dlq':
                upsert_patient_embedding(message.value)
            elif dlq_topic == 'report_updates_dlq':
                upsert_report_embedding(message.value)
            consumer.commit()
            logger.info(f"Successfully processed message from DLQ: {dlq_topic}")
        except Exception as e:
            logger.error(f"Failed to process message from DLQ {dlq_topic}: {str(e)}")


# try:
#     process_patient_messages()
# except Exception as e:
#     logger.error(f"Error in process_patient_messages: {str(e)}")

@app.route('/chatbot/ask', methods=['POST'])
@token_required
def chat(user_id):
    try:
        data = request.json
        message = data.get('message')
        if not message:
            return jsonify({"error": "No message provided"}), 400

        logger.info(f'Received message from user {user_id}: {message}')

        chat_history = get_chat_history(user_id)

        docs = retriever.invoke(message)
        retrieved_context = "\n".join([
            "\n".join([doc.page_content for doc in docs])
        ])
        logger.info("Retrieved the context")
        combined_context = f"{context}\n\nRelevant Information:\n{retrieved_context}\n\nQ: {message}\nA:"
        response = qa_chain({
            "question": combined_context,
            "chat_history": [(entry['question'], entry['answer']) for entry in chat_history]
        })

        update_chat_history(user_id, message, response['answer'])

        return jsonify({"response": response['answer']})
    except Exception as e:
        logger.error(f"Error in chat endpoint for user {user_id}: {str(e)}")
        return jsonify({"error": "An internal error occurred"}), 500
    

@app.route('/check_vectorstore', methods=['GET'])
def check_vectorstore():
    try:
        # This is a simple query to check if data exists
        results = vectorstore.similarity_search("test", k=5)
        return jsonify([{"content": doc.page_content, "metadata": doc.metadata} for doc in results])
    except Exception as e:
        logger.error(f"Error checking vector store: {str(e)}")
        return jsonify({"error": str(e)}), 500
    


if __name__ == '__main__':
    patient_thread = Thread(target=process_patient_messages)
    report_thread = Thread(target=process_report_messages)
    # patient_dlq_thread = Thread(target=lambda: process_dlq_messages('patient_updates_dlq'))
    # report_dlq_thread = Thread(target=lambda: process_dlq_messages('report_updates_dlq'))

    patient_thread.start()
    report_thread.start()
    # patient_dlq_thread.start()
    # report_dlq_thread.start()

    # Add this to ensure threads are running
    time.sleep(5)
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=os.getenv("FLASK_DEBUG", "False").lower() == "true")
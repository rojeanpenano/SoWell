import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import ast

# Initialize Firebase Admin SDK
cred = credentials.Certificate("sowell-key.json")
firebase_admin.initialize_app(cred)

# Load the CSV file with extracted keywords
faq_df = pd.read_csv("data/FAQs_with_keywords.csv")

# Safely parse keyword arrays
def parse_keywords(value):
    try:
        return ast.literal_eval(value)
    except:
        return []

# Firestore reference
db = firestore.client()
collection_ref = db.collection("chatbot_faqs")

# Upload each FAQ to Firestore
uploaded_count = 0
for _, row in faq_df.iterrows():
    question = row['Questions']
    answer = row['Answers']
    keywords = parse_keywords(row['keywords'])

    doc_data = {
        "question": question.strip(),
        "answer": answer.strip(),
        "keywords": keywords
    }

    collection_ref.add(doc_data)
    uploaded_count += 1

print(f"Uploaded {uploaded_count} chatbot FAQs to Firestore.")
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import FieldFilter
from typing import List, Dict, Optional, Any
import json
import os

from app.core.config import settings

class FirebaseService:
    def __init__(self):
        self.db = None
        self.app = None

    def initialize(self):
        """Initialize Firebase Admin SDK"""
        try:
            if not firebase_admin._apps:
                # Check if running on Google Cloud (will use default credentials)
                if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                    cred = credentials.ApplicationDefault()
                else:
                    # Use service account key file
                    if os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
                        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                    else:
                        print(f"Firebase credentials file not found at {settings.FIREBASE_CREDENTIALS_PATH}")
                        print("Please add your Firebase service account key to config/firebase-credentials.json")
                        return
                
                self.app = firebase_admin.initialize_app(cred)
            else:
                self.app = firebase_admin.get_app()
            
            self.db = firestore.client()
            print("✅ Firebase initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing Firebase: {e}")
            print("Make sure to:")
            print("1. Add your Firebase service account key to config/firebase-credentials.json")
            print("2. Set FIREBASE_PROJECT_ID in .env file")
            raise

    async def get_collection(self, collection_name: str) -> List[Dict]:
        """Get all documents from a collection"""
        try:
            docs = self.db.collection(collection_name).stream()
            result = []
            for doc in docs:
                doc_data = doc.to_dict()
                doc_data['id'] = doc.id
                result.append(doc_data)
            return result
        except Exception as e:
            print(f"Error getting collection {collection_name}: {e}")
            return []

    async def get_document(self, collection_name: str, doc_id: str) -> Optional[Dict]:
        """Get a specific document"""
        try:
            doc = self.db.collection(collection_name).document(doc_id).get()
            if doc.exists:
                doc_data = doc.to_dict()
                doc_data['id'] = doc.id
                return doc_data
            return None
        except Exception as e:
            print(f"Error getting document {doc_id}: {e}")
            return None

    async def add_document(self, collection_name: str, data: Dict) -> str:
        """Add a new document"""
        try:
            doc_ref = self.db.collection(collection_name).add(data)
            return doc_ref[1].id
        except Exception as e:
            print(f"Error adding document: {e}")
            raise

    async def update_document(self, collection_name: str, doc_id: str, data: Dict) -> bool:
        """Update a document"""
        try:
            self.db.collection(collection_name).document(doc_id).update(data)
            return True
        except Exception as e:
            print(f"Error updating document {doc_id}: {e}")
            return False

    async def delete_document(self, collection_name: str, doc_id: str) -> bool:
        """Delete a document"""
        try:
            self.db.collection(collection_name).document(doc_id).delete()
            return True
        except Exception as e:
            print(f"Error deleting document {doc_id}: {e}")
            return False

    async def query_collection(
        self, 
        collection_name: str, 
        filters: List[tuple] = None,
        order_by: str = None,
        limit: int = None
    ) -> List[Dict]:
        """Query collection with filters"""
        try:
            query = self.db.collection(collection_name)
            
            if filters:
                for field, operator, value in filters:
                    query = query.where(filter=FieldFilter(field, operator, value))
            
            if order_by:
                query = query.order_by(order_by)
            
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            result = []
            for doc in docs:
                doc_data = doc.to_dict()
                doc_data['id'] = doc.id
                result.append(doc_data)
            
            return result
        except Exception as e:
            print(f"Error querying collection {collection_name}: {e}")
            return []

    async def get_attendance_by_user(self, user_id: str, date_from: str = None, date_to: str = None) -> List[Dict]:
        """Get attendance records for a specific user"""
        filters = [("userId", "==", user_id)]
        
        if date_from:
            filters.append(("date", ">=", date_from))
        if date_to:
            filters.append(("date", "<=", date_to))
        
        return await self.query_collection("attendance", filters=filters, order_by="date")

    async def get_users_by_role(self, role: str = "worker") -> List[Dict]:
        """Get users by role"""
        filters = [("role", "==", role)]
        return await self.query_collection("users", filters=filters)

# Global instance
firebase_service = FirebaseService()
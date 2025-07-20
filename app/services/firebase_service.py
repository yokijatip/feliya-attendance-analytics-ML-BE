import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import FieldFilter
from typing import List, Dict, Optional, Any
import json
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.core.config import settings

class FirebaseService:
    def __init__(self):
        self.db = None
        self.app = None
        self.executor = ThreadPoolExecutor(max_workers=4)

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

    def _convert_firebase_data(self, doc_data: Dict) -> Dict:
        """Convert Firebase datetime objects to strings"""
        for key, value in doc_data.items():
            if hasattr(value, 'isoformat'):
                doc_data[key] = value.isoformat()
            elif hasattr(value, 'strftime'):
                doc_data[key] = value.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            elif value is None:
                doc_data[key] = None
        return doc_data

    async def get_collection(self, collection_name: str) -> List[Dict]:
        """Get all documents from a collection"""
        def _get_collection_sync():
            try:
                docs = self.db.collection(collection_name).stream()
                result = []
                for doc in docs:
                    doc_data = doc.to_dict()
                    doc_data['id'] = doc.id
                    doc_data = self._convert_firebase_data(doc_data)
                    result.append(doc_data)
                return result
            except Exception as e:
                print(f"Error getting collection {collection_name}: {e}")
                return []

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _get_collection_sync)

    async def get_document(self, collection_name: str, doc_id: str) -> Optional[Dict]:
        """Get a specific document"""
        def _get_document_sync():
            try:
                doc = self.db.collection(collection_name).document(doc_id).get()
                if doc.exists:
                    doc_data = doc.to_dict()
                    doc_data['id'] = doc.id
                    doc_data = self._convert_firebase_data(doc_data)
                    return doc_data
                return None
            except Exception as e:
                print(f"Error getting document {doc_id}: {e}")
                return None

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _get_document_sync)

    async def query_collection(
        self, 
        collection_name: str, 
        filters: List[tuple] = None,
        order_by: str = None,
        limit: int = None
    ) -> List[Dict]:
        """Query collection with filters"""
        def _query_collection_sync():
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
                    doc_data = self._convert_firebase_data(doc_data)
                    result.append(doc_data)
                
                return result
            except Exception as e:
                print(f"Error querying collection {collection_name}: {e}")
                return []

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _query_collection_sync)

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

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from datetime import datetime, timedelta
import joblib
import os
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple, Optional
import asyncio
import logging

from app.services.firebase_service import firebase_service
from app.models.ml_models import PerformanceMetrics, ClusteringResult, ClusteringResponse, PerformanceInsights
from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLService:
    def __init__(self):
        self.scaler = StandardScaler()
        self.kmeans_model = None
        self.feature_names = [
            'total_work_hours',
            'average_daily_hours', 
            'attendance_rate',
            'overtime_ratio',
            'punctuality_score',
            'consistency_score',
            'productivity_score'
        ]
        self.cluster_labels = {
            0: "Needs Improvement",
            1: "Average Performer", 
            2: "High Performer"
        }
        self.model_metadata = {
            'last_trained': None,
            'training_data_size': 0,
            'feature_importance': {}
        }

    async def initialize(self):
        """Initialize ML service and load saved models if available"""
        try:
            # Create models directory if it doesn't exist
            os.makedirs(settings.ML_MODEL_PATH, exist_ok=True)
            
            # Try to load existing models
            scaler_path = os.path.join(settings.ML_MODEL_PATH, "scaler.joblib")
            kmeans_path = os.path.join(settings.ML_MODEL_PATH, "kmeans_model.joblib")
            metadata_path = os.path.join(settings.ML_MODEL_PATH, "model_metadata.json")
            
            if os.path.exists(scaler_path) and os.path.exists(kmeans_path):
                self.scaler = joblib.load(scaler_path)
                self.kmeans_model = joblib.load(kmeans_path)
                
                # Load metadata if exists
                if os.path.exists(metadata_path):
                    import json
                    with open(metadata_path, 'r') as f:
                        self.model_metadata = json.load(f)
                
                logger.info("✅ ML models loaded successfully")
                logger.info(f"📊 Model trained on {self.model_metadata.get('training_data_size', 'unknown')} samples")
            else:
                logger.info("ℹ️ No existing models found. Will train new models when needed.")
            
            # Run automatic clustering analysis on startup with error handling
            await self.run_startup_analysis()
                
        except Exception as e:
            logger.error(f"❌ Error initializing ML service: {e}")

    async def run_startup_analysis(self):
        """Run clustering analysis on startup with improved error handling"""
        try:
            logger.info("\n🤖 Running automatic clustering analysis (All Time Data)...")
            
            # Check if we have users and attendance data
            users = await firebase_service.get_users_by_role("worker")
            if not users:
                logger.warning("⚠️ No worker users found. Skipping clustering analysis.")
                return
            
            # Check if users have attendance data
            sample_user = users[0]
            attendance_sample = await firebase_service.get_attendance_by_user(sample_user['id'])
            if not attendance_sample:
                logger.warning("⚠️ No attendance data found. Skipping clustering analysis.")
                return
            
            # Perform clustering analysis
            result = await self.perform_clustering(
                date_from=None,  # All time data
                date_to=None
            )
            
            # Display results
            self.display_clustering_results(result)
            
            # Create visualizations
            await self.create_visualizations_async(result)
            
        except Exception as e:
            logger.error(f"⚠️ Could not run startup analysis: {e}")
    
    async def create_visualizations_async(self, result: ClusteringResponse):
        """Create visualizations asynchronously to avoid blocking"""
        try:
            # Run visualization creation in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.create_visualizations, result)
        except Exception as e:
            logger.error(f"⚠️ Could not create visualizations: {e}")

    def create_visualizations(self, result: ClusteringResponse):
        """Create and save visualizations with improved error handling"""
        try:
            # Set style with fallback
            try:
                plt.style.use('seaborn-v0_8')
            except:
                plt.style.use('default')
            
            # Create figure with subplots
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Employee Performance Clustering Analysis', fontsize=16, fontweight='bold')
            
            # Prepare data
            df_results = pd.DataFrame([
                {
                    'name': r.name,
                    'cluster': r.cluster_label,
                    'performance_score': r.performance_score,
                    **r.features
                }
                for r in result.results
            ])
            
            # 1. Cluster Distribution (Pie Chart)
            cluster_counts = df_results['cluster'].value_counts()
            colors = ['#ff9999', '#66b3ff', '#99ff99']
            axes[0, 0].pie(cluster_counts.values, labels=cluster_counts.index, 
                          autopct='%1.1f%%', colors=colors[:len(cluster_counts)])
            axes[0, 0].set_title('Cluster Distribution')
            
            # 2. Performance Score by Cluster (Box Plot)
            try:
                import seaborn as sns
                sns.boxplot(data=df_results, x='cluster', y='performance_score', ax=axes[0, 1])
            except:
                # Fallback to matplotlib boxplot
                cluster_data = [df_results[df_results['cluster'] == cluster]['performance_score'].values 
                              for cluster in df_results['cluster'].unique()]
                axes[0, 1].boxplot(cluster_data, labels=df_results['cluster'].unique())
            
            axes[0, 1].set_title('Performance Score by Cluster')
            axes[0, 1].tick_params(axis='x', rotation=45)
            
            # 3. Attendance vs Productivity Scatter
            scatter = axes[1, 0].scatter(
                df_results['attendance_rate'], 
                df_results['productivity_score'],
                c=df_results['cluster'].astype('category').cat.codes,
                alpha=0.7,
                s=100,
                cmap='viridis'
            )
            axes[1, 0].set_xlabel('Attendance Rate (%)')
            axes[1, 0].set_ylabel('Productivity Score')
            axes[1, 0].set_title('Attendance vs Productivity')
            
            # 4. Feature Comparison Heatmap
            feature_cols = ['attendance_rate', 'punctuality_score', 'productivity_score', 'consistency_score']
            available_features = [col for col in feature_cols if col in df_results.columns]
            
            if available_features:
                cluster_means = df_results.groupby('cluster')[available_features].mean()
                
                try:
                    sns.heatmap(cluster_means.T, annot=True, fmt='.1f', cmap='RdYlGn', ax=axes[1, 1])
                except:
                    # Fallback to matplotlib imshow
                    im = axes[1, 1].imshow(cluster_means.T.values, cmap='RdYlGn', aspect='auto')
                    axes[1, 1].set_xticks(range(len(cluster_means.index)))
                    axes[1, 1].set_xticklabels(cluster_means.index)
                    axes[1, 1].set_yticks(range(len(available_features)))
                    axes[1, 1].set_yticklabels(available_features)
                    plt.colorbar(im, ax=axes[1, 1])
                
                axes[1, 1].set_title('Average Features by Cluster')
                axes[1, 1].set_xlabel('Cluster')
                axes[1, 1].set_ylabel('Features')
            
            plt.tight_layout()
            
            # Save visualization
            viz_path = os.path.join(settings.ML_MODEL_PATH, "clustering_analysis.png")
            plt.savefig(viz_path, dpi=300, bbox_inches='tight')
            logger.info(f"📊 Visualization saved to: {viz_path}")
            
            plt.close()
            
        except Exception as e:
            logger.error(f"⚠️ Could not create visualizations: {e}")

    def save_models(self):
        """Save trained models to disk with metadata"""
        try:
            scaler_path = os.path.join(settings.ML_MODEL_PATH, "scaler.joblib")
            kmeans_path = os.path.join(settings.ML_MODEL_PATH, "kmeans_model.joblib")
            metadata_path = os.path.join(settings.ML_MODEL_PATH, "model_metadata.json")
            
            joblib.dump(self.scaler, scaler_path)
            joblib.dump(self.kmeans_model, kmeans_path)
            
            # Save metadata
            import json
            self.model_metadata['last_trained'] = datetime.now().isoformat()
            with open(metadata_path, 'w') as f:
                json.dump(self.model_metadata, f, indent=2)
            
            logger.info("✅ Models and metadata saved successfully")
        except Exception as e:
            logger.error(f"❌ Error saving models: {e}")

    async def perform_clustering_with_validation(
        self, 
        user_ids: List[str] = None,
        date_from: str = None,
        date_to: str = None,
        n_clusters: int = None
    ) -> ClusteringResponse:
        """Enhanced clustering with data validation"""
        
        if n_clusters is None:
            n_clusters = settings.CLUSTERING_N_CLUSTERS

        # Get users to analyze
        if user_ids:
            users = []
            for user_id in user_ids:
                user = await firebase_service.get_document("users", user_id)
                if user:
                    users.append(user)
        else:
            users = await firebase_service.get_users_by_role("worker")

        if not users:
            raise ValueError("No users found for clustering analysis")

        if len(users) < n_clusters:
            logger.warning(f"⚠️ Only {len(users)} users found, reducing clusters to {len(users)}")
            n_clusters = len(users)

        # Calculate performance metrics for all users
        performance_data = []
        valid_users = 0
        
        for user in users:
            try:
                metrics = await self.calculate_performance_metrics(
                    user['id'], date_from, date_to
                )
                
                # Validate metrics - skip users with no data
                if metrics.total_work_hours > 0:
                    performance_data.append({
                        'user_id': user['id'],
                        'worker_id': user.get('workerId', ''),
                        'name': user.get('name', ''),
                        'email': user.get('email', ''),
                        **metrics.dict()
                    })
                    valid_users += 1
                else:
                    logger.warning(f"⚠️ Skipping user {user.get('name', user['id'])} - no work data")
                    
            except Exception as e:
                logger.error(f"❌ Error calculating metrics for user {user['id']}: {e}")
                continue

        if valid_users < 2:
            raise ValueError(f"Insufficient valid data. Only {valid_users} users have attendance records.")

        if valid_users < n_clusters:
            n_clusters = valid_users
            logger.info(f"📊 Adjusted clusters to {n_clusters} based on available data")

        # Continue with existing clustering logic...
        return await self.perform_clustering(user_ids, date_from, date_to, n_clusters)

# Global instance
ml_service = MLService()

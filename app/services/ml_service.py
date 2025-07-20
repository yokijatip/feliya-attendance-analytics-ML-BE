import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from datetime import datetime, timedelta
import joblib
import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple, Optional
import logging
import asyncio

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
        self.model_metadata = {}

    async def initialize(self):
        """Initialize ML service and load saved models if available"""
        try:
            # Create models directory if it doesn't exist
            os.makedirs(settings.ML_MODEL_PATH, exist_ok=True)
            
            # Try to load existing models
            scaler_path = os.path.join(settings.ML_MODEL_PATH, "scaler.joblib")
            kmeans_path = os.path.join(settings.ML_MODEL_PATH, "kmeans_model.joblib")
            
            if os.path.exists(scaler_path) and os.path.exists(kmeans_path):
                self.scaler = joblib.load(scaler_path)
                self.kmeans_model = joblib.load(kmeans_path)
                print("✅ ML models loaded successfully")
            else:
                print("ℹ️ No existing models found. Will train new models when needed.")
            
            # Run automatic clustering analysis on startup
            await self.run_startup_analysis()
                
        except Exception as e:
            print(f"❌ Error initializing ML service: {e}")

    async def run_startup_analysis(self):
        """Run clustering analysis on startup and display results"""
        try:
            print("\n🤖 Running automatic clustering analysis (All Time Data)...")
            
            # Check if we have users and attendance data
            users = await firebase_service.get_users_by_role("worker")
            if not users:
                print("⚠️ No worker users found. Skipping clustering analysis.")
                return
            
            # Check if users have attendance data
            sample_user = users[0]
            attendance_sample = await firebase_service.get_attendance_by_user(sample_user['id'])
            if not attendance_sample:
                print("⚠️ No attendance data found. Skipping clustering analysis.")
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
            print(f"⚠️ Could not run startup analysis: {e}")
    
    async def run_monthly_analysis(self, year: int = None, month: int = None):
        """Run clustering analysis for specific month"""
        from datetime import datetime, timedelta
        import calendar
        
        if not year or not month:
            now = datetime.now()
            year = now.year
            month = now.month
        
        # Get first and last day of month
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, calendar.monthrange(year, month)[1])
        
        date_from = first_day.strftime('%Y-%m-%d')
        date_to = last_day.strftime('%Y-%m-%d')
        
        print(f"\n🗓️ Running monthly clustering analysis for {calendar.month_name[month]} {year}...")
        
        try:
            result = await self.perform_clustering(
                date_from=date_from,
                date_to=date_to
            )
            
            print(f"\n📅 MONTHLY ANALYSIS - {calendar.month_name[month]} {year}")
            print("="*60)
            self.display_clustering_results(result)
            
            return result
            
        except Exception as e:
            print(f"⚠️ Could not run monthly analysis: {e}")
            return None

    async def run_quarterly_analysis(self, year: int = None, quarter: int = None):
        """Run clustering analysis for specific quarter"""
        from datetime import datetime
        import calendar
        
        if not year or not quarter:
            now = datetime.now()
            year = now.year
            quarter = (now.month - 1) // 3 + 1
        
        # Define quarter months
        quarter_months = {
            1: (1, 3),   # Q1: Jan-Mar
            2: (4, 6),   # Q2: Apr-Jun
            3: (7, 9),   # Q3: Jul-Sep
            4: (10, 12)  # Q4: Oct-Dec
        }
        
        start_month, end_month = quarter_months[quarter]
        
        first_day = datetime(year, start_month, 1)
        last_day = datetime(year, end_month, calendar.monthrange(year, end_month)[1])
        
        date_from = first_day.strftime('%Y-%m-%d')
        date_to = last_day.strftime('%Y-%m-%d')
        
        print(f"\n📊 Running quarterly clustering analysis for Q{quarter} {year}...")
        
        try:
            result = await self.perform_clustering(
                date_from=date_from,
                date_to=date_to
            )
            
            print(f"\n📈 QUARTERLY ANALYSIS - Q{quarter} {year}")
            print("="*60)
            self.display_clustering_results(result)
            
            return result
            
        except Exception as e:
            print(f"⚠️ Could not run quarterly analysis: {e}")
            return None
    
    def display_clustering_results(self, result: ClusteringResponse):
        """Display clustering results in console"""
        print("\n" + "="*60)
        print("🎯 CLUSTERING ANALYSIS RESULTS")
        print("="*60)
        
        print(f"📊 Total Users Analyzed: {result.total_users}")
        print(f"🎯 Model Accuracy (Silhouette Score): {result.model_accuracy:.3f}")
        print(f"📅 Analysis Period: {result.analysis_period['date_from']} to {result.analysis_period['date_to']}")
        
        # Group results by cluster
        clusters = {}
        for user_result in result.results:
            cluster_label = user_result.cluster_label
            if cluster_label not in clusters:
                clusters[cluster_label] = []
            clusters[cluster_label].append(user_result)
        
        print(f"\n📈 CLUSTER DISTRIBUTION:")
        for cluster_label, users in clusters.items():
            print(f"  {cluster_label}: {len(users)} users ({len(users)/result.total_users*100:.1f}%)")
        
        print(f"\n👥 DETAILED RESULTS:")
        # Display in order: High Performer, Average Performer, Needs Improvement
        display_order = ["High Performer", "Average Performer", "Needs Improvement"]
        for cluster_label in display_order:
            if cluster_label not in clusters:
                continue
            users = clusters[cluster_label]
            print(f"\n🏷️ {cluster_label}:")
            for user in sorted(users, key=lambda x: x.performance_score, reverse=True):
                print(f"  • {user.name} ({user.worker_id}) - Score: {user.performance_score:.1f}")
                print(f"    Attendance: {user.features.get('attendance_rate', 0):.1f}% | "
                      f"Punctuality: {user.features.get('punctuality_score', 0):.1f}% | "
                      f"Productivity: {user.features.get('productivity_score', 0):.1f}%")
        
        print("\n" + "="*60)
    
    async def create_visualizations_async(self, result: ClusteringResponse):
        """Create visualizations asynchronously"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.create_visualizations, result)

    def create_visualizations(self, result: ClusteringResponse):
        """Create and save visualizations"""
        try:
            # Set style with fallback
            try:
                plt.style.use('seaborn-v0_8')
                sns.set_palette("husl")
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
            axes[0, 0].pie(cluster_counts.values, labels=cluster_counts.index, autopct='%1.1f%%')
            axes[0, 0].set_title('Cluster Distribution')
            
            # 2. Performance Score by Cluster (Box Plot)
            try:
                sns.boxplot(data=df_results, x='cluster', y='performance_score', ax=axes[0, 1])
            except:
                # Fallback to basic plot
                for i, cluster in enumerate(df_results['cluster'].unique()):
                    cluster_data = df_results[df_results['cluster'] == cluster]['performance_score']
                    axes[0, 1].scatter([i] * len(cluster_data), cluster_data, alpha=0.6)
                axes[0, 1].set_xticks(range(len(df_results['cluster'].unique())))
                axes[0, 1].set_xticklabels(df_results['cluster'].unique())
            
            axes[0, 1].set_title('Performance Score by Cluster')
            axes[0, 1].tick_params(axis='x', rotation=45)
            
            # 3. Attendance vs Productivity Scatter
            scatter = axes[1, 0].scatter(
                df_results['attendance_rate'], 
                df_results['productivity_score'],
                c=df_results['cluster'].astype('category').cat.codes,
                alpha=0.7,
                s=100
            )
            axes[1, 0].set_xlabel('Attendance Rate (%)')
            axes[1, 0].set_ylabel('Productivity Score')
            axes[1, 0].set_title('Attendance vs Productivity')
            
            # 4. Feature Comparison (Heatmap)
            feature_cols = ['attendance_rate', 'punctuality_score', 'productivity_score', 'consistency_score']
            available_features = [col for col in feature_cols if col in df_results.columns]
            
            if available_features:
                cluster_means = df_results.groupby('cluster')[available_features].mean()
                
                try:
                    sns.heatmap(cluster_means.T, annot=True, fmt='.1f', cmap='RdYlGn', ax=axes[1, 1])
                except:
                    # Fallback heatmap
                    im = axes[1, 1].imshow(cluster_means.T.values, cmap='RdYlGn', aspect='auto')
                    axes[1, 1].set_xticks(range(len(cluster_means.index)))
                    axes[1, 1].set_xticklabels(cluster_means.index, rotation=45)
                    axes[1, 1].set_yticks(range(len(available_features)))
                    axes[1, 1].set_yticklabels(available_features)
                
                axes[1, 1].set_title('Average Features by Cluster')
                axes[1, 1].set_xlabel('Cluster')
                axes[1, 1].set_ylabel('Features')
            
            plt.tight_layout()
            
            # Save visualization
            viz_path = os.path.join(settings.ML_MODEL_PATH, "clustering_analysis.png")
            plt.savefig(viz_path, dpi=300, bbox_inches='tight')
            print(f"📊 Visualization saved to: {viz_path}")
            
            plt.close()
            
        except Exception as e:
            print(f"⚠️ Could not create visualizations: {e}")

    def save_models(self):
        """Save trained models to disk"""
        try:
            scaler_path = os.path.join(settings.ML_MODEL_PATH, "scaler.joblib")
            kmeans_path = os.path.join(settings.ML_MODEL_PATH, "kmeans_model.joblib")
            
            joblib.dump(self.scaler, scaler_path)
            joblib.dump(self.kmeans_model, kmeans_path)
            
            # Update metadata
            self.model_metadata = {
                'last_trained': datetime.now().isoformat(),
                'training_data_size': len(self.feature_names),
                'n_clusters': len(self.cluster_labels)
            }
            
            print("✅ Models saved successfully")
        except Exception as e:
            print(f"❌ Error saving models: {e}")

    async def calculate_performance_metrics(
        self, 
        user_id: str, 
        date_from: str = None, 
        date_to: str = None
    ) -> PerformanceMetrics:
        """Calculate performance metrics for a user"""
        
        # Get attendance data
        attendance_records = await firebase_service.get_attendance_by_user(
            user_id, date_from, date_to
        )
        
        if not attendance_records:
            return PerformanceMetrics(
                user_id=user_id,
                total_work_hours=0.0,
                average_daily_hours=0.0,
                attendance_rate=0.0,
                overtime_ratio=0.0,
                punctuality_score=0.0,
                consistency_score=0.0,
                productivity_score=0.0
            )

        # Convert to DataFrame for easier processing
        df = pd.DataFrame(attendance_records)
        
        # Calculate metrics
        total_work_hours = df['workMinutes'].sum() / 60.0
        total_days = len(df)
        average_daily_hours = total_work_hours / total_days if total_days > 0 else 0
        
        # Attendance rate (based on working days in period)
        date_range_days = self._calculate_working_days(date_from, date_to)
        attendance_rate = (total_days / date_range_days) * 100 if date_range_days > 0 else 0
        
        # Overtime ratio
        total_overtime = df['overtimeMinutes'].sum() / 60.0
        overtime_ratio = (total_overtime / total_work_hours) * 100 if total_work_hours > 0 else 0
        
        # Punctuality score (based on clock-in times)
        punctuality_score = self._calculate_punctuality_score(df)
        
        # Consistency score (based on work hours variation)
        consistency_score = self._calculate_consistency_score(df)
        
        # Productivity score (based on work description and hours)
        productivity_score = self._calculate_productivity_score(df)
        
        return PerformanceMetrics(
            user_id=user_id,
            total_work_hours=total_work_hours,
            average_daily_hours=average_daily_hours,
            attendance_rate=min(attendance_rate, 100),  # Cap at 100%
            overtime_ratio=overtime_ratio,
            punctuality_score=punctuality_score,
            consistency_score=consistency_score,
            productivity_score=productivity_score
        )

    def _calculate_working_days(self, date_from: str, date_to: str) -> int:
        """Calculate number of working days in date range"""
        if not date_from or not date_to:
            return 22  # Default assumption for a month
        
        try:
            start = datetime.strptime(date_from, "%Y-%m-%d")
            end = datetime.strptime(date_to, "%Y-%m-%d")
            
            # Count weekdays only (Monday=0, Sunday=6)
            working_days = 0
            current = start
            while current <= end:
                if current.weekday() < 5:  # Monday=0, Friday=4
                    working_days += 1
                current += timedelta(days=1)
            
            return working_days
        except:
            return 22

    def _calculate_punctuality_score(self, df: pd.DataFrame) -> float:
        """Calculate punctuality score based on clock-in times"""
        try:
            # Convert target time to minutes for comparison
            target_hour, target_minute = map(int, settings.PUNCTUALITY_TIME_THRESHOLD.split(':'))
            target_minutes = target_hour * 60 + target_minute
            
            punctual_days = 0
            for _, row in df.iterrows():
                clock_in_str = str(row.get('clockInTime', ''))
                
                # Handle different time formats
                if clock_in_str and clock_in_str != 'nan':
                    try:
                        # Extract time from various formats
                        if 'T' in clock_in_str:  # ISO format
                            time_part = clock_in_str.split('T')[1].split('+')[0]
                            hour, minute = map(int, time_part.split(':')[:2])
                        elif ':' in clock_in_str:  # HH:MM format
                            hour, minute = map(int, clock_in_str.split(':')[:2])
                        else:
                            continue
                        
                        clock_in_minutes = hour * 60 + minute
                        
                        # Consider punctual if within 15 minutes of target
                        if clock_in_minutes <= target_minutes + 15:
                            punctual_days += 1
                            
                    except (ValueError, IndexError):
                        continue
            
            return (punctual_days / len(df)) * 100 if len(df) > 0 else 0
        except:
            return 50.0  # Default score

    def _calculate_consistency_score(self, df: pd.DataFrame) -> float:
        """Calculate consistency score based on work hours variation"""
        try:
            work_hours = df['workMinutes'] / 60.0
            std_dev = work_hours.std()
            mean_hours = work_hours.mean()
            
            # Lower variation = higher consistency
            if mean_hours > 0:
                coefficient_of_variation = std_dev / mean_hours
                consistency_score = max(0, 100 - (coefficient_of_variation * 100))
            else:
                consistency_score = 0
            
            return min(consistency_score, 100)
        except:
            return 50.0

    def _calculate_productivity_score(self, df: pd.DataFrame) -> float:
        """Calculate productivity score based on work description and hours"""
        try:
            total_score = 0
            for _, row in df.iterrows():
                work_desc = row.get('workDescription', '')
                work_hours = row.get('workMinutes', 0) / 60.0
                
                # Score based on description length and detail (max 40 points)
                desc_score = min(len(work_desc) / 100, 1) * 40
                
                # Score based on reasonable work hours (max 60 points)
                hours_score = min(work_hours / settings.WORKING_HOURS_TARGET, 1) * 60
                
                total_score += desc_score + hours_score
            
            return (total_score / len(df)) if len(df) > 0 else 0
        except:
            return 50.0

    async def perform_clustering(
        self, 
        user_ids: List[str] = None,
        date_from: str = None,
        date_to: str = None,
        n_clusters: int = None
    ) -> ClusteringResponse:
        """Perform K-Means clustering on user performance data"""
        
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

        # Calculate performance metrics for all users
        performance_data = []
        for user in users:
            try:
                metrics = await self.calculate_performance_metrics(
                    user['id'], date_from, date_to
                )
                
                performance_data.append({
                    'user_id': user['id'],
                    'worker_id': user.get('workerId', ''),
                    'name': user.get('name', ''),
                    'email': user.get('email', ''),
                    **metrics.dict()
                })
            except Exception as e:
                print(f"Error calculating metrics for user {user['id']}: {e}")
                continue

        if not performance_data:
            raise ValueError("No valid performance data found for clustering")

        # Convert to DataFrame
        df = pd.DataFrame(performance_data)
        
        # Prepare features for clustering
        feature_columns = [col for col in self.feature_names if col in df.columns]
        X = df[feature_columns].fillna(0)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Adjust n_clusters if we have fewer users
        if len(df) < n_clusters:
            n_clusters = len(df)
            print(f"⚠️ Adjusted clusters to {n_clusters} due to limited data")
        
        # Perform K-Means clustering
        self.kmeans_model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = self.kmeans_model.fit_predict(X_scaled)
        
        # Sort clusters by performance (assign labels based on cluster centers)
        cluster_performance = {}
        for i in range(n_clusters):
            cluster_mask = clusters == i
            if np.any(cluster_mask):
                cluster_users = df[cluster_mask]
                avg_performance = cluster_users[feature_columns].mean().mean()
                cluster_performance[i] = avg_performance
        
        # Sort clusters by performance and reassign labels
        sorted_clusters = sorted(cluster_performance.items(), key=lambda x: x[1])
        cluster_mapping = {}
        for new_label, (old_label, _) in enumerate(sorted_clusters):
            cluster_mapping[old_label] = new_label
        
        # Remap clusters
        clusters = np.array([cluster_mapping[c] for c in clusters])
        
        # Calculate silhouette score for model evaluation
        if len(set(clusters)) > 1:
            silhouette_avg = silhouette_score(X_scaled, clusters)
        else:
            silhouette_avg = 0.0

        # Save the trained models
        self.save_models()
        
        # Prepare results
        results = []
        for i, user_data in enumerate(performance_data):
            cluster = int(clusters[i])
            
            # Calculate overall performance score
            performance_score = self._calculate_overall_score(
                {col: user_data[col] for col in feature_columns}
            )
            
            result = ClusteringResult(
                user_id=user_data['user_id'],
                worker_id=user_data['worker_id'],
                name=user_data['name'],
                cluster=cluster,
                cluster_label=self.cluster_labels.get(cluster, f"Cluster {cluster}"),
                performance_score=performance_score,
                features={col: user_data[col] for col in feature_columns}
            )
            results.append(result)
        
        # Sort results by cluster and then by performance score
        results.sort(key=lambda x: (x.cluster, -x.performance_score))

        # Get cluster centers
        cluster_centers = {}
        for i, center in enumerate(self.kmeans_model.cluster_centers_):
            cluster_centers[f"cluster_{i}"] = center.tolist()

        return ClusteringResponse(
            results=results,
            cluster_centers=cluster_centers,
            feature_names=feature_columns,
            analysis_period={
                "date_from": date_from or "All Time",
                "date_to": date_to or "All Time"
            },
            total_users=len(users),
            model_accuracy=silhouette_avg
        )

    def _calculate_overall_score(self, features: Dict[str, float]) -> float:
        """Calculate overall performance score from features"""
        # Weighted average of different metrics
        weights = {
            'total_work_hours': 0.15,
            'attendance_rate': 0.25,
            'punctuality_score': 0.20,
            'consistency_score': 0.15,
            'productivity_score': 0.25
        }
        
        total_score = 0
        total_weight = 0
        
        for feature, value in features.items():
            if feature in weights:
                # Normalize values to 0-100 scale
                normalized_value = min(value, 100)
                total_score += normalized_value * weights[feature]
                total_weight += weights[feature]
        
        return total_score / total_weight if total_weight > 0 else 0

# Global instance
ml_service = MLService()

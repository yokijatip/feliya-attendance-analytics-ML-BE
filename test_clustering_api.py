"""
Script untuk testing clustering API endpoints
"""

import requests
import json
from datetime import datetime, timedelta

# Base URL API
BASE_URL = "http://localhost:8000"

def test_clustering_analyze():
    """Test clustering analyze endpoint"""
    print("🧪 Testing Clustering Analyze Endpoint")
    print("="*50)
    
    # Test 1: All workers, all time
    print("\n1️⃣ Testing: All workers, all time")
    url = f"{BASE_URL}/api/v1/ml/clustering/analyze"
    
    request_data = {
    #    "user_ids": "kIze9rZs4GbnL2rMjRegPoItUa73",
        "user_ids": None,  # Test with all users
        "date_from": None,
        "date_to": None,
        "n_clusters": 3
    }
    
    try:
        response = requests.post(url, json=request_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {data['total_users']} users")
            print(f"📊 Model Accuracy: {data['model_accuracy']:.3f}")
            print(f"📅 Analysis Period: {data['analysis_period']['date_from']} to {data['analysis_period']['date_to']}")
            
            # Show cluster distribution
            clusters = {}
            for result in data['results']:
                cluster_label = result['cluster_label']
                if cluster_label not in clusters:
                    clusters[cluster_label] = 0
                clusters[cluster_label] += 1
            
            print("\n📈 Cluster Distribution:")
            for cluster_label, count in clusters.items():
                print(f"  {cluster_label}: {count} users")
            
            # Show top performers
            print("\n🏆 Top 3 Performers:")
            sorted_results = sorted(data['results'], key=lambda x: x['performance_score'], reverse=True)
            for i, result in enumerate(sorted_results[:3]):
                print(f"  {i+1}. {result['name']} ({result['worker_id']}) - Score: {result['performance_score']:.1f}")
        else:
            print(f"❌ Error: {response.text}")
    
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 2: Specific date range
    print("\n2️⃣ Testing: Current month analysis")
    
    # Get current month dates
    now = datetime.now()
    first_day = now.replace(day=1)
    if now.month == 12:
        next_month = now.replace(year=now.year+1, month=1, day=1)
    else:
        next_month = now.replace(month=now.month+1, day=1)
    last_day = next_month - timedelta(days=1)
    
    request_data = {
        "user_ids": None,
        "date_from": first_day.strftime("%Y-%m-%d"),
        "date_to": last_day.strftime("%Y-%m-%d"),
        "n_clusters": 3
    }
    
    try:
        response = requests.post(url, json=request_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {data['total_users']} users for current month")
            print(f"📊 Model Accuracy: {data['model_accuracy']:.3f}")
        else:
            print(f"❌ Error: {response.text}")
    
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_quick_analysis():
    """Test quick analysis endpoint"""
    print("\n🚀 Testing Quick Analysis Endpoint")
    print("="*50)
    
    url = f"{BASE_URL}/api/v1/ml/clustering/quick-analysis"
    
    # Test with query parameters
    params = {
        "date_from": "2024-12-01",
        "date_to": "2024-12-31",
        "n_clusters": 3
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Quick Analysis Success!")
            print(f"📊 Total Users: {data['total_users']}")
            print(f"🎯 Model Accuracy: {data['model_accuracy']:.3f}")
            
            # Show sample results
            if data['results']:
                print(f"\n📋 Sample Results:")
                for result in data['results'][:3]:  # Show first 3
                    print(f"  • {result['name']}: {result['cluster_label']} (Score: {result['performance_score']:.1f})")
        else:
            print(f"❌ Error: {response.text}")
    
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_model_status():
    """Test model status endpoint"""
    print("\n📊 Testing Model Status Endpoint")
    print("="*50)
    
    url = f"{BASE_URL}/api/v1/ml/clustering/model-status"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Model Status Retrieved!")
            print(f"🤖 Model Trained: {data['model_trained']}")
            print(f"📊 Available Clusters: {data['available_clusters']}")
            print(f"🏷️ Cluster Labels: {data['cluster_labels']}")
            print(f"📈 Features: {data['feature_names']}")
            
            if 'model_info' in data:
                info = data['model_info']
                print(f"\n📋 Model Info:")
                print(f"  Algorithm: {info['algorithm']}")
                print(f"  Clusters: {info['n_clusters']}")
                print(f"  Features: {info['features_count']}")
                print(f"  Last Trained: {info.get('last_trained', 'N/A')}")
        else:
            print(f"❌ Error: {response.text}")
    
    except Exception as e:
        print(f"❌ Request failed: {e}")

def main():
    print("🧪 CLUSTERING API TESTING SUITE")
    print("="*60)
    
    # Test health check first
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ API Health: {health['status']}")
            print(f"🔥 Firebase Connected: {health['firebase_connected']}")
            print(f"🤖 ML Model Trained: {health['ml_model_trained']}")
        else:
            print("❌ API not healthy!")
            return
    except:
        print("❌ Cannot connect to API!")
        return
    
    # Run tests
    test_model_status()
    test_quick_analysis()
    test_clustering_analyze()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()

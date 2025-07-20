"""
Script untuk menganalisis kualitas data dan memberikan rekomendasi perbaikan
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def analyze_data_quality():
    """Analyze data quality and provide recommendations"""
    print("🔍 DATA QUALITY ANALYSIS")
    print("="*60)
    
    # Get all users
    try:
        response = requests.get(f"{BASE_URL}/api/v1/users?role=worker")
        if response.status_code == 200:
            users = response.json()
            print(f"📊 Total Workers: {len(users)}")
            
            # Analyze each user's attendance data
            users_with_data = 0
            users_without_data = 0
            total_attendance_records = 0
            
            for user in users[:5]:  # Check first 5 users
                user_id = user['id']
                name = user.get('name', 'Unknown')
                worker_id = user.get('workerId', 'Unknown')
                
                # Get attendance summary
                attendance_response = requests.get(
                    f"{BASE_URL}/api/v1/attendance/user/{user_id}/summary"
                )
                
                if attendance_response.status_code == 200:
                    summary = attendance_response.json()
                    records = summary['total_records']
                    work_hours = summary['total_work_hours']
                    
                    print(f"\n👤 {name} ({worker_id}):")
                    print(f"   📋 Records: {records}")
                    print(f"   ⏰ Total Hours: {work_hours:.1f}")
                    print(f"   📈 Avg Daily Hours: {summary['average_daily_hours']:.1f}")
                    
                    if records > 0:
                        users_with_data += 1
                        total_attendance_records += records
                    else:
                        users_without_data += 1
                        print(f"   ⚠️ No attendance data!")
                else:
                    print(f"   ❌ Error getting data for {name}")
            
            print(f"\n📊 DATA SUMMARY:")
            print(f"   ✅ Users with data: {users_with_data}")
            print(f"   ❌ Users without data: {users_without_data}")
            print(f"   📋 Total attendance records: {total_attendance_records}")
            print(f"   📈 Avg records per user: {total_attendance_records/max(users_with_data,1):.1f}")
            
        else:
            print(f"❌ Error getting users: {response.text}")
    
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

def test_improved_clustering():
    """Test clustering with improved parameters"""
    print("\n🚀 TESTING IMPROVED CLUSTERING")
    print("="*60)
    
    # Test with different cluster numbers
    for n_clusters in [2, 3, 4]:
        print(f"\n🧪 Testing with {n_clusters} clusters:")
        
        url = f"{BASE_URL}/api/v1/ml/clustering/quick-analysis"
        params = {"n_clusters": n_clusters}
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                accuracy = data['model_accuracy']
                total_users = data['total_users']
                
                print(f"   📊 Users: {total_users}")
                print(f"   🎯 Accuracy: {accuracy:.3f}")
                
                # Show cluster distribution
                clusters = {}
                for result in data['results']:
                    cluster_label = result['cluster_label']
                    clusters[cluster_label] = clusters.get(cluster_label, 0) + 1
                
                print(f"   📈 Distribution: {clusters}")
                
                # Find best accuracy
                if accuracy > 0.5:
                    print(f"   ✅ Good accuracy!")
                elif accuracy > 0.3:
                    print(f"   ⚠️ Moderate accuracy")
                else:
                    print(f"   ❌ Low accuracy - need more diverse data")
            else:
                print(f"   ❌ Error: {response.text}")
        
        except Exception as e:
            print(f"   ❌ Test failed: {e}")

def get_recommendations():
    """Provide recommendations for improvement"""
    print("\n💡 RECOMMENDATIONS FOR IMPROVEMENT")
    print("="*60)
    
    recommendations = [
        "1. 📊 Data Quality:",
        "   • Pastikan semua worker memiliki data attendance",
        "   • Minimal 10-15 records per user untuk clustering yang baik",
        "   • Periksa data yang missing atau null",
        "",
        "2. 🎯 Model Accuracy:",
        "   • Jika accuracy < 0.3, pertimbangkan mengurangi jumlah cluster",
        "   • Tambahkan lebih banyak features (misal: project completion rate)",
        "   • Normalisasi data yang lebih baik",
        "",
        "3. 🔧 Performance Score:",
        "   • Periksa perhitungan punctuality_score",
        "   • Validasi work_description tidak kosong",
        "   • Pastikan workMinutes > 0",
        "",
        "4. 📈 Next Steps:",
        "   • Implementasi frontend Vue.js untuk visualisasi",
        "   • Tambahkan real-time monitoring",
        "   • Export hasil ke CSV/Excel",
        "   • Notifikasi untuk performance rendah"
    ]
    
    for rec in recommendations:
        print(rec)

def main():
    print("🔍 COMPREHENSIVE DATA ANALYSIS")
    print("="*80)
    
    analyze_data_quality()
    test_improved_clustering()
    get_recommendations()
    
    print("\n✅ Analysis completed!")
    print("\n🚀 Your API is ready for frontend development!")
    print("📋 Consider implementing the recommendations above for better results.")

if __name__ == "__main__":
    main()

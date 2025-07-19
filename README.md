# Employee Performance Analytics API

Backend API untuk analisis performa karyawan menggunakan K-Means clustering dengan integrasi Firebase Firestore.

## 🚀 Fitur Utama

- **Machine Learning**: K-Means clustering untuk analisis performa karyawan
- **Firebase Integration**: Sinkronisasi real-time dengan Firestore
- **RESTful API**: API endpoints yang lengkap untuk manajemen data
- **Performance Analytics**: Analisis mendalam performa karyawan
- **AI-powered Insights**: Rekomendasi dan insight berbasis AI

## 📊 Machine Learning Features

### Performance Metrics

- **Total Work Hours**: Total jam kerja dalam periode tertentu
- **Attendance Rate**: Tingkat kehadiran karyawan
- **Punctuality Score**: Skor ketepatan waktu masuk kerja
- **Consistency Score**: Konsistensi jam kerja harian
- **Productivity Score**: Skor produktivitas berdasarkan deskripsi kerja
- **Overtime Ratio**: Rasio lembur terhadap jam kerja normal

### Clustering Analysis

- **Algorithm**: K-Means clustering dengan 3 cluster default
- **Clusters**: High Performer, Average Performer, Needs Improvement
- **Features**: 7 performance metrics
- **Model Persistence**: Model disimpan dalam format joblib
- **Accuracy**: Silhouette score untuk evaluasi model

## 🛠️ Setup dan Instalasi

### 1. Clone Repository

```bash
git clone <repository-url>
cd employee-performance-backend
```

### 2. Setup Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Firebase

1. Buat project di [Firebase Console](https://console.firebase.google.com/)
2. Enable Firestore Database
3. Generate service account key:
   - Go to Project Settings > Service Accounts
   - Generate new private key
   - Download JSON file
4. Place the JSON file di `config/firebase-credentials.json`
5. Run setup helper:

```bash
python setup_firebase.py
```

### 5. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` file dengan konfigurasi yang sesuai:

```env
FIREBASE_CREDENTIALS_PATH=config/firebase-credentials.json
FIREBASE_PROJECT_ID=your-project-id
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000
ML_MODEL_PATH=models
CLUSTERING_N_CLUSTERS=3
```

### 6. Run Application

```bash
python run_server.py
```

atau

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📚 API Documentation

Setelah menjalankan aplikasi, akses dokumentasi API di:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔗 API Endpoints

### Users Management

- `GET /api/v1/users/` - Get all users
- `GET /api/v1/users/{user_id}` - Get user by ID
- `GET /api/v1/users/workers/active` - Get active workers
- `GET /api/v1/users/worker/{worker_id}` - Get user by worker ID

### Attendance Management

- `GET /api/v1/attendance/` - Get attendance records
- `GET /api/v1/attendance/{attendance_id}` - Get specific attendance
- `GET /api/v1/attendance/user/{user_id}/summary` - Get user attendance summary

### Analytics

- `GET /api/v1/analytics/overview` - Get analytics overview
  - **Parameters**:
    - `date_from` (optional): Start date filter (format: YYYY-MM-DD)
    - `date_to` (optional): End date filter (format: YYYY-MM-DD)
- `GET /api/v1/analytics/team/performance` - Get team performance
  - **Parameters**:
    - `date_from` (optional): Start date filter (format: YYYY-MM-DD)
    - `date_to` (optional): End date filter (format: YYYY-MM-DD)
    - `role` (optional): User role filter (default: "worker")
- `GET /api/v1/analytics/productivity/ranking` - Get productivity ranking
  - **Parameters**:
    - `date_from` (optional): Start date filter (format: YYYY-MM-DD)
    - `date_to` (optional): End date filter (format: YYYY-MM-DD)
    - `limit` (optional): Number of results (default: 10)
- `GET /api/v1/analytics/trends/daily` - Get daily trends
  - **Parameters**:
    - `date_from` (optional): Start date filter (format: YYYY-MM-DD)
    - `date_to` (optional): End date filter (format: YYYY-MM-DD)

### Machine Learning

- `POST /api/v1/ml/clustering/analyze` - Perform clustering analysis
- `GET /api/v1/ml/clustering/quick-analysis` - Quick clustering analysis
- `GET /api/v1/ml/clustering/user/{user_id}/predict` - Predict user cluster
- `GET /api/v1/ml/performance/{user_id}/metrics` - Get performance metrics
- `GET /api/v1/ml/performance/{user_id}/insights` - Get AI insights
- `POST /api/v1/ml/clustering/batch-predict` - Batch predict clusters

## 🗄️ Database Schema

### Users Collection (Firebase Firestore)

```json
{
  "id": "string",
  "email": "string",
  "name": "string",
  "role": "worker|manager|admin",
  "status": "active|inactive|suspended",
  "profileImageUrl": "string",
  "workerId": "string",
  "created": "ISO datetime"
}
```

### Attendance Collection (Firebase Firestore)

```json
{
  "id": "string",
  "attendanceId": "string",
  "userId": "string",
  "projectId": "string",
  "date": "YYYY-MM-DD",
  "clockInTime": "HH:MM",
  "clockOutTime": "HH:MM",
  "totalHoursFormatted": "H:MM",
  "totalMinutes": 0,
  "workHoursFormatted": "H:MM",
  "workMinutes": 0,
  "overtimeHoursFormatted": "H:MM",
  "overtimeMinutes": 0,
  "workDescription": "string",
  "workProofIn": "url",
  "workProofOut": "url",
  "status": "approved|pending|rejected"
}
```

## 🤖 Machine Learning Usage

### Quick Start Clustering Analysis

```python
# GET /api/v1/ml/clustering/quick-analysis
# Response will include:
{
  "results": [...],
  "cluster_centers": {...},
  "feature_names": [...],
  "total_users": 10,
  "model_accuracy": 0.85
}
```

### Get User Performance Insights

```python
# GET /api/v1/ml/performance/{user_id}/insights
# Response:
{
  "user_id": "user123",
  "insights": ["Good attendance with room for improvement"],
  "recommendations": ["Focus on improving daily attendance consistency"],
  "strengths": ["Very punctual", "High productivity"],
  "areas_for_improvement": ["Work schedule consistency"]
}
```

## 🔧 Konfigurasi Lanjutan

### Environment Variables Detail

- `FIREBASE_CREDENTIALS_PATH`: Path ke service account JSON
- `FIREBASE_PROJECT_ID`: ID project Firebase
- `CLUSTERING_N_CLUSTERS`: Jumlah cluster untuk K-Means (default: 3)
- `ML_MODEL_PATH`: Directory untuk menyimpan trained models
- `WORKING_HOURS_TARGET`: Target jam kerja per hari (default: 8)
- `PUNCTUALITY_TIME_THRESHOLD`: Batas waktu untuk punctuality (default: 09:00)

### Model Training

Model akan otomatis di-train saat pertama kali menjalankan clustering analysis. Model akan disimpan di directory `models/` dan dapat digunakan untuk prediksi selanjutnya.

## 📈 Monitoring dan Testing

### Health Check

```bash
curl http://localhost:8000/health
```

### Test API Endpoints

```bash
# Get all active workers
curl http://localhost:8000/api/v1/users/workers/active

# Get analytics overview
curl http://localhost:8000/api/v1/analytics/overview

# Perform quick clustering
curl http://localhost:8000/api/v1/ml/clustering/quick-analysis
```

## 🔐 Security & Best Practices

1. **Firebase Credentials**: Jangan commit file credentials ke repository
2. **Environment Variables**: Gunakan `.env` file untuk konfigurasi sensitif
3. **CORS**: Set ALLOWED_ORIGINS sesuai domain frontend yang diizinkan
4. **API Keys**: Simpan semua API keys di environment variables

## 📝 Development

### Adding New Features

1. Create new models in `app/models/`
2. Add business logic in `app/services/`
3. Create API endpoints in `app/api/routes/`
4. Update documentation

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## 🆘 Troubleshooting

### Common Issues

1. **Firebase Connection Error**

   - Check if `config/firebase-credentials.json` exists
   - Verify FIREBASE_PROJECT_ID in .env
   - Ensure Firestore is enabled in Firebase Console

2. **Import Errors**

   - Run `pip install -r requirements.txt`
   - Check if virtual environment is activated

3. **Model Training Fails**
   - Ensure sufficient data in Firebase
   - Check if users have attendance records
   - Verify date range parameters

### Support

Untuk pertanyaan atau issues:

1. Check dokumentasi API di `/docs`
2. Review error logs
3. Verify Firebase setup dengan `python setup_firebase.py`

---

**Note**: Pastikan untuk setup Firebase Firestore dengan benar dan menambahkan service account credentials sebelum menjalankan aplikasi.

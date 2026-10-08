# Intelligent Plant Growth Monitoring and Prediction Framework

An end-to-end precision agriculture capstone project. This framework integrates machine learning predictive models, real-time IoT sensor telemetry streams, automated crop diagnostics, decision-support recommendation engines, PDF report compiling, and role-based user cockpits into a professional MVC Flask application.

---

## 1. System Architecture

The project is structured around the Model-View-Controller (MVC) software design pattern:

```mermaid
graph TD
    subgraph Client Layer
        Browser[Client Browser]
        ESP32[ESP32 / Wokwi IoT Simulator]
    end

    subgraph Controller & Routing Layer
        Router[Flask Routing Blueprints]
        AuthCtrl[Auth Controller]
        DashCtrl[Dashboard Controller]
        PlantCtrl[Plant Controller]
        IotCtrl[IoT Telemetry Controller]
    end

    subgraph Service & ML Layer
        AdvSvc[Recommendation Engine]
        RepSvc[ReportLab PDF Compiler]
        WeaSvc[Weather API Services]
        DiseaseML[HF MobileNetV2 Classifier]
        GrowthML[RF Growth Regressor]
        SeedML[RF Sowing Predictor]
    end

    subgraph Data & Storage Layer
        DB[(SQLite / SQL Database)]
        PKL[serialized ML Models]
    end

    Browser -->|HTTP requests| Router
    ESP32 -->|JSON POST Webhook| Router
    
    Router --> AuthCtrl
    Router --> DashCtrl
    Router --> PlantCtrl
    Router --> IotCtrl
    
    PlantCtrl --> DiseaseML
    PlantCtrl --> GrowthML
    DashCtrl --> AdvSvc
    PlantCtrl --> RepSvc
    IotCtrl --> DB
    
    DiseaseML --> PKL
    GrowthML --> PKL
    SeedML --> PKL
    
    AuthCtrl --> DB
    PlantCtrl --> DB
    RepSvc --> DB
```

---

## 2. Process Flowchart

The plant monitoring lifecycle handles sensor ingestion, predictions, warnings, and PDF downloads:

```mermaid
flowchart TD
    Start([Initialize app.py]) --> DBInit[Load Database & seed Demo Accounts]
    DBInit --> MLInit[Train Growth Regressor & Load Classifiers]
    MLInit --> Run[Server active on Port 8000]
    
    Run --> Login{User Login}
    Login -->|Invalid| Login
    Login -->|Valid| Dash[Farmer Dashboard]
    
    Dash --> Register[Register Crop Profile]
    Register --> Stream[Ingest IoT Telemetry from ESP32 / Wokwi]
    
    Stream --> Analysis{Evaluate Telemetry}
    Analysis -->|Moisture < 35% or Tank < 20%| Notify[Broadcast Danger/Warning Alert]
    Analysis -->|Optimal| Rec[Calculate Irrigation & NPK Fertilizer schedules]
    
    Rec --> Predict[Compute ML Growth Projections]
    Predict --> Diagnosis[Upload Leaf Image for HF Disease Classification]
    Diagnosis --> PDF[Compile PDF ReportLab Summary Sheet]
    PDF --> End([Download PDF Report])
```

---

## 3. Entity-Relationship (ER) Diagram

The SQLite schema represents the relational mappings of user data:

```mermaid
erDiagram
    USERS {
        int id PK
        string username
        string email
        string password_hash
        string role
        datetime created_at
    }
    PLANTS {
        int id PK
        string name
        string crop_type
        datetime sowing_date
        int age_days
        string status
        float height_cm
        string soil_type
        int user_id FK
        datetime created_at
    }
    SENSOR_READINGS {
        int id PK
        int plant_id FK
        float temperature
        float humidity
        float soil_moisture
        float soil_ph
        float light_intensity
        float rain_level
        float water_tank_level
        datetime timestamp
    }
    DISEASE_DIAGNOSES {
        int id PK
        int plant_id FK
        string disease_name
        float confidence
        string severity
        text description
        text causes
        text prevention
        string recommended_fertilizer
        string recommended_fungicide
        string recovery_time
        string image_path
        datetime timestamp
    }
    GROWTH_PREDICTIONS {
        int id PK
        int plant_id FK
        string current_stage
        float predicted_height
        float growth_rate
        float height_7d
        float height_30d
        datetime estimated_harvest
        float health_score
        datetime timestamp
    }
    NOTIFICATIONS {
        int id PK
        int user_id FK
        text message
        string category
        boolean is_read
        datetime timestamp
    }

    USERS ||--o{ PLANTS : owns
    USERS ||--o{ NOTIFICATIONS : receives
    PLANTS ||--o{ SENSOR_READINGS : monitors
    PLANTS ||--o{ DISEASE_DIAGNOSES : diagnoses
    PLANTS ||--o{ GROWTH_PREDICTIONS : predicts
```

---

## 4. Installation & Setup Guide

Ensure Python 3.13 is installed on your Windows machine, then run:

```powershell
# 1. Activate the environment
venv\Scripts\activate

# 2. Install all required dependencies
pip install -r requirements.txt

# 3. Launch the framework
python app.py
```

### Accessing Demo Portals
During database initialization, the framework automatically seeds two demo user profiles:
- **Farmer Portal:** Username: `farmer` | Password: `farmer123`
- **Admin Portal:** Username: `admin` | Password: `admin123`

---

## 5. API Reference Documentation

### Authentication Blueprints
- **`POST /register`**
  Registers a new User credentials profile (fields: `username`, `email`, `password`, `role`).
- **`POST /login`**
  Authenticates sessions and redirects user to dashboard view.

### Crop Registry & Modeling
- **`POST /plants/add`**
  Registers a new crop profile (fields: `name`, `crop_type`, `soil_type`, `height_cm`, `sowing_date`).
- **`POST /plants/<id>/predict`**
  Computes random forest growth projection regression modeling.
- **`POST /plants/<id>/diagnose`**
  Uploads a leaf image and runs Hugging Face disease classification.
- **`GET /plants/<id>/report`**
  Compiles and downloads a formatted PDF report summary sheet.

### Live IoT Integrations
- **`POST /api/telemetry`**
  Receives JSON telemetry from ESP32/Wokwi.
  Format: `{"plant_id": 1, "temperature": 26.5, "humidity": 62, "soil_moisture": 52.3, "soil_ph": 6.8}`
- **`POST /api/telemetry/simulate`**
  Batch updates sensor readings for testing.

---

## 6. Project Report Summary

### Project Goal
Farming often suffers from manual resource allocations, leading to high water wastage and misdiagnosed crop pathogens. The **Intelligent Plant Growth Monitoring and Prediction Framework** provides an integrated precision farming toolkit, replacing guesswork with data-driven machine learning models.

### Key Achievements
1. **End-to-End IoT Telemetry:** Implemented custom animated Gauges and JSON endpoints capable of receiving continuous ESP32 streams.
2. **Machine Learning Growth Modeling:** Generated custom growth profiles and trained a multi-output `Random Forest Regressor` to forecast height progression (7-day and 30-day), growth rates, and health indices.
3. **Farming Advice Engine:** Created algorithmic rules parsing telemetry trends to recommend precise irrigation volumes (in ml) and balanced NPK fertilizer weights.
4. **Structured MVC Design:** Transformed the single-file script into a clean, modular MVC directory hierarchy.

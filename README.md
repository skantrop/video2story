# Video2Story
### Automatic Video Scene Understanding and Narrative Generation

Video2Story is a system that analyzes videos, extracts visual scenes, generates scene descriptions using AI models, and composes a coherent narrative of the video content.

The project demonstrates how modern **computer vision and multimodal AI models** can transform raw video data into structured semantic information and human-readable storytelling.

This project was developed as part of a **thesis on automated video understanding and narrative generation**.

---

# Overview

Video content contains rich visual information but is difficult to analyze automatically. Video2Story addresses this by building a pipeline that:

1. Extracts snapshots from videos
2. Groups frames into scenes
3. Selects representative keyframes
4. Generates scene descriptions using AI models
5. Produces a structured narrative summarizing the video

The system allows users to upload a video and interactively explore the detected scenes and AI-generated descriptions.

---

# Features

- Upload and process video files  
- Automatic snapshot extraction  
- Scene detection and segmentation  
- Keyframe selection  
- AI-based scene description  
- Narrative generation from scenes  
- Interactive web interface  
- Visual scene exploration with thumbnails  

---

# System Architecture

The system consists of two main components.

## Backend (FastAPI)

Responsible for:

- Video processing  
- Scene detection  
- Keyframe extraction  
- AI inference  
- API endpoints  
- Data storage  

**Technologies**

- Python  
- FastAPI  
- FFmpeg  
- OpenCV  
- HuggingFace models  

---

## Frontend (React + Vite)

Provides the user interface for:

- Uploading videos  
- Viewing jobs  
- Exploring scenes  
- Viewing keyframes  
- Generating descriptions and narratives  

**Technologies**

- React  
- Vite  
- JavaScript  

---

# Requirements

### Backend

- Python 3.10+
- FFmpeg
- Virtual environment

### Frontend

- Node.js 18+
- npm

---

# Environment Variables

Create a `.env` file inside the **backend directory**.

Example:
DATABASE_URL=your_database_url
DATA_DIR=your_data_directory
HF_TOKEN=your_hugging_face_token
HF_VLM_MODEL =your_your_hugging_face_vlm_model
HF_LLM_MODEL=your_your_hugging_face_llm_model

Token is required to access the HuggingFace models used for scene description.

---

# Installation

Clone the repository:

```bash
git clone https://github.com/your-repo/video2story.git
cd video2story



## Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
## Frontend Setup

```bash
cd frontend
npm install
```
---
# Running the Application

## Run both frontend and backend:
```bash
make dev
```

## Run backend only
```bash
make backend
```

## Run frontend only:
```bash
make frontend
```

## Run tests:
```bash
make test
```
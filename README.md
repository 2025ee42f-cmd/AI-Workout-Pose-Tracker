# AI Workout Pose Tracker

An all-in-one AI fitness web application built with **Streamlit**, **OpenCV**, and **MediaPipe**. It features real-time webcam pose detection with automated rep counting, personalized diet planning, and a built-in AI fitness assistant.

## Screenshots

### 1. Real-Time Pose Detection & Rep Counter
![Pose Detection](<Screenshot 1.png>)

### 2. Personalized Diet & Nutrition Plan
![Diet Plan](<Screenshot 2.png>)

### 3. AI Fitness Assistant
![AI Fitness Assistant](<Screenshot 3.png>)

## Features
- **Live Pose Estimation:** Real-time body landmark detection and joint angle calculation using **MediaPipe Pose** and **NumPy**
- **Automated Rep Counter:** Tracks exercise form and counts repetitions live via **OpenCV**
- **Personalized Diet Planner:** Provides tailored meal and nutrition recommendations based on user fitness goals
- **AI Fitness Assistant:** Interactive assistant for answering workout, form, and nutrition questions directly inside the app

## Tech Stack
- **Python 3.11**
- **Streamlit** (Web UI, diet planner & assistant interface)
- **OpenCV (`opencv-python`)** (Webcam capture & video overlay)
- **MediaPipe (`0.10.14`)** (Pose landmark detection)
- **NumPy** (Joint angle calculations)

## Setup & Installation
1. Clone the repository:
   ```bash
   git clone https://github.com
   cd AI-Workout-Pose-Tracker
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

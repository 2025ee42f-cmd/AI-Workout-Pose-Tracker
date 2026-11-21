import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

st.set_page_config(page_title="AI Gym Assistant", layout="wide")

def calculate_angle(a, b, c):
    """Calculates the angle between three points."""
    a = np.array(a) # Shoulder
    b = np.array(b) # Elbow
    c = np.array(c) # Wrist
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
    return angle

def main():
    st.sidebar.title("AI Gym Assistant")
    st.sidebar.markdown("---")
    
    app_mode = st.sidebar.radio(
        "Select a Module:",
        ["AI Gym Trainer", "AI Dietician", "Smart Gym (IoT)"]
    )
    
    # --- MODULE 1: GYM TRAINER ---
    if app_mode == "AI Gym Trainer":
        st.title("Live Push/Pull Up Rep Counter")
        st.write("Check the box below to activate your webcam and start your set.")
        
        run_camera = st.checkbox("Start Tracker")
        FRAME_WINDOW = st.image([])
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Total Reps")
            rep_text = st.empty() 
        with col2:
            st.markdown("### Form Stage")
            stage_text = st.empty()

        counter = 0
        stage = "Up"

        if run_camera:
            cap = cv2.VideoCapture(0)
            
            with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
                while run_camera:
                    ret, frame = cap.read()
                    if not ret:
                        st.error("Failed to access webcam.")
                        break
                    
                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image.flags.writeable = False
                    
                    results = pose.process(image)
                    image.flags.writeable = True
                    
                    if results.pose_landmarks:
                        landmarks = results.pose_landmarks.landmark
                        
                        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                        
                        angle = calculate_angle(shoulder, elbow, wrist)
                        
                        cam_height, cam_width, _ = image.shape
                        elbow_coords = tuple(np.multiply(elbow, [cam_width, cam_height]).astype(int))
                        cv2.putText(image, str(int(angle)), elbow_coords, 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
                        
                        if angle > 160:
                            stage = "Down"
                        elif angle < 30 and stage == 'Down':
                            stage = "Up"
                            counter += 1
                        
                        mp_drawing.draw_landmarks(
                            image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                            mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                            mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                        )
                    
                    rep_text.markdown(f"<h1 style='color: #FF4B4B;'>{counter}</h1>", unsafe_allow_html=True)
                    stage_text.markdown(f"<h1>{stage}</h1>", unsafe_allow_html=True)
                    
                    FRAME_WINDOW.image(image)
                    
            cap.release()
            
    # --- MODULE 2: DIETICIAN ---
    elif app_mode == "AI Dietician":
        st.title("AI Dietician & Calorie Coach")
        st.write("Enter your stats below to get a custom daily calorie and macronutrient breakdown.")
        
        # --- INPUT FORM ---
        with st.form("diet_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                age = st.number_input("Age", min_value=15, max_value=100, value=25)
                gender = st.selectbox("Gender", ["Male", "Female"])
            
            with col2:
                weight_kg = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0)
                height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0)
                
            with col3:
                activity_level = st.selectbox(
                    "Activity Level", 
                    ["Office Job", 
                     "Lightly Active (1-3 days/week)", 
                     "Moderately Active (3-5 days/week)", 
                     "Very Active (6-7 days/week)"]
                )
                goal = st.select_slider("Fitness Goal", options=["Lose Fat", "Maintain", "Bulk (Build Muscle)"])
            
            submit_button = st.form_submit_button(label="Calculate My Macros")

        # --- MATH & LOGIC ---
        if submit_button:
            st.markdown("---")
            
            # 1. Calculate Basal Metabolic Rate (BMR)
            if gender == "Male":
                bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
            else:
                bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
                
            # 2. Activity Multiplier for TDEE
            activity_multipliers = {
                "Office Job": 1.2,
                "Lightly Active (1-3 days/week)": 1.375,
                "Moderately Active (3-5 days/week)": 1.55,
                "Very Active (6-7 days/week)": 1.725
            }
            tdee = bmr * activity_multipliers[activity_level]
            
            # 3. Adjust for Goal
            if goal == "Lose Fat":
                target_calories = tdee - 500
            elif goal == "Bulk (Build Muscle)":
                target_calories = tdee + 500
            else:
                target_calories = tdee
                
            # 4. Macro Calculation (General Bodybuilding Split)
            # Protein: 2g per kg of bodyweight (4 cals per gram)
            # Fats: 0.8g per kg of bodyweight (9 cals per gram)
            # Carbs: The rest of the calories (4 cals per gram)
            protein_g = weight_kg * 2.0
            fats_g = weight_kg * 0.8
            
            protein_cals = protein_g * 4
            fats_cals = fats_g * 9
            carbs_cals = target_calories - (protein_cals + fats_cals)
            carbs_g = carbs_cals / 4
            
            st.subheader("Your Daily Nutrition Targets")
            
            st.metric(label="Target Daily Calories", value=f"{int(target_calories)} kcal")
            
            mac1, mac2, mac3 = st.columns(3)
            with mac1:
                st.info(f"**Protein:**\n\n {int(protein_g)}g ({int(protein_cals)} kcal)")
            with mac2:
                st.warning(f"**Carbs:**\n\n {int(carbs_g)}g ({int(carbs_cals)} kcal)")
            with mac3:
                st.error(f"**Fats:**\n\n {int(fats_g)}g ({int(fats_cals)} kcal)")
                    
    # --- MODULE 3: IOT ---
    elif app_mode == "Smart Gym (IoT)":
        import random
        
        st.title("Smart Gym: AI + IoT Integration")
        st.write("Live adaptive AI coaching based on your real-time performance.")
        
        # --- 1. SIDEBAR
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Live Workout Sensors")
        st.sidebar.write("Adjust sliders to simulate live data.")
        current_hr = st.sidebar.slider("💓 Heart Rate (BPM)", 60, 200, 135)
        rep_speed = st.sidebar.slider("⚡ Rep Speed (s/rep)", 0.5, 5.0, 1.5)
        current_weight = st.sidebar.slider("🏋️ Current Resistance (kg)", 5.0, 100.0, 20.0, step=2.5)
        
        def analyze_telemetry(hr, speed, weight):
            target_hr_zone = (120, 160)
            rec = {"status": "Optimal", "color": "🟢", "rest": 60, "weight_adj": 0.0, "msg": "Perfect pace."}
            
            if hr > target_hr_zone[1]:
                rec.update({"status": "Overtraining Warning", "color": "🔴", "rest": 120, "weight_adj": -5.0, "msg": "Heart rate peaking above target zone. Reduce intensity or increase rest to avoid overtraining."})
            elif speed > 3.5:
                rec.update({"status": "Muscular Fatigue", "color": "🟠", "rest": 90, "weight_adj": -2.5, "msg": "Consider reducing weight or increasing rest time."})
            elif hr < target_hr_zone[0] and speed < 1.0:
                rec.update({"status": "Under-Stimulated", "color": "🔵", "rest": 45, "weight_adj": 5.0, "msg": "Weight is moving too easily. Increase resistance to improve muscle activation."})
            
            rec["new_weight"] = max(2.5, weight + rec["weight_adj"])
            return rec

        ai_data = analyze_telemetry(current_hr, rep_speed, current_weight)

        # --- 2. AI PERFORMANCE COACH ---
        st.subheader(f"AI Coach Status: {ai_data['color']} {ai_data['status']}")
        st.info(f"**AI Analysis:** {ai_data['msg']}")
        
        with st.container():
            rec1, rec2, rec3 = st.columns(3)
            
            # AI Resistance Adjustments
            delta_color = "normal" if ai_data['weight_adj'] >= 0 else "inverse"
            delta_str = f"{ai_data['weight_adj']} kg" if ai_data['weight_adj'] != 0 else "No Change"
            rec1.metric("Target Resistance", f"{ai_data['new_weight']} kg", delta_str, delta_color=delta_color)
            
            # AI Rest Adjustments
            rec2.metric("Optimal Rest Timer", f"{ai_data['rest']} Seconds")
         # --- AI DYNAMIC CALORIE CALCULATION ---
            # This formula reacts to your Heart Rate and Resistance
            dynamic_cals = int((current_hr * current_weight) / 50)
            
            rec3.metric("Calories Burned", f"{dynamic_cals} kcal")
            
        st.markdown("<br>", unsafe_allow_html=True)
        hr_percentage = min(int((current_hr / 200) * 100), 100)
        st.write(f"**Cardiovascular Load:** {hr_percentage}% of Max HR")
        st.progress(hr_percentage / 100)

if __name__ == "__main__":
    main()
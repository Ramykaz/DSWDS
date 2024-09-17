from flask import Flask, render_template, request, redirect, url_for, flash
import cv2
import os
from ultralytics import YOLO
from werkzeug.utils import secure_filename
import time

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = "supersecretkey"

# Load the YOLOv8 model
model = YOLO("static/weights/best.pt")

UPLOAD_FOLDER = 'static/uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

def draw_boxes(image, results):
    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            label = box.cls[0].item()
            conf = box.conf[0].item()
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, f'{model.names[int(label)]} {conf:.2f}', (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    return image

@app.route('/detect_image', methods=['POST'])
def detect_image():
    if 'image' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['image']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        image = cv2.imread(filepath)
        results = model(filepath)
        image_with_boxes = draw_boxes(image, results)
        
        output_path = os.path.join(UPLOAD_FOLDER, "output_" + filename)
        cv2.imwrite(output_path, image_with_boxes)
        
        detected_objects = [model.names[int(box.cls[0].item())] for result in results for box in result.boxes]
        detected_message = ', '.join(set(detected_objects)) if detected_objects else "No driver or steering wheel detected."
        
        return render_template('index.html', image_url="uploads/output_" + filename, detected_message=detected_message)
    return redirect(url_for('index'))


@app.route('/detect_video', methods=['POST'])
def detect_video():
    if 'video' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['video']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        cap = cv2.VideoCapture(filepath)
        if not cap.isOpened():
            flash('Error opening video file')
            return redirect(request.url)

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        output_path = os.path.join(UPLOAD_FOLDER, "output_" + filename)
        out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            results = model(frame)
            frame_with_boxes = draw_boxes(frame, results)
            out.write(frame_with_boxes)

        cap.release()
        out.release()

        return render_template('index.html', video_url="uploads/output_" + filename, detected_message="Video detection complete.")
    
    return redirect(url_for('index'))

@app.route('/detect_realtime')
def detect_realtime():
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        flash('Error opening video capture')
        return redirect(url_for('index'))
    
    output_path = os.path.join(UPLOAD_FOLDER, 'realtime_detection.mp4')
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = 20  # Assuming a common FPS value; adjust as needed
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        results = model(frame)
        frame_with_boxes = draw_boxes(frame, results)
        out.write(frame_with_boxes)
        
        # Instead of cv2.imshow, we save and show the video on the webpage
        # cv2.imshow('Real-Time Detection', frame_with_boxes)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    
    return render_template('index.html', video_url="uploads/realtime_detection.mp4", detected_message="Real-time detection complete.")

if __name__ == '__main__':
    app.run(debug=True)

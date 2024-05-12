


from flask import Flask, jsonify
import cv2
import pandas as pd
import numpy as np
import multiprocessing
import time
from ultralytics import YOLO
import json


model = YOLO('models/yolov8s.pt')

with open("data/coco.txt", "r") as file:
    class_list = file.read().split("\n")


with open('data/config.json', 'r') as f:
    parkings = json.load(f)

def process_parking(parking, parking_statuses):
    cap = cv2.VideoCapture(parking['video_path'])
    parking_areas = parking['areas']
    first_seen = {i: None for i in range(len(parking_areas))}
    last_seen = {i: None for i in range(len(parking_areas))}
    min_parked_time = 3  
    min_clear_time = 2  

    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        results = model.predict(frame)
        boxes_data = results[0].boxes.data
        px = pd.DataFrame(boxes_data).astype("float")
        current_time = time.time()
        occupied = [False] * len(parking_areas)

        for index, row in px.iterrows():
            if 'car' in class_list[int(row[5])]:
                cx, cy = int((row[0] + row[2]) // 2), int((row[1] + row[3]) // 2)
                for i, area in enumerate(parking_areas):
                    if cv2.pointPolygonTest(np.array(area, np.int32), (cx, cy), False) >= 0:
                        last_seen[i] = current_time
                        if first_seen[i] is None:
                            first_seen[i] = current_time
                        elif current_time - first_seen[i] > min_parked_time:
                            occupied[i] = True
                        break

        for i, area in enumerate(parking_areas):
            if last_seen[i] is not None and current_time - last_seen[i] > min_clear_time:
                first_seen[i] = None
                last_seen[i] = None
                occupied[i] = False

        parking_statuses[parking['id']] = occupied
        time.sleep(1)

app = Flask(__name__)

def format_parking_status(parking_config, status):
    rows = parking_config['layout']['rows']
    formatted_status = []
    index = 0
    for row in rows:
        row_status = status[index:index + row['count']]
        formatted_status.append(row_status)
        index += row['count']
    return formatted_status


@app.route('/parkings/<parking_id>', methods=['GET'])
def get_parking_status(parking_id):
    parking = next((p for p in parkings['parkings'] if p['id'] == parking_id), None)
    if not parking:
        return jsonify({"error": "Parking not found"}), 404
    status = parking_statuses.get(parking_id)
    formatted_status = format_parking_status(parking, status)
    return jsonify({"parking_id": parking_id, "address": parking['address'], "status": formatted_status})


@app.route('/parkings', methods=['GET'])
def get_parkings_list():
    parkings_list = [{'id': parking['id'], 'address': parking['address']} for parking in parkings['parkings']]
    return jsonify(parkings_list)


if __name__ == '__main__':
    manager = multiprocessing.Manager()
    parking_statuses = manager.dict()

    processes = []
    for parking in parkings['parkings']:
        p = multiprocessing.Process(target=process_parking, args=(parking, parking_statuses))
        p.start()
        processes.append(p)
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    for p in processes:
        p.join()

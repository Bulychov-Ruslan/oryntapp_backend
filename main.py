# # Кітапханаларды импорттау
# from flask import Flask, jsonify
# import cv2
# import pandas as pd
# import numpy as np
# import multiprocessing
# import time
# from ultralytics import YOLO
# import json


# try:
#     # YOLO моделін жүктеу
#     model = YOLO('models/yolov8s.pt')
# except Exception as e:
#     print(f"Ошибка загрузки модели: {str(e)}")
#     model = None

# try:
#     # Класстар файлын оқу
#     with open("data/coco.txt", "r") as file:
#         class_list = file.read().split("\n")
# except FileNotFoundError:
#     print("Файл классов не найден.")
#     class_list = []
# except Exception as e:
#     print(f"Ошибка при чтении файла классов: {str(e)}")
#     class_list = []

# # Автотұрақтардың мәліметтерін оқу
# with open('data/config.json', 'r') as f:
#     parkings = json.load(f)

# # Автотұрақтардың мәліметтерін өңдеу функциясы
# def process_parking(parking, parking_statuses):
#     """
#     Белгілі бір тұрақ үшін бейне ағынын өңдейді және бос орындардың күйін жаңартады.
#     Args:
#         parking: тұрақ туралы ақпаратты қамтитын сөздік.
#         parking_statuses: тұрақ күйлерінің жалпы сөздігі.
#     """
#     cap = cv2.VideoCapture(parking['video_path'])
#     parking_areas = parking['areas']
#     first_seen = {i: None for i in range(len(parking_areas))}
#     last_seen = {i: None for i in range(len(parking_areas))}
#     min_parked_time = 3  
#     min_clear_time = 2  

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
#             continue

#         results = model.predict(frame)
#         boxes_data = results[0].boxes.data
#         px = pd.DataFrame(boxes_data).astype("float")
#         current_time = time.time()
#         occupied = [False] * len(parking_areas)

#         for index, row in px.iterrows():
#             if 'car' in class_list[int(row[5])]:
#                 cx, cy = int((row[0] + row[2]) // 2), int((row[1] + row[3]) // 2)
#                 for i, area in enumerate(parking_areas):
#                     if cv2.pointPolygonTest(np.array(area, np.int32), (cx, cy), False) >= 0:
#                         last_seen[i] = current_time
#                         if first_seen[i] is None:
#                             first_seen[i] = current_time
#                         elif current_time - first_seen[i] > min_parked_time:
#                             occupied[i] = True
#                         break

#         for i, area in enumerate(parking_areas):
#             if last_seen[i] is not None and current_time - last_seen[i] > min_clear_time:
#                 first_seen[i] = None
#                 last_seen[i] = None
#                 occupied[i] = False

#         parking_statuses[parking['id']] = occupied
#         time.sleep(1)

# # Flask серверін инициалдау
# app = Flask(__name__)

# # Автотұрақтардың мәліметтерін форматтау
# def format_parking_status(parking_config, status):
#     """
#     API арқылы көрсету үшін тұрақ орындарының күйін пішімдейді.
#     Args:
#         parking_config: тұрақ конфигурациясы.
#         status: Орындардың толтырылу күйі.
#     Returns:
#         Орындардың пішімделген күйі.
#     """
#     rows = parking_config['layout']['rows']
#     formatted_status = []
#     index = 0
#     for row in rows:
#         row_status = status[index:index + row['count']]
#         formatted_status.append(row_status)
#         index += row['count']
#     return formatted_status

# # Автотұрақтардың мәліметтерін алу маршруты
# @app.route('/parkings/<parking_id>', methods=['GET'])
# # Автотұрақтардың мәліметтерін алу
# def get_parking_status(parking_id):

#     """
#     Оның идентификаторы бойынша тұрақ мәртебесін алуға арналған API әдісі.
#     Args:
#         parking_id: тұрақ идентификаторы.
#     Returns:
#         Тұрақ күйі бар JSON жауабы.
#     """
#     parking = next((p for p in parkings['parkings'] if p['id'] == parking_id), None)
#     if not parking:
#         return jsonify({"error": "Parking not found"}), 404
#     status = parking_statuses.get(parking_id)
#     formatted_status = format_parking_status(parking, status)
#     return jsonify({"parking_id": parking_id, "address": parking['address'], "status": formatted_status})

# # Автотұрақтардың тізімін алу маршруты
# @app.route('/parkings', methods=['GET'])
# # Автотұрақтардың тізімін алу
# def get_parkings_list():
#     """
#     Барлық тұрақтардың тізімін алуға арналған API әдісі.
#     Returns:
#         JSON тұрақтарының тізімі.
#     """
#     parkings_list = [{'id': parking['id'], 'address': parking['address']} for parking in parkings['parkings']]
#     return jsonify(parkings_list)

# # Flask серверін іске қосу
# if __name__ == '__main__':
#     manager = multiprocessing.Manager()
#     parking_statuses = manager.dict()
    
#     processes = []
#     for parking in parkings['parkings']:
#         p = multiprocessing.Process(target=process_parking, args=(parking, parking_statuses))
#         p.start()
#         processes.append(p)
    
#     app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
#     for p in processes:
#         p.join()




# from flask import Flask, jsonify, request
# import cv2
# import pandas as pd
# import numpy as np
# import multiprocessing
# import time
# from ultralytics import YOLO
# import json

# try:
#     model = YOLO('models/yolov8s.pt')
# except Exception as e:
#     print(f"Ошибка загрузки модели: {str(e)}")
#     model = None

# try:
#     with open("data/coco.txt", "r") as file:
#         class_list = file.read().split("\n")
# except FileNotFoundError:
#     print("Файл классов не найден.")
#     class_list = []
# except Exception as e:
#     print(f"Ошибка при чтении файла классов: {str(e)}")
#     class_list = []

# with open('data/config.json', 'r') as f:
#     parkings = json.load(f)

# def process_parking(parking, parking_statuses, reservations):
#     cap = cv2.VideoCapture(parking['video_path'])
#     parking_areas = parking['areas']
#     first_seen = {i: None for i in range(len(parking_areas))}
#     last_seen = {i: None for i in range(len(parking_areas))}
#     min_parked_time = 3  
#     min_clear_time = 2  

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
#             continue

#         results = model.predict(frame)
#         boxes_data = results[0].boxes.data
#         px = pd.DataFrame(boxes_data).astype("float")
#         current_time = time.time()
#         occupied = [False] * len(parking_areas)

#         for index, row in px.iterrows():
#             if 'car' in class_list[int(row[5])]:
#                 cx, cy = int((row[0] + row[2]) // 2), int((row[1] + row[3]) // 2)
#                 for i, area in enumerate(parking_areas):
#                     if cv2.pointPolygonTest(np.array(area, np.int32), (cx, cy), False) >= 0:
#                         last_seen[i] = current_time
#                         if first_seen[i] is None:
#                             first_seen[i] = current_time
#                         elif current_time - first_seen[i] > min_parked_time:
#                             occupied[i] = True
#                         break

#         for i, area in enumerate(parking_areas):
#             if last_seen[i] is not None and current_time - last_seen[i] > min_clear_time:
#                 first_seen[i] = None
#                 last_seen[i] = None
#                 occupied[i] = False

#         # Учет бронирований
#         if parking['id'] not in reservations:
#             reservations[parking['id']] = [None] * len(parking_areas)
        
#         for i in range(len(parking_areas)):
#             if reservations[parking['id']][i] is not None:
#                 reserved_until = reservations[parking['id']][i]
#                 if reserved_until > current_time:
#                     occupied[i] = True
#                 else:
#                     reservations[parking['id']][i] = None

#         parking_statuses[parking['id']] = occupied
#         time.sleep(1)

# app = Flask(__name__)

# def format_parking_status(parking_config, status):
#     rows = parking_config['layout']['rows']
#     formatted_status = []
#     index = 0
#     for row in rows:
#         row_status = status[index:index + row['count']]
#         formatted_status.append(row_status)
#         index += row['count']
#     return formatted_status

# @app.route('/parkings/<parking_id>', methods=['GET'])
# def get_parking_status(parking_id):
#     parking = next((p for p in parkings['parkings'] if p['id'] == parking_id), None)
#     if not parking:
#         return jsonify({"error": "Parking not found"}), 404
#     status = parking_statuses.get(parking_id)
#     formatted_status = format_parking_status(parking, status)
#     return jsonify({"parking_id": parking_id, "address": parking['address'], "status": formatted_status})

# @app.route('/parkings', methods=['GET'])
# def get_parkings_list():
#     parkings_list = [{'id': parking['id'], 'address': parking['address']} for parking in parkings['parkings']]
#     return jsonify(parkings_list)

# @app.route('/parkings/<parking_id>/book', methods=['POST'])
# def book_parking_space(parking_id):
#     data = request.get_json()
#     row = data.get('row')
#     index = data.get('index')
#     duration = data.get('duration')
#     parking = next((p for p in parkings['parkings'] if p['id'] == parking_id), None)
#     if not parking:
#         return jsonify({"error": "Parking not found"}), 404
    
#     flat_index = sum(row['count'] for row in parking['layout']['rows'][:row]) + index
#     reservation_time = time.time() + duration * 60
#     if parking_id not in reservations:
#         reservations[parking_id] = [None] * sum(row['count'] for row in parking['layout']['rows'])
#     reservations[parking_id][flat_index] = reservation_time
#     return jsonify({"status": "success"}), 200

# @app.route('/parkings/<parking_id>/cancel', methods=['POST'])
# def cancel_parking_reservation(parking_id):
#     data = request.get_json()
#     row = data.get('row')
#     index = data.get('index')
#     parking = next((p for p in parkings['parkings'] if p['id'] == parking_id), None)
#     if not parking:
#         return jsonify({"error": "Parking not found"}), 404
    
#     flat_index = sum(row['count'] for row in parking['layout']['rows'][:row]) + index
#     if parking_id not in reservations:
#         return jsonify({"error": "No reservations found"}), 404
#     reservations[parking_id][flat_index] = None
#     return jsonify({"status": "success"}), 200

# if __name__ == '__main__':
#     manager = multiprocessing.Manager()
#     parking_statuses = manager.dict()
#     reservations = manager.dict()
    
#     processes = []
#     for parking in parkings['parkings']:
#         p = multiprocessing.Process(target=process_parking, args=(parking, parking_statuses, reservations))
#         p.start()
#         processes.append(p)
    
#     app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
#     for p in processes:
#         p.join()








# Python
from flask import Flask, jsonify, request
import cv2
import pandas as pd
import numpy as np
import multiprocessing
import time
from ultralytics import YOLO
import json

try:
    model = YOLO('models/yolov8s.pt')
except Exception as e:
    print(f"Ошибка загрузки модели: {str(e)}")
    model = None

try:
    with open("data/coco.txt", "r") as file:
        class_list = file.read().split("\n")
except FileNotFoundError:
    print("Файл классов не найден.")
    class_list = []
except Exception as e:
    print(f"Ошибка при чтении файла классов: {str(e)}")
    class_list = []

with open('data/config.json', 'r') as f:
    parkings = json.load(f)

reservations = {}

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
    current_time = time.time()
    active_reservations = {str(index): expiration for (p_id, index), expiration in reservations.items() if p_id == parking_id and expiration > current_time}
    return jsonify({"parking_id": parking_id, "address": parking['address'], "status": formatted_status, "reservations": active_reservations})

@app.route('/reserve', methods=['POST'])
def reserve_parking_spot():
    data = request.get_json()
    parking_id = data['parkingId']
    spot_index = data['spotIndex']
    duration = data['duration']

    expiration_time = time.time() + duration
    reservations[(parking_id, spot_index)] = expiration_time
    return jsonify({"success": True})

@app.route('/cancel_reservation', methods=['POST'])
def cancel_reservation():
    data = request.get_json()
    parking_id = data['parkingId']
    spot_index = data['spotIndex']

    if (parking_id, spot_index) in reservations:
        del reservations[(parking_id, spot_index)]
        return jsonify({"success": True})
    else:
        return jsonify({"error": "Reservation not found"}), 404

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

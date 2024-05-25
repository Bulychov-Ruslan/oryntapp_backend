from flask import Flask, jsonify, request  # Flask-тан қажетті модульдерді импорттаймыз
import cv2  # Видеомен жұмыс істеу үшін OpenCV импорттаймыз
import pandas as pd  # Деректермен жұмыс істеу үшін Pandas импорттаймыз
import numpy as np  # Массивтермен жұмыс істеу үшін NumPy импорттаймыз
import multiprocessing  # Көппроцессорлы өңдеу үшін multiprocessing импорттаймыз
import time  # Уақытты өлшеу үшін time модулін импорттаймыз
from ultralytics import YOLO  # Нысандарды анықтау үшін YOLO импорттаймыз
import json  # Конфигурациялық файлдармен жұмыс істеу үшін JSON импорттаймыз

# YOLO моделін жүктеу
try:
    model = YOLO('models/yolov8s.pt')
except Exception as e:
    print(f"Model loading error: {str(e)}")
    model = None

# Кластар файлын оқу
try:
    with open("data/coco.txt", "r") as file:
        class_list = file.read().split("\n")
except FileNotFoundError:
    print("Class file not found.")
    class_list = []
except Exception as e:
    print(f"Error reading class file: {str(e)}")
    class_list = []

# Тұрақтар конфигурациялық файлын оқу
with open('data/config.json', 'r') as f:
    parkings = json.load(f)

reservations = {}  # Резервтеулерді сақтау үшін сөздік

def process_parking(parking, parking_statuses):
    """
    Тұрақтың бейнесін өңдейді және тұрақ орындарының статусын анықтайды.
    
    YOLO моделін пайдаланып, бейнедегі нысандарды анықтайды.
    Жалпы parking_statuses сөздігінде тұрақ орындарының күйін жаңартады.

    Аргументтер:
    parking -- тұрақ конфигурациясы, бейне жолы мен тұрақ аймақтарын қамтиды
    parking_statuses -- тұрақ орындарының күйлерін сақтау үшін жалпы сөздік
    """
    cap = cv2.VideoCapture(parking['video_path'])  # Бейне файлды ашамыз
    parking_areas = parking['areas']  # Тұрақ аймақтарын аламыз
    first_seen = {i: None for i in range(len(parking_areas))}  # Бірінші рет көрінген уақыт
    last_seen = {i: None for i in range(len(parking_areas))}  # Соңғы рет көрінген уақыт
    min_parked_time = 3  # Орынды бос емесін анықтау үшін ең аз уақыт
    min_clear_time = 2  # Орын босатуды анықтаудың ең аз уақыты

    while True:
        ret, frame = cap.read()  # Бейненің кадрын оқу
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Соңына жеткенде бейнені басына қайтарамыз
            continue

        results = model.predict(frame)  # YOLO моделін пайдаланып болжау
        boxes_data = results[0].boxes.data  # Бокс деректерін аламыз
        px = pd.DataFrame(boxes_data).astype("float")  # Деректерді DataFrame-ге түрлендіреміз
        current_time = time.time()  # Ағымдағы уақыт
        occupied = [False] * len(parking_areas)  # Тұрақ орындарының толтырылу күйі

        for index, row in px.iterrows():
            if 'car' in class_list[int(row[5])]:  # Анықталған нысанның көлік екенін тексереміз
                cx, cy = int((row[0] + row[2]) // 2), int((row[1] + row[3]) // 2)  # Бокс орталығы
                for i, area in enumerate(parking_areas):
                    if cv2.pointPolygonTest(np.array(area, np.int32), (cx, cy), False) >= 0:  # Бокс орталығы тұрақ аймағының ішінде екенін тексереміз
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

        parking_statuses[parking['id']] = occupied  # Тұрақтың күйлерін жаңартамыз
        time.sleep(1)  # Келесі итерацияға дейін кідіріс

app = Flask(__name__)  # Flask-тің экземплярын жасаймыз

def format_parking_status(parking_config, status):
    """
    Тұрақтың күйін тұрақ конфигурациясына сәйкес форматтайды.
    
    Жолдарға бөлінген тұрақ орындарының күй тізімін қайтарады.

    Аргументтер:
    parking_config -- тұрақ конфигурациясын қамтиды
    status -- тұрақ орындарының ағымдағы күйі
    """
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
    """
    Тұрақтың күйін оның ID бойынша алу маршруты.
    
    Тұрақ орындарының ағымдағы күйін және брондалуын қайтарады.

    Аргументтер:
    parking_id -- тұрақтың ID-сы
    """
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
    """
    Тұрақ орнын брондау маршруты.
    
    Брондау деректерін POST сұранысы арқылы қабылдайды және брондауді сақтайды.
    """
    data = request.get_json()
    parking_id = data['parkingId']
    spot_index = data['spotIndex']
    duration = data['duration']

    expiration_time = time.time() + duration
    reservations[(parking_id, spot_index)] = expiration_time
    return jsonify({"success": True})

@app.route('/cancel_reservation', methods=['POST'])
def cancel_reservation():
    """
    Тұрақ орнынның брондауын болдырмау маршруты.
    
    Болдырмау деректерін POST сұранысы арқылы қабылдайды және брондауды жояды, егер ол бар болса.
    """
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
    """
    Барлық тұрақтардың тізімін алу маршруты.
    
    Барлық тұрақтардың ID мен мекенжайларын қайтарып береді.
    """
    parkings_list = [{'id': parking['id'], 'address': parking['address']} for parking in parkings['parkings']]
    return jsonify(parkings_list)

if __name__ == '__main__':
    manager = multiprocessing.Manager()
    parking_statuses = manager.dict()  # Процестер арасында тұрақ орындарының күйлерін сақтау үшін жалпы сөздік жасаймыз
    
    processes = []
    for parking in parkings['parkings']:
        # Әр тұрақ үшін жаңа процесті жасап, іске қосамыз
        p = multiprocessing.Process(target=process_parking, args=(parking, parking_statuses))
        p.start()
        processes.append(p)
    
    # Flask серверін 5000 портында іске қосамыз
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    
    # Барлық процестердің аяқталуын күтеміз
    for p in processes:
        p.join()

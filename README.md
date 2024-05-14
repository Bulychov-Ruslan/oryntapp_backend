# Тұрақ орындарын табу үшін "ORYNTAPP" мобильді қосымшасын әзірлеу

Бұл жоба "ORYNTAPP" мобильді қосымшасының серверлік бөлігі болып табылады. Бұл жоба тұрақ орындарының бос немесе бос емес екенін анықтауға арналған.
Камералардан алынған автотұрақ орындарын анализдеп орынның бос немес бос емес екенін анықтап қосымшаға API арқылы жіберіп отыру.
Жобаның қосымша бөлігі мына сілтемеде: [GitHub](https://github.com/Bulychov-Ruslan/oryntapp_app.git)

## Орнату нұсқаулар

1. **Репозиторийді клондау:**

    ```bash
    git clone https://github.com/Bulychov-Ruslan/oryntapp_backend.git
    ```

2. **Жоба каталогына өту:**

    ```bash
    cd oryntapp_backend
    ```

3. **Виртуалды ортаны жасау және іске қосу:**

    - **Windows үшін:**
    
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

    - **Linux/Mac үшін:**
    
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
      

4. **Тәуелділіктерді орнату:**

    ```bash
    pip install -r requirements.txt
    ```

## Жобаның іске қосылуы
    ```bash
    python main.py
    ```

## Жобадағы тестілеулерді іске асыру

1. **Модулді тестілеу:**
    ```bash
    python -m unittest tests/test_unit.py
    ```
2. **Системалық тістілеу:**
    ```bash
    pytest tests/test_system.py
    ```

# Автор: Булычов Руслан

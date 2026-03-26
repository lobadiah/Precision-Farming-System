# 🌾 Precision Farming System: MVP

Welcome to your Smart Farm! This project is an end-to-end IoT solution that uses sensors to monitor your crops and **Artificial Intelligence** to decide exactly when they need water or fertilizer.

---

## 🏗️ How it Works (The "Team")
This project is like a team of specialized workers, each running in its own container:

1.  **The Messenger (Mosquitto):** Receives data from your sensors (or simulations).
2.  **The Librarian (Ingestor):** Takes the sensor data and writes it into the books (Databases).
3.  **The Memory (InfluxDB & Postgres):** Stores your sensor history and AI decisions.
4.  **The Brain (ML Worker):** Every minute, it checks the history and decides if an alert is needed.
5.  **The Presentation (Grafana):** Draws beautiful graphs for you to see.
6.  **The Front Desk (Backend API):** Shows the AI's final decisions to you or a mobile app.

---

## 🚀 Step 1: How to Run the Project
Since this project uses **Docker**, you don't need to install Python or Databases manually. Everything is packaged together.

### Prerequisites:
-   Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) (and make sure it is running).

### Commands:
1.  Open **Command Prompt** (cmd) or PowerShell.
2.  Navigate to this folder:
    ```cmd
    cd "C:\Users\DELL\Desktop\personal projects\Farm precision system"
    ```
3.  Start the entire team:
    ```cmd
    docker-compose up -d --build
    ```

---

## 🧪 Step 2: How to Test the "Prototype"
Since you might not have sensors plugged in right now, we can **SIMULATE** them to see the system work.

### 1. Send Simulated Data (Acting as the Sensor)
Run this command in your terminal. It tells the system that "Zone_A" is getting very hot and dry:
```cmd
docker exec mosquitto mosquitto_pub -t "telemetry/1/Zone_A/sensor_01" -m "{\"battery\": 4.2, \"sensors\": {\"soil_moisture\": 22.0, \"temperature\": 31.0, \"humidity\": 40.0, \"nitrogen\": 60}}"
```

### 2. Watch the "Brain" Work (ML Worker)
The AI Brain scans the data every 60 seconds. You can watch it "thinking" by running:
```cmd
docker-compose logs -f ml_worker
```
*(You will see a message like: `Generated 2 recommendations for Zone_A`)*

### 3. See the Final Alert (The Results)
Click this link to see what the AI decided to do:
👉 [http://localhost:8000/api/v1/recommendations/Zone_A](http://localhost:8000/api/v1/recommendations/Zone_A)

### 4. Use the Simple Web Dashboard (Easiest Method)
Instead of looking at code, you can now use the beautiful dashboard we built:
- Simply open the **`index.html`** file in your browser.
- It will automatically fetch the latest alerts and show them with icons (💧 for Water, 🌱 for Fertilizer)!

---

## 📊 Step 3: Visualizing the Farm
You don't have to look at code to see your farm. We have a visual dashboard:
1.  Go to [http://localhost:3000](http://localhost:3000)
2.  **Login:** `admin` / `admin_password`
3.  Click **Dashboards** > **Farm Overview**.
4.  You will see your moisture, heat, and humidity trends live on the screen!

---

## 🧠 Step 4: Understanding the AI Logic
The AI follows a simple but powerful "Expert Rule" set:
- **IF** Soil Moisture is < 30% **AND** Temp is > 25°C → **ACTION:** Water the plants.
- **IF** Nitrogen is < 80 → **ACTION:** Apply Fertilizer.

As you collect more data over months, you can upgrade this to "Predictive AI" which can predict rain and save you money by *not* watering when rain is coming!

---

## 🛠️ Step 5: Real Hardware Integration (The Prototype)
When you are ready to move from simulation to real plants, you will need the following components.

### 🛒 Hardware Shopping List
| Component | Purpose | Approx. Cost |
| :--- | :--- | :--- |
| **ESP32 DevKit V1** | The "Micro-Controller" (Connects sensors to Wi-Fi) | $5 - $8 |
| **Capacitive Soil Moisture Sensor v1.2** | Measures water in the soil (Corrosion resistant) | $2 - $4 |
| **DHT22 Sensor** | Measures Air Temperature & Humidity | $3 - $5 |
| **NPK Soil Sensor (RS485)** | Measures Nitrogen, Phosphorus, Potassium | $20 - $30 |
| **RS485 to TTL Adapter** | Required to connect the NPK sensor to the ESP32 | $2 - $4 |
| **Jumper Wires & Breadboard** | For connecting everything together | $5 |

### 🔌 Basic Wiring Guide
1.  **Soil Moisture Sensor:**
    - VCC → ESP32 3.3V
    - GND → ESP32 GND
    - AUOUT → ESP32 Pin 34 (Analog Input)
2.  **DHT22 Sensor:**
    - VCC → ESP32 3.3V
    - GND → ESP32 GND
    - DATA → ESP32 Pin 4 (Digital Input)
3.  **Power:** Use a micro-USB cable to power the ESP32 from your computer or a 5V power adapter.

### 💻 Firmware (Code for ESP32)
You can use the **Arduino IDE** to program your ESP32. Your code should:
1.  Connect to your local Wi-Fi.
2.  Read the sensor values from the pins.
3.  Format the data into the **JSON** format shown in Step 2.
4.  Publish that JSON to the `mosquitto` broker running on your computer's IP address.

---

## 🗺️ Roadmap: Mobile App (Play Store)
To move from a computer-based system to a mobile app that a farmer can download:
1.  **Cloud Hosting:** Move this project from your computer to a cloud provider (like AWS or DigitalOcean) so it's accessible over the internet via a public IP or domain.
2.  **Flutter/React Native:** Build a simple app that connects to the **Backend API** (port 8000) we've already built.
3.  **Push Notifications:** Configure the **ML Worker** to send a "Firebase Cloud Message" (FCM) to the farmer's phone as soon as a watering recommendation is generated.

---

## 🔗 Quick Access Links
| Service | Link | Purpose |
| :--- | :--- | :--- |
| **Backend API** | [http://localhost:8000/docs](http://localhost:8000/docs) | Test the AI endpoints |
| **Grafana** | [http://localhost:3000](http://localhost:3000) | Visual Farm Dashboard |
| **InfluxDB** | [http://localhost:8086](http://localhost:8086) | View Raw Sensor Data |

---
*Created for the Farm Precision System Project.*
* by Obadiah Louis Adamu*


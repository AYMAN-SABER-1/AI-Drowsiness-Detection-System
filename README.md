# EYE ALERT - AI-Powered Driver Drowsiness Detection System

> *"The eye that never sleeps"*

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-478_Landmarks-00979D?style=for-the-badge)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![Raspberry Pi](https://img.shields.io/badge/Raspberry_Pi-4-C51A4A?style=for-the-badge&logo=raspberrypi&logoColor=white)
![ESP32](https://img.shields.io/badge/ESP32-Arduino_C++-E7352C?style=for-the-badge&logo=espressif&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)[cite: 1]

---

## 📌 Problem Statement

Driver drowsiness is one of the leading causes of road accidents worldwide, accounting for over 20% of fatal crashes. Drowsiness sets in gradually, leaving drivers unaware until it is too late, especially during night trips or long highway commutes.

| Statistic | Value |
| :--- | :--- |
| **Fatal accidents caused by drowsiness** | > 20% worldwide |
| **Most dangerous hours** | 2:00 AM – 6:00 AM |
| **Risk after 18h awake** | Equivalent to 0.05% BAC |
| **Drowsy driving admission** | 1 in 25 adult drivers |

---

## 💡 Solution Overview

**EYE ALERT** is an edge-computing, real-time embedded AI solution that continuously monitors the driver's state using computer vision. When fatigue or eye closure is detected, it instantly triggers visual (LED) and auditory (Buzzer) alerts. The system runs **100% offline**, ensuring zero latency and full operational privacy without requiring an internet connection.

### Key Features
* **Real-Time Processing:** 25–30 FPS with under 500ms detection latency.
* **Offline Operation:** No internet connection or cloud processing required.
* **Facial Landmark Mesh:** Uses MediaPipe Face Landmarker tracking 478 3D facial points.
* **Low-Light Capability:** Designed to operate under varying cabin lighting conditions.

---

## ⚙️ System Architecture

```mermaid
graph TD
    A[RPi Camera Module v2] -->|CSI Interface| B[Raspberry Pi 4 - Software Layer]
    B -->|Python 3.12 / MediaPipe / OpenCV| C{EAR < 0.21 for 15 frames?}
    C -->|Yes| D[Serial UART / 115200 Baud]
    D -->|USB Cable| E[ESP32 - Firmware Layer]
    E -->|GPIO 12| F[LED Warning Indicator]
    E -->|GPIO 13| G[Active Buzzer Alarm]


Architectural Layers

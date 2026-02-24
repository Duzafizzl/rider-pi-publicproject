#!/usr/bin/env python3
"""
rider_pi_control.py – Hardware abstraction for XGO Rider-Pi (xgorider). Extended for Rider Pi API.

Created: 2026-02-16
Last updated: 2026-02-24
Source: Rider-Pi Miore; extended for FastAPI/MCP (move, sensors, display, resonance, speak, …).
"""

"""
Rider Pi Control Wrapper – wrapper around xgolib XGO class.

This library provides a simple Robot class used by the FastAPI app and MCP server on the Pi.
"""

import time
from xgolib import XGO


class Robot:
    """Wrapper class for XGO Rider-Pi robot."""

    def __init__(self):
        """Initialize the robot."""
        self.car = XGO("xgorider")
        self.car.rider_reset()  # Reset to default stance

    # Max pitch/roll change that indicates a collision (degrees)
    IMU_CRASH_THRESHOLD_DEG = 15.0
    # How often to check IMU during movement (seconds)
    IMU_CHECK_INTERVAL = 0.1
    # Maximum safe duration per move command
    MAX_MOVE_DURATION = 5.0

    def _read_imu_safe(self):
        try:
            pitch = self.car.rider_read_imu_int16("pitch")
            roll = self.car.rider_read_imu_int16("roll")
            return float(pitch or 0), float(roll or 0)
        except Exception:
            return 0.0, 0.0

    def _move_with_imu_guard(self, go_fn, duration: float, speed: float):
        """Shared logic: start movement, poll IMU, auto-stop on collision."""
        duration = min(duration, self.MAX_MOVE_DURATION)
        speed_value = int(speed * 100)
        speed_value = max(-100, min(100, speed_value))
        pitch_start, roll_start = self._read_imu_safe()
        go_fn(speed_value)

        elapsed = 0.0
        while elapsed < duration:
            step = min(self.IMU_CHECK_INTERVAL, duration - elapsed)
            time.sleep(step)
            elapsed += step
            pitch_now, roll_now = self._read_imu_safe()
            dp = abs(pitch_now - pitch_start)
            dr = abs(roll_now - roll_start)
            if dp > self.IMU_CRASH_THRESHOLD_DEG or dr > self.IMU_CRASH_THRESHOLD_DEG:
                self.car.stop()
                return f"STOPPED: IMU crash detected (pitch_delta={dp:.1f}, roll_delta={dr:.1f}) after {elapsed:.1f}s"
        self.car.stop()
        return "OK"

    def move_forward(self, duration: float = 1.0, speed: float = 0.5):
        try:
            return self._move_with_imu_guard(self.car.forward, duration, speed)
        except Exception as e:
            return f"ERROR: {str(e)}"

    def move_backward(self, duration: float = 1.0, speed: float = 0.5):
        try:
            return self._move_with_imu_guard(self.car.back, duration, speed)
        except Exception as e:
            return f"ERROR: {str(e)}"

    def rotate(self, angle: float, speed: float = 0.5):
        try:
            angle = max(-180.0, min(180.0, angle))
            speed_value = int(speed * 100)
            speed_value = max(-100, min(100, speed_value))
            duration = abs(angle) / (50 * speed) if speed > 0 else 1.0
            duration = max(0.1, min(5.0, duration))
            if angle > 0:
                self.car.right(speed_value)
            else:
                self.car.left(speed_value)
            time.sleep(duration)
            self.car.stop()
            return "OK"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def stop(self):
        try:
            self.car.stop()
            return "OK"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def get_battery_level(self) -> int:
        """Battery level 0–100 %. Display often shows correct value; xgolib may differ."""
        try:
            raw = self.car.rider_read_battery()
            if raw is None:
                return -1
            # Raw value can be int 0–100, float (e.g. voltage 7.7), or other type
            if isinstance(raw, (list, tuple)):
                raw = raw[0] if raw else 0
            if isinstance(raw, float):
                # If voltage (e.g. 7.7 V for 2S LiPo): 6.0–8.4 V → 0–100 %
                if 5.0 <= raw <= 9.0:
                    pct = int((raw - 6.0) / (8.4 - 6.0) * 100) if raw >= 6.0 else 0
                    return max(0, min(100, pct))
                raw = int(round(raw))
            if isinstance(raw, str):
                raw = int(float(raw)) if raw else 0
            val = int(raw)
            # If value 0–100, use as-is; if small (e.g. 7 for 7.7 V), treat as tenth of volt → percent
            if 0 <= val <= 100:
                return val
            if 0 <= val <= 15:
                return val * 10  # e.g. 7 → 70 %, 8 → 80 %
            return max(0, min(100, val))
        except Exception as e:
            print(f"ERROR reading battery: {e}")
            return -1

    def get_battery_raw(self):
        """Raw value from rider_read_battery() – for debugging (display may show e.g. 77 %, API 2 %)."""
        try:
            return self.car.rider_read_battery()
        except Exception as e:
            print(f"ERROR reading battery raw: {e}")
            return None

    def get_attitude(self) -> dict:
        try:
            roll = self.car.rider_read_imu_int16("roll")
            pitch = self.car.rider_read_imu_int16("pitch")
            yaw = self.car.rider_read_imu_int16("yaw")
            return {
                "roll": float(roll) if roll else 0.0,
                "pitch": float(pitch) if pitch else 0.0,
                "yaw": float(yaw) if yaw else 0.0,
            }
        except Exception as e:
            print(f"ERROR reading attitude: {e}")
            return {"roll": 0.0, "pitch": 0.0, "yaw": 0.0}

    def set_expression(self, expression_id: int):
        try:
            expression_id = max(1, min(35, int(expression_id)))
            self.car.rider_action(expression_id)
            return "OK"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def set_rgb(self, red: int, green: int, blue: int):
        """Set all LEDs to one color. rider_led(index, (r,g,b)) – index 0 and 1."""
        try:
            red = max(0, min(255, int(red)))
            green = max(0, min(255, int(green)))
            blue = max(0, min(255, int(blue)))
            color = (red, green, blue)
            self.car.rider_led(0, color)
            self.car.rider_led(1, color)
            return "OK"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def execute_action(self, action_id: int):
        try:
            action_id = max(1, min(6, int(action_id)))
            self.car.action(action_id)
            return "OK"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def adjust_height(self, height: int):
        try:
            height = max(75, min(115, int(height)))
            self.car.rider_height(height)
            return "OK"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def adjust_roll(self, roll: int):
        try:
            roll = max(-17, min(17, int(roll)))
            self.car.rider_roll(roll)
            return "OK"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def set_balance_mode(self, enabled: bool):
        try:
            value = 1 if enabled else 0
            self.car.rider_balance_roll(value)
            return "OK"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def periodic_squat(self, period: float):
        try:
            period = max(0.0, min(4.0, float(period)))
            self.car.rider_periodic_z(period)
            return "OK"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def periodic_shake(self, period: float):
        try:
            period = max(0.0, min(4.0, float(period)))
            self.car.rider_periodic_roll(period)
            return "OK"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def reset(self):
        try:
            self.car.rider_reset()
            return "OK"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def show_expressions(
        self,
        duration_per_expression: float = 0.5,
        start_id: int = 1,
        end_id: int = 35,
    ):
        try:
            start_id = max(1, min(35, int(start_id)))
            end_id = max(1, min(35, int(end_id)))
            duration = max(0.1, min(5.0, float(duration_per_expression)))
            for expr_id in range(start_id, end_id + 1):
                self.set_expression(expr_id)
                time.sleep(duration)
            return f"OK: Expression show finished ({end_id - start_id + 1} expressions shown)"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def show_random_expressions(
        self, count: int = 10, duration_per_expression: float = 0.5
    ):
        try:
            import random

            count = max(1, min(50, int(count)))
            duration = max(0.1, min(5.0, float(duration_per_expression)))
            for _ in range(count):
                expr_id = random.randint(1, 35)
                self.set_expression(expr_id)
                time.sleep(duration)
            return f"OK: Random expression show finished ({count} expressions shown)"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def start_face_detection(self, duration: float = 0.0):
        """Start face detection (MediaPipe), show on display. See source for full implementation."""
        try:
            import cv2
            import mediapipe as mp
            from PIL import Image
            import xgoscreen.LCD_2inch as LCD_2inch

            display = LCD_2inch.LCD_2inch()
            display.clear()
            mp_face_detection = mp.solutions.face_detection
            mp_drawing = mp.solutions.drawing_utils
            cap = cv2.VideoCapture(0)
            cap.set(3, 320)
            cap.set(4, 240)
            face_detection = mp_face_detection.FaceDetection(
                model_selection=0, min_detection_confidence=0.5
            )
            start_time = time.time()
            frame_count = 0
            try:
                while cap.isOpened():
                    if duration > 0.0 and (time.time() - start_time) >= duration:
                        break
                    success, image = cap.read()
                    if not success:
                        continue
                    image.flags.writeable = False
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    results = face_detection.process(image_rgb)
                    image.flags.writeable = True
                    image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
                    if results.detections:
                        for detection in results.detections:
                            mp_drawing.draw_detection(image, detection)
                            frame_count += 1
                    b, g, r = cv2.split(image)
                    image_display = cv2.merge((r, g, b))
                    image_display = cv2.flip(image_display, 1)
                    imgok = Image.fromarray(image_display)
                    display.ShowImage(imgok)
                    if cv2.waitKey(5) & 0xFF == 27:
                        break
            finally:
                cap.release()
                face_detection.close()
                cv2.destroyAllWindows()
            return f"OK: Face detection finished. {frame_count} frames with faces processed."
        except ImportError as e:
            return f"ERROR: Missing library: {str(e)}"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def list_available_voices(self) -> dict:
        """List available TTS voices (Azure, espeak, pyttsx3). See source for full implementation."""
        return {
            "azure_speech": {"de-DE": ["de-DE-KatjaNeural"], "en-US": ["en-US-JennyNeural"]},
            "espeak": [],
            "pyttsx3": [],
        }

    def speak(self, text: str, language: str = "de-DE", voice: str = None) -> str:
        """TTS: Azure > espeak > pyttsx3. See Rider-Pi Miore for full implementation."""
        try:
            import os

            speech_key = os.getenv("AZURE_SPEECH_KEY", "")
            if speech_key:
                try:
                    import azure.cognitiveservices.speech as speechsdk

                    speech_region = os.getenv("AZURE_SPEECH_REGION", "westeurope")
                    speech_config = speechsdk.SpeechConfig(
                        subscription=speech_key, region=speech_region
                    )
                    voice_name = voice or (
                        "de-DE-KatjaNeural" if language.startswith("de") else "en-US-JennyNeural"
                    )
                    speech_config.speech_synthesis_voice_name = voice_name
                    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
                    result = synthesizer.speak_text_async(text).get()
                    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                        return "OK: Text spoken (Azure)"
                    return f"ERROR: Azure TTS: {result.reason}"
                except Exception:
                    pass
            try:
                import subprocess

                subprocess.run(
                    ["espeak", "-v", "de+f2" if language.startswith("de") else "en", text],
                    check=True,
                    timeout=30,
                )
                return "OK: Text spoken (espeak)"
            except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
                pass
            return "ERROR: No TTS available. Configure Azure or espeak."
        except Exception as e:
            return f"ERROR: {str(e)}"

    def demo_german_voices(
        self, delay_between_voices: float = 2.0, male_only: bool = False
    ) -> str:
        """Demo of German Azure voices. See source for full implementation."""
        return self.speak("Hello, I am a demo voice.", language="de-DE")


import tkinter as tk
from tkinter import ttk
import requests
from PIL import Image, ImageTk
from io import BytesIO
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import threading

# ---------------- CONFIGURATION ----------------
API_KEY = "58f3709de044d9985194a0bfce7dcd96"

CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
IP_URL = "https://ipinfo.io/json"

# ---------------- MAIN APPLICATION ----------------
class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Forecast App")
        self.root.geometry("760x700")
        self.root.configure(bg="#eaf4ff")

        self.unit = "C"
        self.current_data = None
        self.forecast_data = None
        self.icon_images = []

        title = tk.Label(
            root, text="Weather Forecast App",
            font=("Arial", 23, "bold"),
            bg="#eaf4ff", fg="#174a7e"
        )
        title.pack(pady=15)

        # Search section
        search_frame = tk.Frame(root, bg="#eaf4ff")
        search_frame.pack(pady=10)

        self.city_entry = tk.Entry(
            search_frame, font=("Arial", 14), width=25
        )
        self.city_entry.grid(row=0, column=0, padx=5)
        self.city_entry.bind(
            "<Return>", lambda event: self.get_weather()
        )

        tk.Button(
            search_frame, text="Get Weather",
            command=self.get_weather,
            bg="#1976d2", fg="white",
            font=("Arial", 11)
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            search_frame, text="My Location",
            command=self.detect_location,
            bg="#00897b", fg="white",
            font=("Arial", 11)
        ).grid(row=0, column=2, padx=5)

        self.unit_button = tk.Button(
            root, text="Switch to °F",
            command=self.toggle_unit,
            bg="#ffb74d", font=("Arial", 11)
        )
        self.unit_button.pack(pady=8)

        self.status = tk.Label(
            root, text="Enter a city or ZIP code.",
            bg="#eaf4ff", fg="#444444",
            font=("Arial", 11)
        )
        self.status.pack(pady=5)

        # Current weather panel
        current_frame = tk.LabelFrame(
            root, text="Current Weather",
            font=("Arial", 13, "bold"),
            bg="white", padx=15, pady=10
        )
        current_frame.pack(fill="x", padx=25, pady=10)

        self.icon_label = tk.Label(current_frame, bg="white")
        self.icon_label.pack()

        self.weather_label = tk.Label(
            current_frame, text="No weather data yet",
            font=("Arial", 13), bg="white",
            justify="center"
        )
        self.weather_label.pack()

        # Forecast notebook
        notebook = ttk.Notebook(root)
        notebook.pack(
            fill="both", expand=True,
            padx=25, pady=10
        )

        hourly_tab = tk.Frame(notebook, bg="white")
        daily_tab = tk.Frame(notebook, bg="white")

        notebook.add(hourly_tab, text="Upcoming Forecast")
        notebook.add(daily_tab, text="5-Day Forecast")

        self.hourly_text = tk.Text(
            hourly_tab, font=("Arial", 11),
            wrap="word", height=12
        )
        self.hourly_text.pack(fill="both", expand=True)

        self.daily_text = tk.Text(
            daily_tab, font=("Arial", 11),
            wrap="word", height=12
        )
        self.daily_text.pack(fill="both", expand=True)

        self.hourly_text.config(state="disabled")
        self.daily_text.config(state="disabled")

        tk.Button(
                search_frame,
                text="Refresh",
                command=self.refresh_weather,
                bg="#4CAF50",
                fg="white",
                font=("Arial", 11)
            ).grid(row=0, column=3, padx=5)

    # ---------------- API REQUEST ----------------
    def api_request(self, url, params=None):
        try:
            response = requests.get(
                url, params=params, timeout=10
            )

            if response.status_code == 401:
                raise ValueError(
                    "Invalid API key. Check your OpenWeatherMap key."
                )

            if response.status_code == 404:
                raise ValueError(
                    "City or ZIP code not found."
                )

            if response.status_code == 429:
                raise ValueError(
                    "API request limit reached. Try again later."
                )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            raise ValueError(
                "Network timeout. Please try again."
            )
        except requests.exceptions.RequestException as e:
            raise ValueError(
                "Network or API error: " + str(e)
            )
        except requests.exceptions.JSONDecodeError:
            raise ValueError("Invalid response from weather API.")

    # ---------------- WEATHER SEARCH ----------------
    def get_weather(self):
        city = self.city_entry.get().strip()

        if not city:
            self.show_error("Please enter a city or ZIP code.")
            return

        if API_KEY == "YOUR_API_KEY_HERE":
            self.show_error("Please configure your API key first.")
            return

        self.status.config(
            text="Loading weather data...", fg="blue"
        )

        threading.Thread(
            target=self.fetch_weather,
            args=(city,), daemon=True
        ).start()

    def fetch_weather(self, city):
        try:
            # ZIP codes may use ZIP,country format
            if city.split(",")[0].strip().isdigit():
                search_param = {"zip": city}
            else:
                search_param = {"q": city}

            params = {
                **search_param,
                "appid": API_KEY,
                "units": "metric"
            }

            current = self.api_request(CURRENT_URL, params)

            # Use coordinates for accurate forecast
            forecast = self.api_request(
                FORECAST_URL,
                {
                    "lat": current["coord"]["lat"],
                    "lon": current["coord"]["lon"],
                    "appid": API_KEY,
                    "units": "metric"
                }
            )

            icon_code = current["weather"][0]["icon"]
            icon_image = None

            try:
                icon_url = (
                    "https://openweathermap.org/img/wn/"
                    + icon_code + "@2x.png"
                )
                response = requests.get(icon_url, timeout=5)
                response.raise_for_status()
                icon_image = Image.open(
                    BytesIO(response.content)
                ).convert("RGBA")
            except (requests.RequestException, OSError):
                pass

            self.root.after(
                0,
                lambda: self.update_weather(
                    current, forecast, icon_image
                )
            )

        except (ValueError, KeyError, TypeError) as e:
            message = str(e)
            self.root.after(
                0, lambda: self.show_error(message)
            )

    # ---------------- DISPLAY WEATHER ----------------
    def update_weather(self, current, forecast, icon_image):
        self.current_data = current
        self.forecast_data = forecast

        if icon_image:
            photo = ImageTk.PhotoImage(icon_image)
            self.icon_label.config(image=photo)
            self.icon_label.image = photo
        else:
            self.icon_label.config(image="")
            self.icon_label.image = None

        self.status.config(
            text="Weather updated successfully!",
            fg="green"
        )

        self.display_results()

    def refresh_weather(self):
        city = self.city_entry.get().strip()

        if not city:
            self.show_error("Please enter a city to refresh weather.")
            return

        self.status.config(
            text="Refreshing weather data...",
            fg="blue"
        )

        self.get_weather()
    def convert_temp(self, celsius):
        if self.unit == "F":
            return celsius * 9 / 5 + 32
        return celsius

    def display_results(self):
        if not self.current_data:
            return

        data = self.current_data
        symbol = "°C" if self.unit == "C" else "°F"

        temp_c = data["main"]["temp"]
        temp_f = temp_c * 9 / 5 + 32

        description = data["weather"][0]["description"].title()
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]

        if self.unit == "C":
            primary = temp_c
            secondary = temp_f
            other_symbol = "°F"
        else:
            primary = temp_f
            secondary = temp_c
            other_symbol = "°C"

        weather_info = (
            f"Location: {data['name']}, {data['sys']['country']}\n"
            f"Temperature: {primary:.1f}{symbol} "
            f"({secondary:.1f}{other_symbol})\n"
            f"Condition: {description}\n"
            f"Humidity: {humidity}%\n"
            f"Wind Speed: {wind:.1f} m/s"
        )

        self.weather_label.config(text=weather_info)
        self.show_forecast()

    # ---------------- FORECAST ----------------
    def show_forecast(self):
        data = self.forecast_data
        if not data:
            return

        symbol = "°C" if self.unit == "C" else "°F"
        timezone_offset = data["city"]["timezone"]
        local_tz = timezone(timedelta(seconds=timezone_offset))

        # Next 6 available 3-hour forecast periods
        hourly_output = (
            "Next 6 Forecast Periods (3-hour intervals)\n\n"
        )

        for item in data["list"][:6]:
            date_time = datetime.fromtimestamp(
                item["dt"], local_tz
            )
            temp = self.convert_temp(item["main"]["temp"])
            condition = item["weather"][0]["description"].title()

            hourly_output += (
                f"{date_time.strftime('%d %b, %I:%M %p')}\n"
                f"Temperature: {temp:.1f}{symbol}\n"
                f"Condition: {condition}\n"
                f"Humidity: {item['main']['humidity']}%\n"
                f"Wind: {item['wind']['speed']:.1f} m/s\n"
                "-------------------------------------\n"
            )

        self.set_text(self.hourly_text, hourly_output)

        # Group forecast by local calendar date
        grouped = defaultdict(list)

        for item in data["list"]:
            local_date = datetime.fromtimestamp(
                item["dt"], local_tz
            ).date()
            grouped[local_date].append(item)

        today = datetime.fromtimestamp(
            self.current_data["dt"], local_tz
        ).date()

        daily_output = "5-Day Weather Forecast\n\n"
        future_days = [
            day for day in sorted(grouped)
            if day > today
        ][:5]

        for day in future_days:
            entries = grouped[day]

            temps = [
                entry["main"]["temp"]
                for entry in entries
            ]

            min_temp = self.convert_temp(min(temps))
            max_temp = self.convert_temp(max(temps))

            # Condition closest to noon
            representative = min(
                entries,
                key=lambda entry: abs(
                    datetime.fromtimestamp(
                        entry["dt"], local_tz
                    ).hour - 12
                )
            )

            condition = representative[
                "weather"
            ][0]["description"].title()

            daily_output += (
                f"{day.strftime('%A, %d %B')}\n"
                f"Min: {min_temp:.1f}{symbol} | "
                f"Max: {max_temp:.1f}{symbol}\n"
                f"Condition: {condition}\n"
                "-------------------------------------\n"
            )

        daily_output += (
            "\nNote: Min/max are from available "
            "3-hour samples, not official daily extremes."
        )

        self.set_text(self.daily_text, daily_output)

    def set_text(self, widget, content):
        widget.config(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, content)
        widget.config(state="disabled")

    # ---------------- UNIT TOGGLE ----------------
    def toggle_unit(self):
        self.unit = "F" if self.unit == "C" else "C"

        self.unit_button.config(
            text="Switch to °C"
            if self.unit == "F" else "Switch to °F"
        )

        self.display_results()

    # ---------------- IP LOCATION ----------------
    def detect_location(self):
        self.status.config(
            text="Detecting approximate location...",
            fg="blue"
        )

        threading.Thread(
            target=self.fetch_location,
            daemon=True
        ).start()

    def fetch_location(self):
        try:
            data = self.api_request(IP_URL)
            city = data.get("city")

            if not city:
                raise ValueError(
                    "Unable to detect your city."
                )

            self.root.after(
                0, lambda: self.use_detected_city(city)
            )

        except ValueError as e:
            message = str(e)
            self.root.after(
                0, lambda: self.show_error(message)
            )

    def use_detected_city(self, city):
        self.city_entry.delete(0, tk.END)
        self.city_entry.insert(0, city)
        self.get_weather()

    # ---------------- ERROR HANDLING ----------------
    def show_error(self, message):
        self.status.config(
            text=message, fg="red",
            wraplength=650
        )


# ---------------- RUN APPLICATION ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()

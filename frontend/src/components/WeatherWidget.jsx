

import { useEffect, useState } from "react";

function WeatherWidget() {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchWeather();
  }, []);

  async function fetchWeather() {
    setError("");
    setLoading(true);
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;

        const response = await fetch(`http://127.0.0.1:8000/external/weather?lat=${lat}&lon=${lon}`);
        if (!response.ok) {
            throw new Error("Failed to fetch weather data");
        }
        const data = await response.json();
        setWeather(data);
        setLoading(false);
      },
      (error) => {
        console.error("Error getting geolocation:", error);
        setError("Unable to retrieve your location for weather data.");
        setLoading(false);
      }
    );
  }

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Weather</h2>

      {loading && <p>Loading weather...</p>}

      {error && <p style={styles.error}>{error}</p>}

      {weather && !loading && !error && (
        <div>
          <p style={styles.city}>{weather.city}</p>

          <p style={styles.temperature}>{weather.temperature}°C</p>

          <p style={styles.description}>{weather.weather}</p>

          <p style={styles.detail}>Humidity: {weather.humidity}%</p>
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
  backgroundColor: "#ffffff",
  padding: "16px",
  borderRadius: "14px",
  boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
  width: "260px",
  height: "170px",
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  alignItems: "center",
},

title: {
  margin: "0 0 14px 0",
  fontSize: "28px",
  textAlign: "center",
  color: "#555",
},

city: {
  fontSize: "18px",
  fontWeight: "bold",
  margin: "0 0 4px 0",
  textAlign: "center",
  color : "#555",
},

temperature: {
  fontSize: "36px",
  fontWeight: "bold",
  margin: "0",
  textAlign: "center",
  color : "#222",
},

description: {
  margin: "4px 0",
  textTransform: "capitalize",
  textAlign: "center",
  color : "#555",
},

detail: {
  margin: "0",
  color: "#555",
  textAlign: "center",
},

  error: {
    color: "red"
  }
};

export default WeatherWidget;
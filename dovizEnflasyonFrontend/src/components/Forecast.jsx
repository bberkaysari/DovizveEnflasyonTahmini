import React, { useState, useRef } from "react";
import axios from "axios";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const Forecast = () => {
  const [forecastType, setForecastType] = useState("currency");
  const [currency, setCurrency] = useState("USD");
  const [frequency, setFrequency] = useState("1");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showGraph, setShowGraph] = useState(false);

  const forecastCache = useRef({});

  const resetLayout = () => {
    setForecast(null);
    setShowGraph(false);
  };

  const fetchForecast = async () => {
    setLoading(true);
    setShowGraph(true);

    const cacheKey = forecastType === "currency"
      ? `${forecastType}-${currency}-${frequency}-${startDate}-${endDate}`
      : "inflation";

    if (forecastCache.current[cacheKey]) {
      setForecast(forecastCache.current[cacheKey]);
      setLoading(false);
      return;
    }

    try {
      const url = forecastType === "currency"
        ? "http://127.0.0.1:5000/forecast_static"
        : "http://127.0.0.1:5000/inflation_static";

      const response = await axios.get(url);
      forecastCache.current[cacheKey] = response.data;
      setForecast(response.data);
    } catch (error) {
      console.error("Tahmin alınırken bir hata oluştu:", error);
    }

    setLoading(false);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return null;
    const d = new Date(dateStr);
    return d.toISOString().split("T")[0];
  };

  const formattedStart = formatDate(startDate);
  const formattedEnd = formatDate(endDate);

  let labels = [], datasets = [];

  if (forecastType === "currency") {
    const realData = (forecast?.forecasts?.[currency]?.real || []).filter(d =>
      (!formattedStart || d.date >= formattedStart) && (!formattedEnd || d.date <= formattedEnd)
    );
    const forecastData = (forecast?.forecasts?.[currency]?.forecast || []).filter(d =>
      (!formattedStart || d.date >= formattedStart) && (!formattedEnd || d.date <= formattedEnd)
    );

    labels = [...realData.map(d => d.date), ...forecastData.map(d => d.date)];

    const actualValues = [...realData.map(d => d.actual), ...Array(forecastData.length).fill(null)];
    const predictionValues = [...Array(realData.length).fill(null), ...forecastData.map(d => d.prediction)];
    const confLowValues = [...Array(realData.length).fill(null), ...forecastData.map(d => d.conf_low)];
    const confHighValues = [...Array(realData.length).fill(null), ...forecastData.map(d => d.conf_high)];

    datasets = [
      {
        label: "Gerçek Kur",
        data: actualValues,
        borderColor: "#3b82f6",
        backgroundColor: "rgba(59, 130, 246, 0.1)",
        tension: 0.4,
      },
      {
        label: `Tahmin (${currency})`,
        data: predictionValues,
        borderColor: "#10b981",
        backgroundColor: "rgba(16, 185, 129, 0.1)",
        tension: 0.4,
      },
      {
        label: "Alt Güven Aralığı",
        data: confLowValues,
        borderColor: "#f43f5e",
        borderDash: [5, 5],
        fill: false,
      },
      {
        label: "Üst Güven Aralığı",
        data: confHighValues,
        borderColor: "#22c55e",
        borderDash: [5, 5],
        fill: false,
      },
    ];
  } else if (forecastType === "inflation") {
    const inflReal = forecast?.forecasts?.["TÜFE"]?.real || [];
    const inflForecast = forecast?.forecasts?.["TÜFE"]?.forecast || [];
  
    // Enflasyon oranlarını hesapla (yıllık yüzde değişim)
    const realRates = inflReal
      .map((d, i) => {
        if (i < 12) return null; // 12 ay öncesi yoksa oran hesaplanmaz
        const prev = inflReal[i - 12];
        const rate = ((d.actual - prev.actual) / prev.actual) * 100;
        return {
          date: d.date,
          value: +rate.toFixed(2),
        };
      })
      .filter(Boolean); // null'ları temizle
  
      const lastReal = inflReal[inflReal.length - 12]; // 12 ay öncesi veri

      const forecastRates = inflForecast.map((d) => {
        const rate = ((d.prediction - lastReal.actual) / lastReal.actual) * 100;
        const confLowRate = ((d.conf_low - lastReal.actual) / lastReal.actual) * 100;
        const confHighRate = ((d.conf_high - lastReal.actual) / lastReal.actual) * 100;
      
        return {
          date: d.date,
          prediction: +rate.toFixed(2),
          conf_low: +confLowRate.toFixed(2),
          conf_high: +confHighRate.toFixed(2),
        };
      });
  
    labels = [...realRates.map(d => d.date), ...forecastRates.map(d => d.date)];
  
    const actualValues = [...realRates.map(d => d.value), ...Array(forecastRates.length).fill(null)];
    const predictionValues = [...Array(realRates.length).fill(null), ...forecastRates.map(d => d.prediction)];
    const confLowValues = [...Array(realRates.length).fill(null), ...forecastRates.map(d => d.conf_low)];
    const confHighValues = [...Array(realRates.length).fill(null), ...forecastRates.map(d => d.conf_high)];
  
    datasets = [
      {
        label: "Yıllık Enflasyon Oranı (%)",
        data: actualValues,
        borderColor: "#f59e0b",
        backgroundColor: "rgba(245, 158, 11, 0.2)",
        tension: 0.4,
      },
      {
        label: "Tahmin Oranı",
        data: predictionValues,
        borderColor: "#22c55e",
        backgroundColor: "rgba(34, 197, 94, 0.2)",
        tension: 0.4,
      },
      {
        label: "Alt Güven Aralığı",
        data: confLowValues,
        borderColor: "#f43f5e",
        borderDash: [5, 5],
        fill: false,
      },
      {
        label: "Üst Güven Aralığı",
        data: confHighValues,
        borderColor: "#0ea5e9",
        borderDash: [5, 5],
        fill: false,
      },
    ];
  }

  const chartData = { labels, datasets };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
        labels: {
          color: "#f1f5f9",
        },
      },
      title: {
        display: true,
        text: forecastType === "currency"
          ? `${currency} İçin Döviz Tahmini`
          : "Enflasyon Tahmini",
        color: "#f1f5f9",
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: "#94a3b8" },
      },
      y: {
        grid: { display: true, color: "#475569" },
        ticks: { color: "#94a3b8" },
      },
    },
  };

  return (
    <div className="p-12 bg-slate-900 text-slate-100 flex h-screen items-center justify-center transition-all duration-500 ease-in-out">
      <div className={`transition-all duration-700 ease-in-out flex ${showGraph ? "w-full" : "w-full flex-col items-center"}`}>
        <div className={`transition-all duration-700 ease-in-out ${showGraph ? "w-1/4 bg-slate-800" : "w-full max-w-lg bg-transparent"} rounded-lg p-6 shadow-md`}>
          <h1 className="text-2xl font-bold text-emerald-500 mb-6">
            Tahmin <span className="text-slate-100">Seçenekleri</span>
          </h1>
          <div className="grid grid-cols-1 gap-6">
            <div>
              <label className="block text-slate-400 font-medium mb-2">Tahmin Türü</label>
              <select
                value={forecastType}
                onChange={(e) => {
                  setForecastType(e.target.value);
                  resetLayout();
                }}
                className="w-full p-2 bg-slate-700 text-slate-100 border border-slate-600 rounded-md"
              >
                <option value="currency">Döviz</option>
                <option value="inflation">Enflasyon</option>
              </select>
            </div>

            {forecastType === "currency" && (
              <>
                <div>
                  <label className="block text-slate-400 font-medium mb-2">Döviz</label>
                  <select
                    value={currency}
                    onChange={(e) => {
                      setCurrency(e.target.value);
                      resetLayout();
                    }}
                    className="w-full p-2 bg-slate-700 text-slate-100 border border-slate-600 rounded-md"
                  >
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 font-medium mb-2">Frekans</label>
                  <select
                    value={frequency}
                    onChange={(e) => {
                      setFrequency(e.target.value);
                      resetLayout();
                    }}
                    className="w-full p-2 bg-slate-700 text-slate-100 border border-slate-600 rounded-md"
                  >
                    <option value="1">Günlük</option>
                    <option value="0">Aylık</option>
                  </select>
                </div>

                {frequency === "1" && (
                  <>
                    <div>
                      <label className="block text-slate-400 font-medium mb-2">Başlangıç Tarihi</label>
                      <input
                        type="date"
                        value={startDate}
                        onChange={(e) => setStartDate(e.target.value)}
                        className="w-full p-2 bg-slate-700 text-slate-100 border border-slate-600 rounded-md"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-400 font-medium mb-2">Bitiş Tarihi</label>
                      <input
                        type="date"
                        value={endDate}
                        onChange={(e) => setEndDate(e.target.value)}
                        className="w-full p-2 bg-slate-700 text-slate-100 border border-slate-600 rounded-md"
                      />
                    </div>
                  </>
                )}
              </>
            )}
          </div>
          <button
            onClick={fetchForecast}
            className="w-full bg-emerald-700 text-white py-2 px-4 rounded-md hover:bg-emerald-600 mt-4"
          >
            Tahmini Al
          </button>
        </div>

        {showGraph && (
          <div className="flex-1 bg-slate-800 rounded-lg p-6 ml-4">
            {loading ? (
              <div className="flex flex-col items-center justify-center h-full">
                <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-green-500 border-opacity-75 mb-4"></div>
                <p className="text-lg text-green-400 font-medium">
                  Modelimiz geleceği görüyor, lütfen bekleyin...
                </p>
              </div>
            ) : (
              <div>
                <h1 className="text-2xl font-bold text-emerald-500 mb-6">Tahmin <span className="text-slate-100">Grafiği</span></h1>
                <Line data={chartData} options={chartOptions} />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Forecast;
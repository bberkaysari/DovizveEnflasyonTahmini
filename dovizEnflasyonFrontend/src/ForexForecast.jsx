import React, { useState } from "react";
import axios from "axios";
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
import { Line } from "react-chartjs-2";
import { motion } from "framer-motion";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const ForexForecast = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const getForecast = async () => {
    setLoading(true);
    try {
      const response = await axios.get("http://127.0.0.1:5000/forecast_static");
      setData(response.data);
    } catch (error) {
      console.error("Tahmin alınırken bir hata oluştu:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center py-10">
      <motion.h1
        className="text-4xl font-bold mb-6 text-blue-600"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
      >
        Döviz Kuru Tahmini
      </motion.h1>
      <motion.button
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded mb-10 shadow-lg"
        onClick={getForecast}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
      >
        Tahmini Al
      </motion.button>
      {loading && <p className="text-lg font-medium text-gray-500">Yükleniyor...</p>}
      {data && (
        <motion.div
          className="w-3/4 bg-white rounded-lg shadow-md p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="text-2xl font-semibold text-gray-700 mb-4">USD/TRY ve EUR/TRY Tahminleri</h2>
          <Line
            data={{
              labels: [...data.real_2024.dates, ...data.future_dates],
              datasets: [
                {
                  label: "USD/TRY (Tahmin)",
                  data: [
                    ...Array(data.real_2024.dates.length).fill(null),
                    ...data.future_usd,
                  ],
                  borderColor: "rgb(59, 130, 246)",
                  backgroundColor: "rgba(59, 130, 246, 0.2)",
                  fill: true,
                  tension: 0.4,
                },
                {
                  label: "EUR/TRY (Tahmin)",
                  data: [
                    ...Array(data.real_2024.dates.length).fill(null),
                    ...data.future_eur,
                  ],
                  borderColor: "rgb(234, 88, 12)",
                  backgroundColor: "rgba(234, 88, 12, 0.2)",
                  fill: true,
                  tension: 0.4,
                },
                {
                  label: "USD/TRY (Gerçek 2024)",
                  data: data.real_2024.usd,
                  borderColor: "rgb(16, 185, 129)",
                  backgroundColor: "rgba(16, 185, 129, 0.2)",
                  fill: true,
                  tension: 0.4,
                },
                {
                  label: "EUR/TRY (Gerçek 2024)",
                  data: data.real_2024.eur,
                  borderColor: "rgb(239, 68, 68)",
                  backgroundColor: "rgba(239, 68, 68, 0.2)",
                  fill: true,
                  tension: 0.4,
                },
              ],
            }}
            options={{
              responsive: true,
              plugins: {
                legend: {
                  position: "top",
                },
                title: {
                  display: true,
                  text: "USD/TRY ve EUR/TRY Tahmin ve Gerçek Değerleri",
                },
              },
            }}
          />
        </motion.div>
      )}
    </div>
  );
};

export default ForexForecast;

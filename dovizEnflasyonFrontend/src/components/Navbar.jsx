import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import "remixicon/fonts/remixicon.css";

const Navbar = () => {
  const [usdRate, setUsdRate] = useState(null);
  const [eurRate, setEurRate] = useState(null);
  const [dateTime, setDateTime] = useState("");

  // Kur verilerini backend'den (statik json) çek
  useEffect(() => {
    const fetchRates = async () => {
      try {
        const res = await fetch("http://localhost:5001/kur");
        const data = await res.json();
        setUsdRate(data.USD);
        setEurRate(data.EUR);
      } catch (error) {
        console.error("Kur verileri alınamadı:", error);
      }
    };
    fetchRates();
  }, []);

  // Canlı tarih ve saat
  useEffect(() => {
    const updateDateTime = () => {
      const now = new Date();
      const formatted = now.toLocaleString("tr-TR", {
        dateStyle: "short",
        timeStyle: "medium",
      });
      setDateTime(formatted);
    };

    updateDateTime();
    const interval = setInterval(updateDateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <nav className="bg-slate-900 border-b border-emerald-600 shadow-md">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        {/* Logo */}
        <h1 className="text-2xl font-extrabold text-emerald-500">
          <i className="ri-arrow-right-up-line"></i>Tahmincin
          <i className="text-red-500 ri-arrow-right-down-line"></i>
        </h1>

        {/* Kur verileri ve saat */}
        <div className="text-slate-100 text-sm flex items-center space-x-6 mr-6">
          {usdRate && eurRate ? (
            <>
              <div className="flex space-x-4">
                <span>USD: {usdRate} ₺</span>
                <span>EUR: {eurRate} ₺</span>
              </div>
              <span className="text-xs italic text-slate-400">{dateTime}</span>
            </>
          ) : (
            <span>Kur verileri alınıyor...</span>
          )}
        </div>

        {/* Navigasyon */}
        <div className="flex space-x-6">
          <Link
            to="/"
            className="text-slate-200 hover:text-emerald-500 transition-all duration-300 font-medium text-lg"
          >
            Ana Sayfa
          </Link>
          <Link
            to="/forecast"
            className="text-slate-200 hover:text-emerald-500 transition-all duration-300 font-medium text-lg"
          >
            Tahmin
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
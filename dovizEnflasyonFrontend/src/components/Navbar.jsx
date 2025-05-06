import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import "remixicon/fonts/remixicon.css";

const Navbar = () => {
  const [usdRate, setUsdRate] = useState(null);
  const [eurRate, setEurRate] = useState(null);
  const [updatedAt, setUpdatedAt] = useState("");
  const [dateTime, setDateTime] = useState("");

  useEffect(() => {
    const fetchRates = async () => {
      try {
        const res = await fetch("http://localhost:5000/kur");
        const data = await res.json();
        setUsdRate(data.USD);
        setEurRate(data.EUR);
        setUpdatedAt(data.updated_at);
      } catch (error) {
        console.error("Kur verileri alınamadı:", error);
      }
    };
    fetchRates();
  }, []);

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

        {/* Sol: Logo */}
        <div className="text-emerald-500 font-extrabold text-2xl flex-shrink-0">
          <i className="ri-arrow-right-up-line"></i>Tahmincin
          <i className="text-red-500 ri-arrow-right-down-line"></i>
        </div>

        {/* Orta: Kur ve güncelleme */}
        <div className="text-center text-slate-100 text-sm">
          {usdRate && eurRate ? (
            <>
              <div className="space-x-6">
                <span>$: {usdRate} ₺</span>
                <span>€: {eurRate} ₺</span>
              </div>
              <div className="text-xs italic text-slate-400 mt-1">
                Son Güncelleme: {updatedAt}
              </div>
            </>
          ) : (
            <span>Kur verileri alınıyor...</span>
          )}
        </div>

        {/* Sağ: Saat + Navigasyon */}
        <div className="flex items-center space-x-6 text-slate-100">
          <span className="text-xs italic text-slate-400">{dateTime}</span>
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
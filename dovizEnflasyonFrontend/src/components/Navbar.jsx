import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import "remixicon/fonts/remixicon.css";

const Navbar = () => {
  const [usdRate, setUsdRate] = useState(null);
  const [eurRate, setEurRate] = useState(null);

  useEffect(() => {
    const fetchRates = async () => {
      try {
        const res = await fetch("https://api.frankfurter.app/latest?from=TRY&to=USD,EUR");
        const data = await res.json();
        setUsdRate((1 / data.rates.USD).toFixed(2));
        setEurRate((1 / data.rates.EUR).toFixed(2));
      } catch (error) {
        console.error("Kur verileri alınamadı:", error);
      }
    };
    fetchRates();
  }, []);

  return (
    <nav className="bg-slate-900 border-b border-emerald-600 shadow-md">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        {/* Logo */}
        <h1 className="text-2xl font-extrabold text-emerald-500">
          <i className="ri-arrow-right-up-line"></i>Tahmincin<i className="text-red-500 ri-arrow-right-down-line"></i>
        </h1>

        {/* Exchange Rates */}
        <div className="text-slate-100 text-sm flex flex-col items-end mr-6">
          {usdRate && eurRate ? (
            <>
              <span>USD: {usdRate} ₺</span>
              <span>EUR: {eurRate} ₺</span>
            </>
          ) : (
            <span>Kur verileri alınıyor...</span>
          )}
        </div>

        {/* Navigation Links */}
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

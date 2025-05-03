import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import "remixicon/fonts/remixicon.css";
import Footer from "./Footer";

const HomePage = () => {
  const [typedText, setTypedText] = useState(""); // Yazılan metin
  const fullText = "  Tahmincin: Finansal Tahmin Uygulaması";

  useEffect(() => {
    let index = 0;
    const typeInterval = setInterval(() => {
      if (index < fullText.length-1) {
        setTypedText((prev) => prev + fullText[index]);
        index++;
      } else {
        clearInterval(typeInterval); // Tüm harfler eklendiğinde durdur
      }
    }, 100); // Harf ekleme hızı (milisaniye)
    return () => clearInterval(typeInterval); // Temizlik
  }, []);

  const cards = [
    {
      icon: "ri-line-chart-line",
      title: "Döviz Tahminleri",
      description: "USD ve EUR için günlük ve aylık tahminler alın, geleceği daha net görün.",
    },
    {
      icon: "ri-money-cny-box-line",
      title: "Enflasyon Analizleri",
      description: "Gelecekteki enflasyon oranlarını tahmin ederek yatırım stratejilerinizi oluşturun.",
    },
    {
      icon: "ri-layout-3-line",
      title: "Kullanıcı Dostu Arayüz",
      description: "Şık ve modern tasarımımızla kolayca tahmin alın ve analiz edin.",
    },
    {
      icon: "ri-dashboard-line",
      title: "Detaylı Grafikler",
      description: "Tüm analizleriniz için gelişmiş grafik seçenekleri sunuyoruz.",
    },
  ];

  return (
    <div className="bg-slate-900 text-slate-100 min-h-screen flex flex-col items-center justify-center p-6">
      {/* Başlık */}
      <h1 className="text-4xl font-extrabold text-emerald-500 mb-4">
        {typedText}
      </h1>

      {/* Tanıtım Yazısı */}
      <p className="text-lg text-slate-300 text-center max-w-2xl mb-6 leading-relaxed">
        Tahmincin, döviz ve enflasyon tahminlerini hızlı ve doğru bir şekilde 
        sunan modern bir finansal analiz platformudur. 
        Günlük ve aylık tahmin seçenekleriyle geleceğe dair ekonomik verileri
        görselleştirerek yatırım kararlarınızı destekler.
      </p>

      <p className="text-lg text-slate-300 text-center max-w-2xl mb-10 leading-relaxed">
        Gelişmiş algoritmalarımız ve görselleştirme araçlarımız sayesinde 
        piyasaları analiz etmek artık çok daha kolay! 
        Döviz tahminlerinden enflasyon oranlarına kadar birçok metriği 
        detaylı grafiklerle inceleyin.
      </p>

      {/* Buton */}
      <div className="flex space-x-6 mb-10">
        <Link
          to="/forecast"
          className="bg-emerald-700 text-white py-3 px-6 rounded-md font-bold text-lg hover:bg-emerald-600 hover:border hover:border-emerald-500 transition-all duration-300"
        >
          Tahminlere Başla
        </Link>
      </div>

      {/* Özellikler */}
      <section
        id="features"
        className="mt-16 w-full px-6 md:px-12 lg:px-24 py-12 bg-slate-800 rounded-lg shadow-md"
      >
        <h2 className="text-3xl font-extrabold text-emerald-500 mb-8 text-center">
          Uygulama Özellikleri
        </h2>
        <div className="flex flex-wrap justify-center gap-6">
          {cards.map((card, index) => (
            <div
              key={index}
              className="flex flex-col items-center bg-slate-900 p-6 rounded-lg shadow-md border border-slate-700 hover:border-emerald-500 transition-all duration-300 w-72"
            >
              <i className={`${card.icon} text-4xl text-emerald-500 mb-4`}></i>
              <h3 className="text-xl font-bold text-slate-100 mb-2">{card.title}</h3>
              <p className="text-slate-300 text-center">{card.description}</p>
            </div>
          ))}
        </div>
      </section>
      <Footer></Footer>
    </div>
  );
};

export default HomePage;

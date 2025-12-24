# Universal Memory - Urban Flow AI

## Mevcut Aşama
- **Durum:** Canlı Takip & Dashboard (Live Tracking & Dashboard)
- **Tarih:** 2025-12-24
- **Özet:** Gerçek zamanlı nesne takibi, giriş/çıkış sayımı ve WebSocket tabanlı dashboard tamamlandı.

## Teknik Kararlar (Stack)
- **Takip Algoritması:** Centroid Tracker (Euclidean Distance).
- **Sayım:** Sanal çizgi (Tripwire) geçişi ve yön tespiti (vektörel).
- **Video Yayını:** MJPEG (Low latency, HTTP multipart).
- **Veri Yayını:** WebSocket (`ws://localhost:8000/ws`).
- **UI:** React + TailwindCSS + StatsOverlay bileşeni.

## Karşılaşılan Engeller ve Çözümler
- **Pip Path Sorunu:** PowerShell'de `pip` yerine `python -m pip` kullanıldı.
- **Cache:** MJPEG stream mimarisi ile cache sorunları önlendi.

## Bir Sonraki Adım
- Kullanıcının sistemi canlı olarak test etmesi.
- Gerekirse performans optimizasyonu (Skip frames ayarı vs.).
- Uzun vadeli veritabanı kaydı (sqlite/postgres) eklenebilir.

## Notlar
- `roi_config.json` ile ROI ve Tripwire ayarları değiştirilebilir.

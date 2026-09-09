# Cowboy's Burger — Admin Panel

Menü fiyatlarını yönetmek için basit bir Flask paneli.

## Yerel çalıştırma
```
pip install -r requirements.txt
python app.py
```
Tarayıcıda: http://localhost:5000/admin
Varsayılan şifre: cowboys2026 (Render'da ADMIN_PASSWORD env değişkeniyle değiştir)

## Render'a Deploy
1. Bu klasörü bir GitHub reposuna yükle.
2. Render.com'da "New +" > "Web Service" > reposu seç.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app`
5. Environment Variables:
   - ADMIN_PASSWORD = (istediğin şifre)
   - SECRET_KEY = (rastgele bir metin)
6. Deploy sonrası verilen URL'i (örn. https://cowboys-admin.onrender.com)
   ana sitedeki `MENU_API_URL` değişkenine yaz.

## Not
Free tier'da dosya sistemi kalıcı değildir — servis yeniden başladığında
SQLite verisi sıfırlanabilir. Kalıcılık için Render'ın ücretsiz
PostgreSQL eklentisine geçmek gerekir (ileride konuşabiliriz).

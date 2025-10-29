# Distributed Counter (FastAPI + Redis lock)


## Çalıştırma


1. `docker-compose up --build`
2. Uygulamalar: `http://localhost:8000` ve `http://localhost:8001`
3. Sayaç başlangıç dosyası volume içinde `counting.txt` olarak saklanır.

Örnek istekler:


```bash
curl -X POST http://localhost:8000/increment
curl http://localhost:8000/count
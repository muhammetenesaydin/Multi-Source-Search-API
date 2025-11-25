# Çok Kaynaklı Arama Motoru API - Temiz Versiyon

Bu proje, çok kaynaklı arama motorunun yalnızca API işlevselliğine odaklandığı sadeleştirilmiş bir versiyonudur.

## Özellikler

- GitHub depolarını detaylı meta verilerle arama
- arXiv'den akademik makaleleri bulma
- İsteğe bağlı Semantic Scholar entegrasyonu
- DuckDuckGo kullanarak web arama geri dönüşü
- FastAPI ile REST API
- Docker desteği

## Kurulum

1. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

2. Ortam değişkenlerini ayarlayın. Bir `.env` dosyası oluşturun:
```env
GITHUB_TOKEN=github_tokeniniz_buraya
SERPAPI_KEY=serpapi_anahtarınız_buraya
SEMANTIC_SCHOLAR_KEY=semantic_scholar_anahtarınız_buraya
```

## Kullanım

### API Sunucusu

API sunucusunu başlatın:
```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000
```

Veya Docker kullanarak:
```bash
docker-compose up
```

API uç noktası:
```
GET /search?query=arama_sorgunuz&max_results=10
```

## API Uç Noktaları

- `GET /` - Kök uç nokta
- `GET /search` - Sorgu parametreleriyle arama uç noktası:
  - `query` (gerekli) - Arama sorgusu metni
  - `max_results` (isteğe bağlı) - Maksimum sonuç sayısı (1-100, varsayılan: 10)

## Proje Yapısı

```
.
├── api/
│   └── app.py              # FastAPI uygulaması
├── connectors/
│   ├── github.py           # GitHub API bağlantısı
│   ├── arxiv.py            # arXiv API bağlantısı
│   ├── semantic_scholar.py # Semantic Scholar API bağlantısı
│   └── web_search.py       # Web arama bağlantısı
├── aggregator.py           # Sonuç toplayıcı
├── models.py               # Veri modelleri
├── requirements.txt        # Python bağımlılıkları
├── Dockerfile              # Docker yapılandırması
└── docker-compose.yml      # Docker Compose yapılandırması
```

## Lisans

Bu proje MIT Lisansı ile lisanslanmıştır.
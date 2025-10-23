# LLM Setup Guide - Тохиргооны Зааварчилгаа

Энэхүү систем дараах LLM provider-ийг дэмждэг:
- ✅ **Google Gemini** (Санал болгож байна)
- ✅ **OpenAI** 
- ⚠️ **Ollama** (Локал орчинд л, үйлдвэрлэлд зөвлөхгүй)

---

## 🌟 Option 1: Google Gemini (Санал болгож байна)

### Давуу тал:
- 🆓 **Үнэгүй tier** - Сард 15 requests/min
- ⚡ **Хурдан** - gemini-1.5-flash маш хурдан
- 🧠 **Ухаалаг** - Монгол хэл сайн ойлгодог
- 💰 **Хямд** - Production-д хэрэглэхэд хямд

### 1. API Key авах:

1. **Google AI Studio руу орох:**
   - Вэб хаягаар очих: https://makersuite.google.com/app/apikey
   - Google account-аар нэвтрэх

2. **API Key үүсгэх:**
   - "Create API Key" товч дарах
   - Үүссэн key-г хуулах

3. **`.env` файлд тохируулах:**
   ```bash
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=AIzaSy...your-key-here
   GEMINI_MODEL=gemini-1.5-flash
   ```

### Боломжтой Model-үүд:

| Model | Хурд | Чадвар | Үнэ |
|-------|------|--------|-----|
| `gemini-1.5-flash` | ⚡⚡⚡ Хамгийн хурдан | 🧠🧠 Сайн | 💰 Хамгийн хямд |
| `gemini-1.5-pro` | ⚡⚡ Хурдан | 🧠🧠🧠 Маш сайн | 💰💰 Дунд |
| `gemini-pro` | ⚡ Дунд | 🧠🧠 Сайн | 💰 Хямд |

**Санал:** Production-д `gemini-1.5-flash` ашиглах - хурдан бас хямд!

---

## 💼 Option 2: OpenAI

### Давуу тал:
- 🏆 **Чадварлаг** - GPT-4 хамгийн ухаалаг
- 🔄 **Function Calling** - Маш сайн function calling дэмждэг
- 📚 **Баримт бичиг** - Сайн баримтжуулсан

### Сул тал:
- 💳 **Төлбөртэй** - Үнэгүй tier байхгүй
- 💰 **Үнэтэй** - GPT-4 нэлээд үнэтэй
- ⏳ **Удаан** - Gemini-с удаан

### 1. API Key авах:

1. **OpenAI Platform руу орох:**
   - Вэб хаяг: https://platform.openai.com/signup
   - Бүртгүүлэх эсвэл нэвтрэх

2. **API Key үүсгэх:**
   - Settings → API Keys руу очих
   - "Create new secret key" дарах
   - Key-г хуулаад аюулгүй хадгалах ⚠️

3. **Төлбөрийн мэдээлэл оруулах:**
   - Billing settings руу очих
   - Credit card мэдээлэл нэмэх
   - Сарын лимит тохируулах

4. **`.env` файлд тохируулах:**
   ```bash
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-...your-key-here
   OPENAI_MODEL=gpt-4
   ```

### Боломжтой Model-үүд:

| Model | Хурд | Чадвар | Үнэ (1M tokens) |
|-------|------|--------|-----------------|
| `gpt-4` | ⚡ Удаан | 🧠🧠🧠🧠 Онцгой | $30 |
| `gpt-4-turbo` | ⚡⚡ Дунд | 🧠🧠🧠🧠 Онцгой | $10 |
| `gpt-3.5-turbo` | ⚡⚡⚡ Хурдан | 🧠🧠🧠 Сайн | $0.50 |

---

## 🎯 Option 3: Custom OpenAI-Compatible API

OpenAI API-тай ижил байгууллагатай бусад үйлчилгээ ашиглах:

### Жишээ: Azure OpenAI

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your-azure-key
OPENAI_BASE_URL=https://your-resource.openai.azure.com/
OPENAI_MODEL=gpt-4
```

### Жишээ: Other providers (Together AI, Anyscale, etc.)

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your-provider-key
OPENAI_BASE_URL=https://api.together.xyz/v1
OPENAI_MODEL=mistralai/Mixtral-8x7B-Instruct-v0.1
```

---

## 🚀 Хэрхэн эхлүүлэх

### 1. Dependencies суулгах:

```bash
# Google Gemini-д зориулж
pip install google-generativeai

# Эсвэл OpenAI-д зориулж
pip install openai

# Эсвэл хоёуланд нь
pip install -r requirements.txt
```

### 2. `.env` файл тохируулах:

```bash
# .env.example-г хуулах
cp .env.example .env

# Өөрийн API key оруулах
nano .env
```

### 3. Application ажиллуулах:

```bash
# API Mode
python main.py

# CLI Mode (тест)
python main.py cli
```

---

## 🔐 Аюулгүй байдлын зөвлөмж

### ⚠️ ЧУХАЛ: API Key-г хамгаалах

1. **Хэзээ ч Git руу оруулах БОЛОХГҮЙ!**
   ```bash
   # .env файл .gitignore-д байгаа эсэхийг шалгах
   cat .gitignore | grep .env
   ```

2. **Production орчинд environment variable ашиглах:**
   ```bash
   # Server дээр
   export GEMINI_API_KEY="your-key-here"
   export LLM_PROVIDER="gemini"
   ```

3. **Docker ашиглавал:**
   ```dockerfile
   # docker-compose.yml
   environment:
     - GEMINI_API_KEY=${GEMINI_API_KEY}
     - LLM_PROVIDER=gemini
   ```

4. **Cloud deployment (Heroku, Google Cloud Run, etc.):**
   ```bash
   # Heroku жишээ
   heroku config:set GEMINI_API_KEY=your-key-here
   heroku config:set LLM_PROVIDER=gemini
   ```

---

## 📊 Үнийн харьцуулалт

### 10,000 хэрэглэгчид нэг сард:
(Дундажаар хэрэглэгч бүр 5 мессеж илгээж, хариу авна)

| Provider | Model | Өртөг | Тайлбар |
|----------|-------|-------|---------|
| **Google Gemini** | gemini-1.5-flash | **$0-5** | Үнэгүй tier хангалттай! |
| Google Gemini | gemini-1.5-pro | $50-100 | Илүү чадварлаг хэрэгтэй бол |
| OpenAI | gpt-3.5-turbo | $25-50 | Хямд OpenAI сонголт |
| OpenAI | gpt-4 | $150-300 | Хамгийн үнэтэй, хамгийн сайн |

**🏆 Санал: Google Gemini gemini-1.5-flash** - Үнэ чанарын хамгийн сайн харьцаа!

---

## 🧪 Тест хийх

### CLI Mode-оор тест:

```bash
python main.py cli

# Дараах команд туршаад үзнэ үү:
👤 You: Маргааш 10:00-д үс засалт захиалмаар байна
👤 You: Миний захиалгуудыг харуулаарай
👤 You: Захиалга цуцлаарай
```

### API-р тест (curl):

```bash
# Server ажиллуулах
python main.py

# Өөр terminal дээр:
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Маргааш 10:00-д үс засалт захиалмаар байна",
    "user_id": "test_user"
  }'
```

---

## 🐛 Алдаа засах

### "GEMINI_API_KEY not set"

```bash
# .env файл үүсгэсэн эсэхийг шалгах
ls -la | grep .env

# Key тохируулах
echo 'GEMINI_API_KEY=your-key-here' >> .env
echo 'LLM_PROVIDER=gemini' >> .env
```

### "google.generativeai not installed"

```bash
pip install google-generativeai
```

### "Rate limit exceeded"

Gemini үнэгүй tier:
- 15 requests/minute
- 1500 requests/day

Шийдэл:
1. Paid tier руу шилжих
2. Rate limiting нэмэх application-д
3. Request кэш хийх

---

## 📚 Нэмэлт мэдээлэл

### Google Gemini Documentation:
- Эхлэх: https://ai.google.dev/docs
- Python SDK: https://github.com/google/generative-ai-python
- Pricing: https://ai.google.dev/pricing

### OpenAI Documentation:
- API Reference: https://platform.openai.com/docs
- Pricing: https://openai.com/pricing
- Best Practices: https://platform.openai.com/docs/guides/production-best-practices

---

## 💡 Санал

**Эхлэлт:**
1. Google Gemini (`gemini-1.5-flash`) ашиглаарай - үнэгүй бас хурдан!
2. Үйлдвэрлэлд гарахаас өмнө тестлээд үзээрэй
3. Хэрэв илүү сайн чанар хэрэгтэй бол `gemini-1.5-pro` ашиглаарай

**Production:**
1. API Key-г environment variable-аар дамжуулах
2. Rate limiting нэмэх
3. Error handling сайжруулах
4. Logging нэмэх
5. Monitoring тохируулах

Амжилт хүсье! 🚀

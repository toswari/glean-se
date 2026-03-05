# Using Alibaba Cloud Model Studio as an OpenAI-Compatible Provider

This guide explains how to configure the Docling RAG Agent to use **Alibaba Cloud Model Studio** (DashScope) via its OpenAI-compatible API endpoint.

---

## 1. Overview

Alibaba Cloud Model Studio (DashScope) provides an OpenAI-compatible API that allows you to use their models with minimal code changes. The RAG Agent can seamlessly switch to Alibaba Cloud by configuring environment variables.

### Supported Endpoints

| Region | Endpoint | Status |
|--------|----------|--------|
| International | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` | ✅ Recommended |
| Asia Pacific (Southeast) | `https://dashscope-ap-southeast-1.aliyuncs.com/compatible-mode/v1` | ⚠️ DNS issues in some regions |
| China | `https://dashscope.aliyuncs.com/compatible-mode/v1` | For China region |

**Note:** The international endpoint (`dashscope-intl.aliyuncs.com`) is recommended for all API keys as it provides the best reliability. The ap-southeast-1 endpoint may have DNS resolution issues in some regions.

---

## 2. Prerequisites

1. **Alibaba Cloud Account**: Sign up at [Alibaba Cloud](https://www.alibabacloud.com/)
2. **Model Studio Access**: Navigate to [Model Studio Console](https://modelstudio.console.alibabacloud.com/)
3. **API Key**: Generate an API key from the console

---

## 3. Environment Configuration

### Step 1: Get Your API Key

1. Log in to [Alibaba Cloud Model Studio Console](https://modelstudio.console.alibabacloud.com/)
2. Navigate to **API Key Management**
3. Create a new API key or use an existing one

### Step 2: Configure `.env` File

Edit your `.env` file with the following settings:

```env
# Select Alibaba as the provider
LLM_PROVIDER=alibaba

# Alibaba Cloud Model Studio API Key
ALIBABA_API_KEY=your-alibaba-api-key-here

# Optional: Custom base URL (auto-detected based on API key)
# For sk-sp- keys (Southeast Asia):
# ALIBABA_BASE_URL=https://dashscope-ap-southeast-1.aliyuncs.com/compatible-mode/v1
# For other international keys:
# ALIBABA_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1

# Model Selection - Use Alibaba/DashScope model names
# Examples: qwen-turbo, qwen-plus, qwen-max, qwen2.5-72b-instruct
LLM_CHOICE=qwen-plus

# Embedding Model - Use Alibaba embedding models
# Examples: text-embedding-v2, text-embedding-v3
EMBEDDING_MODEL=text-embedding-v3
```

### Available Models

#### LLM Models
| Model | Description |
|-------|-------------|
| `qwen-turbo` | Fast, cost-effective model |
| `qwen-plus` | Balanced performance and cost |
| `qwen-max` | Most capable model |
| `qwen2.5-72b-instruct` | Large instruction-tuned model |

#### Embedding Models
| Model | Description |
|-------|-------------|
| `text-embedding-v2` | Previous generation embedding model |
| `text-embedding-v3` | Latest embedding model with improved performance |
| `text-embedding-v3` (Model ID: 2842587) | Alibaba Cloud Model Studio text embedding model - see [Model Console](https://modelstudio.console.alibabacloud.com/ap-southeast-1?tab=doc&accounttraceid=69648193b6f04d43bf2509e356d123bchbek#/doc/?type=model&url=2842587) |

---

## 4. How It Works

The RAG Agent uses the `openai` Python SDK and `pydantic-ai`'s `OpenAIModel` / `OpenAIProvider`. When `LLM_PROVIDER=alibaba`:

1. The `ALIBABA_API_KEY` is used for authentication
2. Requests are sent to the Alibaba DashScope OpenAI-compatible endpoint
3. Model names are mapped to Alibaba's model IDs

### Code Flow

```
User Query → RAG Agent → get_llm_model() → OpenAIProvider (Alibaba endpoint)
                                      ↓
                              Alibaba DashScope API
                                      ↓
                              Response to Agent
```

---

## 5. Testing the Integration

### Test Basic Chat Completion

```bash
uv run python -c "
import os
import openai
from dotenv import load_dotenv
load_dotenv()

client = openai.AsyncOpenAI(
    api_key=os.getenv('ALIBABA_API_KEY'),
    base_url=os.getenv('ALIBABA_BASE_URL', 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1'),
)

async def main():
    resp = await client.chat.completions.create(
        model=os.getenv('LLM_CHOICE', 'qwen-plus'),
        messages=[{'role': 'user', 'content': 'Hello from Alibaba Model Studio!'}],
    )
    print(resp.choices[0].message.content)

import asyncio
asyncio.run(main())
"
```

### Test Embeddings

```bash
uv run python -c "
import os
import openai
from dotenv import load_dotenv
load_dotenv()

client = openai.AsyncOpenAI(
    api_key=os.getenv('ALIBABA_API_KEY'),
    base_url=os.getenv('ALIBABA_BASE_URL', 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1'),
)

async def main():
    resp = await client.embeddings.create(
        model=os.getenv('EMBEDDING_MODEL', 'text-embedding-v3'),
        input=['Hello from Alibaba Model Studio!'],
    )
    print('Embedding length:', len(resp.data[0].embedding))

import asyncio
asyncio.run(main())
"
```

### Test Full RAG Pipeline

```bash
# Ingest documents using Alibaba embeddings
uv run python -m ingestion.ingest --documents documents/

# Start the agent using Alibaba LLM
uv run python cli.py
```

---

## 6. Regional Endpoints

Depending on your location and compliance requirements, you can use different endpoints:

| Region | Endpoint |
|--------|----------|
| International | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| China | `https://dashscope.aliyuncs.com/compatible-mode/v1` |

Set the `ALIBABA_BASE_URL` environment variable to use a specific endpoint:

```env
ALIBABA_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
```

---

## 7. Pricing and Rate Limits

- **LLM Pricing**: Varies by model (qwen-turbo is cheapest, qwen-max is most expensive)
- **Embedding Pricing**: Charged per 1K tokens
- **Rate Limits**: Depends on your Alibaba Cloud account tier

Check the [official pricing page](https://www.alibabacloud.com/en/product/pricing) for current rates.

---

## 8. Troubleshooting

### Common Issues

**Issue**: `401 Unauthorized`
- **Solution**: Verify your `ALIBABA_API_KEY` is correct and active

**Issue**: `404 Not Found`
- **Solution**: Check that `ALIBABA_BASE_URL` is correct and the model exists

**Issue**: Model not found error
- **Solution**: Ensure the model name in `LLM_CHOICE` is a valid Alibaba/DashScope model

**Issue**: Slow response times
- **Solution**: Try using a closer regional endpoint or switch to `qwen-turbo` for faster responses

---

## 9. Switching Between Providers

You can easily switch between providers by changing `LLM_PROVIDER`:

```env
# Use OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Use Alibaba Cloud
LLM_PROVIDER=alibaba
ALIBABA_API_KEY=sk-...

# Use Clarifai
LLM_PROVIDER=clarifai
CLARIFAI_API_KEY=...
CLARIFAI_OPENAI_BASE_URL=...
```

---

## 10. References

- [Alibaba Cloud Model Studio Documentation](https://help.aliyun.com/zh/model-studio/)
- [DashScope API Reference](https://help.aliyun.com/zh/model-studio/developer-reference/)
- [Alibaba Cloud Console](https://modelstudio.console.alibabacloud.com/)
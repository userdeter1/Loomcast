# Loomcast Troubleshooting & FAQ

Guide for diagnosing, troubleshooting, and resolving common issues with Loomcast and local LLM runtimes.

---

## 1. Quick Diagnostic: `loomcast doctor`

When encountering any issue, run `loomcast doctor` first:

```bash
loomcast doctor
```

It inspects 5 key layers:
1. Configuration loading (`config.json`)
2. Environment variables (`LOOMCAST_*`)
3. Runtimes HTTP connectivity (Ollama, LM Studio, llama.cpp)
4. Catalog reachability
5. SHA-256 integrity of the static catalog

---

## 2. Runtime Connectivity Issues

### Ollama Runtime Offline
**Symptom**: `RuntimeUnavailableError` or `Runtime OLLAMA: unavailable` in `loomcast doctor`.

**Solution**:
1. Check if Ollama service is running:
   ```bash
   ollama serve
   ```
2. Verify default URL (`http://127.0.0.1:11434`):
   ```bash
   curl http://127.0.0.1:11434/api/tags
   ```
3. If Ollama is running on a non-standard port or IP, update Loomcast config or set environment variable:
   ```bash
   loomcast config
   # or
   export LOOMCAST_OLLAMA_URL="http://localhost:11434"
   ```

### LM Studio Connection Issues
**Symptom**: `LMSTUDIO: unavailable` or endpoint error.

**Solution**:
1. Open LM Studio.
2. Navigate to the **Local Server** tab (left sidebar icon).
3. Click **Start Server** (default port: `1234`).
4. Ensure CORS support is enabled if calling from web browsers.

### llama.cpp Server Issues
**Symptom**: `LLAMACPP: unavailable`.

**Solution**:
1. Start `llama-server` binary with your target GGUF model:
   ```bash
   ./llama-server -m /path/to/model.gguf --port 8080
   ```
2. Ensure endpoint URL matches `http://127.0.0.1:8080`.

---

## 3. Model Management & API Restrictions

### Why does `loomcast install` return an error on LM Studio or llama.cpp?
- **Explanation**: Ollama exposes an HTTP endpoint (`/api/pull`) to download and manage model files dynamically. LM Studio and llama.cpp require models to be loaded manually through their graphical interface or command-line parameters.
- **Solution**: Load models directly inside LM Studio or start `llama-server` with your desired GGUF model.

---

## 4. Catalog & Network Resiliency

### "Dynamic catalog unavailable (fell back to static catalog)"
- **Explanation**: Loomcast couldn't reach the live remote catalog index due to network interruption or offline operation.
- **Behavior**: Loomcast automatically switches to its embedded static catalog. All search and recommendation commands continue working seamless without failing.

---

## 5. Configuration & Environment Variables

Loomcast configuration can be controlled via environment variables:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `LOOMCAST_DEFAULT_BACKEND` | Default runtime (`ollama`, `lmstudio`, `llamacpp`) | `ollama` |
| `LOOMCAST_OLLAMA_URL` | Ollama HTTP endpoint | `http://127.0.0.1:11434` |
| `LOOMCAST_LMSTUDIO_URL` | LM Studio HTTP endpoint | `http://127.0.0.1:1234` |
| `LOOMCAST_LLAMACPP_URL` | llama.cpp HTTP endpoint | `http://127.0.0.1:8080` |
| `LOOMCAST_CATALOG_SOURCE` | Catalog mode (`dynamic`, `static`) | `dynamic` |

To override via CLI:
```bash
loomcast config --set-default lmstudio
```

---

## 6. Frequently Asked Questions (FAQ)

### Does Loomcast execute inference or compute weights itself?
No. Loomcast is a lightweight orchestration layer (SDK + CLI) that routes requests to your installed local runtimes. It does not replace Ollama or LM Studio.

### Can I compare different models across runtimes?
Yes! `loomcast compare` accepts specific models per runtime or auto-detects installed models:
```bash
loomcast compare "Write a poem" -b ollama -b lmstudio
```

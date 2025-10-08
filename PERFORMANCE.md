# Chakra Performance Settings

Quick reference for startup options:

## Standard Development Mode
```bash
./start_chakra.sh
```
- Auto-reload enabled
- Single worker
- Development Angular build
- Model pre-warming included

## Production Mode
```bash
./start_chakra.sh --production
```
- Multiple workers for better performance
- No auto-reload (faster startup)
- Production Angular build
- Model pre-warming included

## Just Backend
```bash
./start_backend.sh
```
- Development mode by default

## Just Backend (Production)
```bash
./start_backend.sh --production
```
- Production mode with multiple workers

## Model Warm-up Only
```bash
./warm_up_ollama.sh
```
- Pre-warms the Ollama model without starting servers

For more details, see `docs/performance_optimization.md`
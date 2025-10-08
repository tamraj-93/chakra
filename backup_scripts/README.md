# Original Scripts (Backup)

This directory contains backups of the original startup scripts before performance optimizations were applied. These are kept for reference purposes only.

The main scripts in the parent directory now include all performance optimizations by default.

## Original Scripts

- `start_backend.sh`: Original script for starting the backend server
- `start_chakra.sh`: Original script for starting both backend and frontend

## Improvements Made

The new scripts in the parent directory include:

1. Multi-worker support
2. Ollama model pre-warming
3. Production/Development mode switch
4. Better resource utilization

For full details of the optimizations, see `../docs/performance_optimization.md`
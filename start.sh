#!/bin/bash
# Change Impact Memory - Startup Script
# Starts both backend (FastAPI) and frontend (Vite) servers

echo "🧠 Change Impact Memory"
echo "========================"
echo ""

# Start backend
echo "Starting backend (FastAPI) on http://localhost:8000..."
cd "$(dirname "$0")"
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend
sleep 2

# Start frontend
echo "Starting frontend (Vite) on http://localhost:5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Application running:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers."

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait

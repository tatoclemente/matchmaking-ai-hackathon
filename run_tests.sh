#!/bin/bash

echo "🧪 Ejecutando tests del Matchmaking Service..."
echo ""

export PYTHONPATH=.

echo "📍 Test Haversine Distance"
echo "----------------------------"
python3 -c "from tests.utils.test_geo_utils import test_haversine_distance; test_haversine_distance(); print('✓ Haversine distance test passed')"

echo ""
echo "🎯 Test Scoring Service"
echo "----------------------------"
python3 tests/test_scoring_service.py

echo ""
echo "✅ Todos los tests completados"

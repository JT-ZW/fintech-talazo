# app/api/iot.py
"""
IoT and sensor data API endpoints for Talazo AgriFinance Platform.
"""

import random
import math
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError, Schema, fields, validate
from app.core.extensions import create_error_response, create_success_response

iot_bp = Blueprint('iot', __name__)


class SensorDataSchema(Schema):
    """Schema for sensor data validation."""
    sensor_id = fields.Str(required=True)
    sensor_type = fields.Str(required=True, validate=validate.OneOf([
        'soil_moisture', 'temperature', 'humidity', 'ph', 
        'nitrogen', 'phosphorus', 'potassium', 'light'
    ]))
    value = fields.Float(required=True)
    unit = fields.Str(required=True)
    location = fields.Dict(missing=None)
    farmer_id = fields.Int(missing=None)


@iot_bp.route('/sensor-data', methods=['POST'])
def receive_sensor_data():
    """Receive data from IoT sensors."""
    try:
        # Get request data
        json_data = request.get_json()
        if not json_data:
            return jsonify(create_error_response("No sensor data provided", 400))

        # Handle batch data
        if isinstance(json_data, list):
            sensor_readings = json_data
        else:
            sensor_readings = [json_data]

        # Validate each sensor reading
        schema = SensorDataSchema()
        validated_readings = []
        
        for reading in sensor_readings:
            try:
                validated_reading = schema.load(reading)
                validated_reading['timestamp'] = datetime.utcnow().isoformat()
                validated_reading['processed'] = False
                validated_readings.append(validated_reading)
            except ValidationError as err:
                current_app.logger.warning(f"Invalid sensor reading: {err.messages}")
                continue

        if not validated_readings:
            return jsonify(create_error_response("No valid sensor readings", 400))

        # In production, this would save to database and trigger processing
        # For now, simulate processing
        for reading in validated_readings:
            reading['processed'] = True
            current_app.logger.info(f"Processed sensor reading: {reading['sensor_id']}")

        return jsonify(create_success_response({
            'received_count': len(validated_readings),
            'processed_count': len(validated_readings),
            'readings': validated_readings
        }, "Sensor data received and processed successfully"))

    except Exception as e:
        current_app.logger.error(f"Error processing sensor data: {str(e)}")
        return jsonify(create_error_response("Failed to process sensor data", 500))


@iot_bp.route('/realtime-data', methods=['GET'])
def get_realtime_data():
    """Get real-time sensor data."""
    try:
        # Get query parameters
        farmer_id = request.args.get('farmer_id', type=int)
        sensor_type = request.args.get('sensor_type')
        limit = request.args.get('limit', 100, type=int)

        # Simulate real-time sensor data
        sensor_types = [
            {'type': 'soil_moisture', 'unit': '%', 'range': (20, 80)},
            {'type': 'temperature', 'unit': '°C', 'range': (15, 35)},
            {'type': 'humidity', 'unit': '%', 'range': (40, 90)},
            {'type': 'ph', 'unit': 'pH', 'range': (5.5, 8.5)},
            {'type': 'nitrogen', 'unit': 'ppm', 'range': (10, 50)},
            {'type': 'phosphorus', 'unit': 'ppm', 'range': (5, 25)},
            {'type': 'potassium', 'unit': 'ppm', 'range': (100, 300)}
        ]

        # Filter by sensor type if specified
        if sensor_type:
            sensor_types = [s for s in sensor_types if s['type'] == sensor_type]

        # Generate simulated data
        realtime_data = []
        base_time = datetime.utcnow()

        for i in range(min(limit, 50)):  # Limit to prevent excessive data
            for sensor in sensor_types:
                min_val, max_val = sensor['range']
                reading = {
                    'sensor_id': f"sensor_{sensor['type']}_{random.randint(100, 999)}",
                    'sensor_type': sensor['type'],
                    'value': round(random.uniform(min_val, max_val), 2),
                    'unit': sensor['unit'],
                    'timestamp': (base_time - timedelta(minutes=i)).isoformat(),
                    'farmer_id': farmer_id or random.randint(1, 10),
                    'location': {
                        'latitude': round(random.uniform(-20.0, -15.0), 6),
                        'longitude': round(random.uniform(25.0, 33.0), 6)  # Zimbabwe coordinates
                    },
                    'status': 'active'
                }
                realtime_data.append(reading)

        # Sort by timestamp (newest first)
        realtime_data.sort(key=lambda x: x['timestamp'], reverse=True)

        return jsonify(create_success_response({
            'data': realtime_data[:limit],
            'total_readings': len(realtime_data),
            'last_updated': datetime.utcnow().isoformat(),
            'filters': {
                'farmer_id': farmer_id,
                'sensor_type': sensor_type,
                'limit': limit
            }
        }, "Real-time sensor data retrieved successfully"))

    except Exception as e:
        current_app.logger.error(f"Error retrieving real-time data: {str(e)}")
        return jsonify(create_error_response("Failed to retrieve real-time data", 500))


@iot_bp.route('/simulate-sensors', methods=['POST'])
def simulate_sensors():
    """Simulate sensor data for testing and development."""
    try:
        # Get simulation parameters
        json_data = request.get_json() or {}
        num_sensors = json_data.get('num_sensors', 5)
        duration_hours = json_data.get('duration_hours', 24)
        interval_minutes = json_data.get('interval_minutes', 30)
        farmer_id = json_data.get('farmer_id', 1)

        # Calculate number of readings
        total_readings = int((duration_hours * 60) / interval_minutes)
        
        # Generate simulated sensor network
        simulated_data = []
        base_time = datetime.utcnow()
        
        sensor_configs = [
            {'type': 'soil_moisture', 'unit': '%', 'baseline': 45, 'variation': 15},
            {'type': 'temperature', 'unit': '°C', 'baseline': 25, 'variation': 8},
            {'type': 'humidity', 'unit': '%', 'baseline': 65, 'variation': 20},
            {'type': 'ph', 'unit': 'pH', 'baseline': 6.5, 'variation': 1.5},
            {'type': 'nitrogen', 'unit': 'ppm', 'baseline': 30, 'variation': 15}
        ]

        for i in range(total_readings):
            timestamp = (base_time - timedelta(minutes=i * interval_minutes)).isoformat()
            
            for j, config in enumerate(sensor_configs[:num_sensors]):
                # Simulate realistic sensor drift and noise
                base_value = config['baseline']
                variation = config['variation']
                
                # Add some realistic patterns (e.g., temperature cycles)
                if config['type'] == 'temperature':
                    # Simulate daily temperature cycle
                    hour_of_day = (base_time - timedelta(minutes=i * interval_minutes)).hour
                    daily_cycle = 5 * math.sin((hour_of_day - 6) * math.pi / 12)
                    base_value += daily_cycle
                
                value = base_value + random.uniform(-variation/2, variation/2)
                value = max(0, round(value, 2))  # Ensure positive values
                
                reading = {
                    'sensor_id': f"sim_{config['type']}_{j+1:03d}",
                    'sensor_type': config['type'],
                    'value': value,
                    'unit': config['unit'],
                    'timestamp': timestamp,
                    'farmer_id': farmer_id,
                    'location': {
                        'latitude': round(-18.0 + random.uniform(-0.01, 0.01), 6),
                        'longitude': round(31.0 + random.uniform(-0.01, 0.01), 6)
                    },
                    'simulated': True,
                    'quality': random.choice(['excellent', 'good', 'fair'])
                }
                simulated_data.append(reading)

        return jsonify(create_success_response({
            'simulated_readings': len(simulated_data),
            'parameters': {
                'num_sensors': num_sensors,
                'duration_hours': duration_hours,
                'interval_minutes': interval_minutes,
                'farmer_id': farmer_id
            },
            'data_sample': simulated_data[:10],  # Return first 10 as sample
            'total_data_points': len(simulated_data),
            'simulation_period': {
                'start': (base_time - timedelta(hours=duration_hours)).isoformat(),
                'end': base_time.isoformat()
            }
        }, "Sensor simulation completed successfully"))

    except Exception as e:
        current_app.logger.error(f"Error simulating sensors: {str(e)}")
        return jsonify(create_error_response("Failed to simulate sensors", 500))


@iot_bp.route('/sensors/status', methods=['GET'])
def get_sensors_status():
    """Get status of all sensors in the network."""
    try:
        # Simulate sensor network status
        sensors_status = []
        sensor_types = ['soil_moisture', 'temperature', 'humidity', 'ph', 'nitrogen']
        
        for i, sensor_type in enumerate(sensor_types):
            for j in range(3):  # 3 sensors per type
                sensor = {
                    'sensor_id': f"sensor_{sensor_type}_{j+1:03d}",
                    'type': sensor_type,
                    'status': random.choice(['online', 'online', 'online', 'offline', 'maintenance']),
                    'last_reading': (datetime.utcnow() - timedelta(minutes=random.randint(1, 60))).isoformat(),
                    'battery_level': random.randint(20, 100),
                    'signal_strength': random.randint(60, 100),
                    'location': {
                        'latitude': round(-18.0 + random.uniform(-0.1, 0.1), 6),
                        'longitude': round(31.0 + random.uniform(-0.1, 0.1), 6)
                    }
                }
                sensors_status.append(sensor)

        # Calculate summary statistics
        total_sensors = len(sensors_status)
        online_sensors = len([s for s in sensors_status if s['status'] == 'online'])
        offline_sensors = len([s for s in sensors_status if s['status'] == 'offline'])
        
        return jsonify(create_success_response({
            'sensors': sensors_status,
            'summary': {
                'total_sensors': total_sensors,
                'online': online_sensors,
                'offline': offline_sensors,
                'maintenance': total_sensors - online_sensors - offline_sensors,
                'network_health': round((online_sensors / total_sensors) * 100, 1)
            },
            'last_updated': datetime.utcnow().isoformat()
        }, "Sensor network status retrieved successfully"))

    except Exception as e:
        current_app.logger.error(f"Error retrieving sensor status: {str(e)}")
        return jsonify(create_error_response("Failed to retrieve sensor status", 500))

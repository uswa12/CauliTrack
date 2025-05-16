import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import PatchFreshnessTable from './components/PatchFreshnessTable';
import './app.css';

function App() {
  const [socket, setSocket] = useState(null);
  const [selectedPatch, setSelectedPatch] = useState(1);
  const [selectedPhase, setSelectedPhase] = useState('farm');
  const [chartData, setChartData] = useState([]);
  const [baseTime, setBaseTime] = useState(null);
  const [tempData, setTempData] = useState([]);
  const [humidityData, setHumidityData] = useState([]);
  const [soilData, setSoilData] = useState([]);
  const [sunlightData, setSunlightData] = useState([]);
  const [airflowData, setAirflowData] = useState([]);
  const [vibrationData, setVibrationData] = useState([]);

  const phaseOptions = ['farm', 'depot', 'transport', 'market'];

  useEffect(() => {
    const newSocket = io('http://localhost:5000');
    setSocket(newSocket);
    return () => newSocket.close();
  }, []);

  useEffect(() => {
    if (!socket) return;

    socket.on('sensor_update', data => {
      if (data.patch_id === selectedPatch && data.phase === selectedPhase) {
        const timestamp = new Date(data.time).getTime();
        const freshness = data.freshness;
        
        let startTime = baseTime;
        if (startTime === null) {
          startTime = timestamp;
          setBaseTime(timestamp);
        }
        const elapsed = ((timestamp - startTime) / 1000).toFixed(2);
        const timeValue = parseFloat(elapsed);

        setChartData(prev => [...prev, { time: timeValue, freshness }]);
        setTempData(prev => [...prev, { time: timeValue, temperature: data.temperature }]);
        setHumidityData(prev => [...prev, { time: timeValue, humidity: data.humidity }]);

        if (selectedPhase === 'farm') {
          setSoilData(prev => [...prev, { time: timeValue, soil_moisture: data.soil_moisture }]);
          setSunlightData(prev => [...prev, { time: timeValue, sunlight: data.sunlight }]);
        } else if (selectedPhase === 'depot') {
          setAirflowData(prev => [...prev, { time: timeValue, airflow: data.airflow }]);
        } else if (selectedPhase === 'transport') {
          setVibrationData(prev => [...prev, { time: timeValue, vibration: data.vibration }]);
        } else if (selectedPhase === 'market') {
          setSunlightData(prev => [...prev, { time: timeValue, sunlight: data.sunlight }]);
        }
      }
    });

    return () => {
      socket.off('sensor_update');
    };
  }, [socket, selectedPatch, selectedPhase, baseTime]);

  const resetData = () => {
    setChartData([]);
    setTempData([]);
    setHumidityData([]);
    setSoilData([]);
    setSunlightData([]);
    setAirflowData([]);
    setVibrationData([]);
    setBaseTime(null);
  };

  const handlePhaseClick = (phase) => {
    setSelectedPhase(phase);
    resetData();
  };

  const handleStart = () => {
    fetch(`http://localhost:5000/start/${selectedPhase}`, { method: 'POST' })
      .then(res => res.json())
      .catch(console.error);
    resetData();
  };

  const handleStop = () => {
    fetch(`http://localhost:5000/stop/${selectedPhase}`, { method: 'POST' })
      .then(res => res.json())
      .catch(console.error);
  };

  const handleLoad = () => {
    resetData();
    fetch(`http://localhost:5000/api/history?patch_id=${selectedPatch}&phase=${selectedPhase}`)
      .then(res => res.json())
      .then(data => {
        if (!Array.isArray(data) || data.length === 0) return;
        const t0 = data[0].timestamp;
        const newData = data.map(entry => ({
          time: parseFloat(((entry.timestamp - t0) / 1000).toFixed(2)),
          freshness: entry.freshness
        }));
        setChartData(newData);
      })
      .catch(console.error);
  };

  const patchOptions = Array.from({ length: 100 }, (_, i) => (
    <option key={i + 1} value={i + 1}>{i + 1}</option>
  ));

  const renderChart = (title, data, dataKey, unit, maxY = 1000) => (
    <div className="chart-container">
      <h3>{title}</h3>
      {data.length === 0 ? <p>No data yet.</p> : (
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={data} margin={{ top: 5, right: 5, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" label={{ value: 'Time (s)', position: 'insideBottom', offset: -5, fontSize: 12 }} tick={{ fontSize: 12 }} />
            <YAxis domain={[0, maxY]} label={{ value: unit, angle: -90, position: 'insideLeft', offset: -5, fontSize: 12 }} tick={{ fontSize: 12 }} />
            <Tooltip />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Line type="monotone" dataKey={dataKey} stroke="#8884d8" name={unit} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );

  return (
    <div className="app-container">
      <h1>Smart Cauliflower Freshness Tracker with Simulated IoT Sensors and Real-Time Visualization</h1>

      <div className="controls">
      <div class="container">
        <div className="phase-buttons">
          {phaseOptions.map(phase => (
            <button
              key={phase}
              className={selectedPhase === phase ? 'phase-button active' : 'phase-button'}
              onClick={() => handlePhaseClick(phase)}
            >
              {phase.charAt(0).toUpperCase() + phase.slice(1)}
            </button>
          ))}</div>
        </div>

        <div className="action-buttons">
          <button onClick={handleStart}>▶ Start</button>
          <button onClick={handleStop}>■ Stop</button>
          <button onClick={handleLoad}>📜 Load History</button>
        </div>

        <div className="patch-selector">
          <label>
            Patch ID:
            <select
              value={selectedPatch}
              onChange={e => {
                setSelectedPatch(parseInt(e.target.value));
                resetData();
              }}
            >
              {patchOptions}
            </select>
          </label>
        </div>
      </div>

      <div className="charts-grid">
        <div className="charts-row">
          {renderChart(`Freshness for ${selectedPhase} Phase`, chartData, 'freshness', 'Freshness (%)', 100)}
          {renderChart(`Temperature for ${selectedPhase} Phase`, tempData, 'temperature', 'Temperature (°C)', 50)}
          {renderChart(`Humidity for ${selectedPhase} Phase`, humidityData, 'humidity', 'Humidity (%)', 100)}
        </div>
        <div className="charts-row">
          {selectedPhase === 'farm' && (
            <>
              {renderChart('Soil Moisture', soilData, 'soil_moisture', 'Soil Moisture (%)', 100)}
              {renderChart('Sunlight', sunlightData, 'sunlight', 'Sunlight (lux)', 1000)}
            </>
          )}
          {selectedPhase === 'depot' && (
            renderChart('Airflow', airflowData, 'airflow', 'Airflow (m/s)', 12)
          )}
          {selectedPhase === 'transport' && (
            renderChart('Vibration', vibrationData, 'vibration', 'Vibration (units)', 12)
          )}
          {selectedPhase === 'market' && (
            renderChart('Sunlight', sunlightData, 'sunlight', 'Sunlight (lux)', 1000)
          )}
        </div>
      </div>

      <div className="table-container">
        <h3>Average Freshness per Patch (24h)</h3>
        <PatchFreshnessTable phase={selectedPhase} />
      </div>
    </div>
  );
}

export default App;
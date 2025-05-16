import React, { useEffect, useState } from 'react';

function PatchFreshnessTable({ phase }) {
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchPatchData = async () => {
      try {
        const res = await fetch(`http://localhost:5000/api/summary/patches?phase=${phase}`);
        const json = await res.json();
        setData(json);
      } catch (err) {
        console.error('Failed to fetch patch-level summary:', err);
      }
    };

    fetchPatchData();
    const interval = setInterval(fetchPatchData, 5000); // Update every 5 sec
    return () => clearInterval(interval);
  }, [phase]);

  return (
    <div style={{ padding: '10px' }}>
      <h4>Average Freshness per Patch (Last 24 Hours) – {phase}</h4>
      <table
  border="1"
  cellPadding="6"
  style={{
    borderCollapse: "collapse",
    width: "80%",
    margin: "2rem auto",
    boxShadow: "0 4px 10px rgba(0, 0, 0, 0.1)",
    fontFamily: "Arial, sans-serif",
    textAlign: "center",
    backgroundColor: "#fdfdfd",
  }}
>
  <thead>
    <tr style={{ backgroundColor: "#4CAF50", color: "white" }}>
      <th style={{ padding: "12px" }}>Patch ID</th>
      <th style={{ padding: "12px" }}>Avg Freshness (24h)</th>
    </tr>
  </thead>
  <tbody>
    {data.map(row => (
      <tr key={row.patch_id} style={{ borderBottom: "1px solid #ccc" }}>
        <td style={{ padding: "10px" }}>{row.patch_id}</td>
        <td style={{ padding: "10px" }}>{row.avg_freshness}</td>
      </tr>
    ))}
  </tbody>
</table>

    </div>
  );
}

export default PatchFreshnessTable;

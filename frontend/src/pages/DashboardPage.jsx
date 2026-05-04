import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function DashboardPage() {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  const [orders, setOrders] = useState([]);
  const [loading , setLoading] = useState(true);
  const [error, setError] = useState("");
  useEffect(() => {
    if (!token) {
      navigate("/");
    } else {
      getMyOrders();
    }
  }, [token, navigate]);

  if (!token) {
    return null;
  }

  async function getMyOrders() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:8000/my-orders", {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Could not load orders at the moment.");
      }
    

      const data = await response.json();
      setOrders(data);
    } catch (error) {
      console.error(error);
      setError("Could not load orders");
    } finally {
      setLoading(false);
    }
  }

  async function handleLogout() {
    localStorage.removeItem("token");
    navigate("/");
  }

  return (
    <div style={{ padding: "40px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <h1>Dashboard</h1>
        <button type="button" onClick={handleLogout}>
          logout
        </button>
      </div>
      
      <h2 style={{ textAlign: "left" }}>My Orders</h2>
      <button type="button" onClick={() => navigate("/bakeries")} style={{ marginBottom: "20px" }}>
        Browse Bakeries
      </button>

      {loading ? (
        <p>Loading orders...</p>
      ) : error ? (
        <p>{error}</p>
      ) : orders.length === 0 ? (
        <p>No orders found.</p>
      ) : (
        <table style={{ width: "33%", borderCollapse: "collapse", marginTop: "20px" }}>
          <thead>
            <tr style={{ backgroundColor: "#7992d6ff", borderBottom: "1px solid #ddddddff" }}>
              <th style={{ padding: "4px", textAlign: "center", color: "white" }}>Menu Item</th>
              <th style={{ padding: "4px", textAlign: "center", color: "white" }}>Quantity</th>
              <th style={{ padding: "4px", textAlign: "center", color: "white" }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((order) => (
              <tr key={order.order_id} style={{ borderBottom: "1px solid #ddd" }}>
                <td style={{ padding: "4px", textAlign: "center" }}>{order.menu_item}</td>
                <td style={{ padding: "4px", textAlign: "center" }}>{order.quantity}</td>
                <td style={{ padding: "4px", textAlign: "center" }}>{order.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default DashboardPage;

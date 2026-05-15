import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function DashboardPage() {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const role = localStorage.getItem("role");
  console.log("role: ", role);
  useEffect(() => {
    if (!token) {
      navigate("/");
    } else {
      if (role === "customer") {
        getMyOrders();
      } else if (role === "bakery_owner") {
        getIncomingOrders();
      } else {
        setError("Invalid user role");
        setLoading(false);
      }
    }
  }, [token, navigate, role]);

  if (!token) {
    return null;
  }

async function getIncomingOrders() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:8000/incoming-orders", {
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

  async function updateOrderStatus(orderId, newStatus) {
    try {
      const response = await fetch(`http://127.0.0.1:8000/orders/${orderId}/status`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ status: newStatus }),
      });

      if (!response.ok) {
        throw new Error("Could not update order status at the moment.");
      }

      if (role === "customer") {
        getMyOrders();
      } else if (role === "bakery_owner") {
        getIncomingOrders();
      }
    } catch (error) {
      console.error(error);
      setError("Could not update order status");
    }
  }

  async function handleLogout() {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    navigate("/");
  }

  return (
    <div style={{ padding: "40px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <h1>{role === "customer" ? "Customer Dashboard" : "Bakery Owner Dashboard"}</h1>
        <button type="button" onClick={handleLogout}>
          logout
        </button>
      </div>
      
      {role === "customer" ? (
        <>
          <h2>My Orders</h2>
          <button onClick={() => navigate("/bakeries")}>
            Browse Bakeries
          </button>
        </>
      ) : role === "bakery_owner" ? (
        <>
          <h2>Incoming Orders</h2>
          <button onClick={() => navigate("/manage-menu")}>
            Manage Menu
          </button>
        </>
        ) : (
          <p>Invalid user role</p>
      )}

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
              {role === "bakery_owner" && <th style={{ padding: "4px", textAlign: "center", color: "white" }}>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {orders.map((order) => (
              <tr key={order.order_id} style={{ borderBottom: "1px solid #ddd" }}>
                <td style={{ padding: "4px", textAlign: "center" }}>{order.menu_item}</td>
                <td style={{ padding: "4px", textAlign: "center" }}>{order.quantity}</td>
                <td style={{ padding: "4px", textAlign: "center" }}>{order.status}</td>
                {role === "bakery_owner" && (
                  <td style={{ padding: "4px", textAlign: "center" }}>
                    <select value={order.status} onChange={(e) => updateOrderStatus(order.order_id, e.target.value)} style={{ padding: "4px", border: "1px solid #26c47aff", borderRadius: "4px", fontSize: "14px" }}>
                      <option value="pending">Pending</option>
                      <option value="preparing">Preparing</option>
                      <option value="ready">Ready</option>
                      <option value="delivered">Delivered</option>
                    </select>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default DashboardPage;

import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import CurrencyWidget from "../components/CurrencyWidget";
import WeatherWidget from "../components/WeatherWidget";

function DashboardPage() {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const role = localStorage.getItem("role");
  const [bakery, setBakery] = useState(null);
  console.log("role: ", role);
  useEffect(() => {
    if (!token) {
      navigate("/");
    } else {
      if (role === "customer") {
        getMyOrders();
      } else if (role === "bakery_owner") {
        getIncomingOrders();
        getMyBakery();
      } else {
        setError("Invalid user role");
        setLoading(false);
      }
    }
  }, [token, navigate, role]);

  if (!token) {
    return null;
  }
  
async function getMyBakery() {
  try {
    const meResponse = await fetch("http://127.0.0.1:8000/me", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const me = await meResponse.json();

    const bakeryResponse = await fetch(`http://127.0.0.1:8000/bakeries-of-${me.id}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const bakeries = await bakeryResponse.json();

    if (bakeries.length > 0) {
      setBakery(bakeries[0]);
    }
  } catch (error) {
    console.error(error);
  }
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
    <div style={styles.page}>

    <div style={styles.container}>

      <div style={styles.widgetRow}>

        <CurrencyWidget />

        <WeatherWidget />

      </div>

      <div style={styles.header}>

        <h1 style={styles.title}>

          {role === "customer" ? "Customer Dashboard" : "Bakery Owner Dashboard"}

        </h1>

        <button type="button" onClick={handleLogout}>

          logout

        </button>

      </div>

      <div style={styles.section}>

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

            <button

              onClick={() => navigate(`/bakeries/${bakery.id}/manage-menu`)}

              disabled={!bakery}

            >

              Manage Menu

            </button>

          </>

        ) : (

          <p>Invalid user role</p>

        )}
      </div>

      {loading ? (
        <p>Loading orders...</p>
      ) : error ? (
        <p>{error}</p>
      ) : orders.length === 0 ? (
        <p>No orders found.</p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "20px" }}>
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
    </div>
  );
}
const styles = {
  page: {
    minHeight: "100vh",
    backgroundColor: "#17181f",
    color: "#f5f5f5",
    padding: "40px",
  },

  container: {
    maxWidth: "1100px",
    margin: "0 auto",
  },

  widgetRow: {
    display: "flex",
    gap: "20px",
    marginBottom: "40px",
    justifyContent: "flex-start",
    alignItems: "center",
  },

  header: {
    display: "flex",
    justifyContent: "space-between",
    marginBottom: "40px",
  },

  title: {
    fontSize: "42px",
    margin: 0,
  },

  section: {
    marginBottom: "24px",
  },
};
export default DashboardPage;

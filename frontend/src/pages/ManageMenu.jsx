import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

function ManageMenu() {
    const params = useParams();
    const bakeryId = params.bakery_id;
    const token = localStorage.getItem("token");
    console.log(params);
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [menuItems, setMenuItems] = useState([]);

    useEffect(() => {
        fetchMenuItems();
    }, []);

    async function fetchMenuItems() {
        setLoading(true);
        setError("");

        if (!bakeryId) {
            setError("Bakery ID not found.");
            setLoading(false);
            return;
        }

        try {
            const response = await fetch(`http://localhost:8000/bakeries/${bakeryId}/manage-menu`, {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error("Failed to load menu items");
            }

            const data = await response.json();
            setMenuItems(data);
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    }

    async function addMenuItem() {
        // This function will handle adding a new menu item
        // You can implement the logic to show a form for entering the new menu item details and send a POST request to the backend to create the menu item
    }
    
    async function editMenuItem(itemId) {
        // This function will handle editing an existing menu item
        // You can implement the logic to show a form pre-filled with the item's current details and send a PUT/PATCH request to the backend to update the menu item
    }

    async function deleteMenuItem(itemId) {
        // This function will handle deleting a menu item
        // You can implement the logic to send a DELETE request to the backend to remove the menu item
    }

  return (
    <>
      <div style={{ padding: "20px" }}>
        <h1>Manage Menu</h1>
      </div>
      {loading && <p>Loading menu items...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {!loading && !error && menuItems.length === 0 && (
        <p>No menu items found.</p>
      )}

      {!loading && !error && menuItems.length > 0 && (
        <div>
          <h2> Current Menu Items </h2>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Name</th>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Price</th>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {menuItems.map((item) => (
                  <tr key={item.id}>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>{item.name}</td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>${Number(item.price).toFixed(2)}</td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      <button onClick={() => editMenuItem(item.id)} style={{ marginRight: "10px" }}>Edit</button>
                      <button onClick={() => deleteMenuItem(item.id)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
        </div>
      )}
    </>
  );
}

export default ManageMenu;
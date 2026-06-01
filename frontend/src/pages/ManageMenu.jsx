import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

function ManageMenu() {
    const params = useParams();
    const bakeryId = params.bakery_id;
    const navigate = useNavigate();
    const token = localStorage.getItem("token");
    console.log(params);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [menuItems, setMenuItems] = useState([]);
    const [newItem, setNewItem] = useState({
        name: "",
        description: "",
        price: "",
    });
    const [editingItem, setEditingItem] = useState(null);

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

    async function addMenuItem(event) {
        event.preventDefault();
        setError("");

        if (!bakeryId) {
            setError("Bakery ID not found.");
            return;
        }

        try {
            const response = await fetch("http://localhost:8000/manage-menu", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({
                    bakery_id: Number(bakeryId),
                    name: newItem.name,
                    description: newItem.description,
                    price: Number(newItem.price)
                })
            });

            if (!response.ok) {
                throw new Error("Failed to add menu item");
            }

            setNewItem({
                name: "",
                description: "",
                price: "",
            });

            fetchMenuItems();
        } catch (error) {
            setError(error.message);
        }
    }
    
    function editMenuItem(item) {
        setEditingItem({
            id: item.id,
            name: item.name,
            description: item.description,
            price: item.price,
        });
    }

    async function saveEditedItem(event) {
        event.preventDefault();
        setError("");

        if (Number(editingItem.price) < 1 || Number.isNaN(Number(editingItem.price))) {
            setError("Price must be a number and at least 1.");
            return;
        }

        try {
            const response = await fetch(`http://localhost:8000/manage-menu?menu_item_id=${editingItem.id}`, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({
                    bakery_id: Number(bakeryId),
                    name: editingItem.name,
                    description: editingItem.description,
                    price: Number(editingItem.price)
                })
            });

            if (!response.ok) {
                throw new Error("Failed to update menu item");
            }

            setEditingItem(null);
            fetchMenuItems();
        } catch (error) {
            setError(error.message);
        }
    }

    async function deleteMenuItem(itemId) {
        setError("");

        const confirmed = window.confirm("Are you sure you want to delete this menu item?");
        if (!confirmed) return;

        try {
            const response = await fetch(`http://localhost:8000/manage-menu?menu_item_id=${itemId}`, {
                method: "DELETE",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error("Failed to delete menu item");
            }

            fetchMenuItems();
        } catch (error) {
            setError(error.message);
        }
    }

  return (
    <>
      <button
        onClick={() => navigate(-1)}
        style={{
          position: "absolute",
          top: "20px",
          left: "20px",
          fontSize: "28px",
          background: "none",
          border: "none",
          cursor: "pointer",
          padding: 0,
        }}
      >
        ←
      </button>

      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", paddingTop: "40px" }}>
        <h1>Manage Menu</h1>

          <form onSubmit={addMenuItem} style={{ display: "flex", flexDirection: "column", gap: "10px", width: "400px", marginTop: "20px" }}>
          <h2>Add Menu Item</h2>

          <input
            type="text"
            placeholder="Item name"
            value={newItem.name}
            onChange={(event) => setNewItem({ ...newItem, name: event.target.value })}
            required
          />

          <input
            type="text"
            placeholder="Description"
            value={newItem.description}
            onChange={(event) => setNewItem({ ...newItem, description: event.target.value })}
            required
          />

          <input
            type="number"
            placeholder="Price"
            value={newItem.price}
            onChange={(event) => setNewItem({ ...newItem, price: event.target.value })}
            required
            min="0"
            step="0.01"
          />

          <button type="submit">Add Menu Item</button>
        </form>
        {editingItem && (
          <form
            onSubmit={saveEditedItem}
            style={{ display: "flex", flexDirection: "column", gap: "10px", width: "400px", marginTop: "30px" }}
          >
            <h2>Edit Menu Item</h2>

            <input
              type="text"
              value={editingItem.name}
              onChange={(event) => setEditingItem({ ...editingItem, name: event.target.value })}
              required
            />

            <input
              type="text"
              value={editingItem.description}
              onChange={(event) => setEditingItem({ ...editingItem, description: event.target.value })}
              required
            />

            <input
              type="number"
              value={editingItem.price}
              onChange={(event) => setEditingItem({ ...editingItem, price: event.target.value })}
              required
              min="1"
              step="0.01"
            />

            <div>
              <button type="submit" style={{ marginRight: "10px" }}>Save</button>
              <button type="button" onClick={() => setEditingItem(null)}>Cancel</button>
            </div>
          </form>
        )}
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
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Description</th>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Price</th>
                  <th style={{ border: "1px solid #ddd", padding: "8px" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {menuItems.map((item) => (
                  <tr key={item.id}>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>{item.name}</td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>{item.description}</td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>${Number(item.price).toFixed(2)}</td>
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                      <button onClick={() => editMenuItem(item)} style={{ marginRight: "10px" }}>Edit</button>
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
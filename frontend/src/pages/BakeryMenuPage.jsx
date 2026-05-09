import { useEffect, useState } from "react";
import { useNavigate , useParams} from "react-router-dom";


function BakeryMenuPage() {
  const navigate = useNavigate();
  const params = useParams();
  // console.log(params);
  const bakery_id = params.bakery_id 
  const [menuItems, setMenuItems] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [orderMessage, setOrderMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const token = localStorage.getItem("token");

  useEffect(() => {
      if (!token) {
        navigate("/");
      } else {
        getMenuOfBakery(bakery_id);
      }
    }, [token, navigate, bakery_id]);
  
    if (!token) {
      return null;
    }

  async function getMenuOfBakery() {
    setLoading(true);
    setError("");

    if (!bakery_id) {
      setError("Bakery ID is missing from the URL");
      setLoading(false);
      return;
    }


    try {
      const response = await fetch(`http://127.0.0.1:8000/bakeries/${bakery_id}/menu-items`);

      if (!response.ok) {
        throw new Error("Could not load the menu of this bakery at the moment.");
      }

      const data = await response.json();
      setMenuItems(data);
    } catch (error) {
      console.error(error);
      setError("Could not load the menu of this bakery");
    } finally {
      setLoading(false);
    }
  }

  async function handleOrder() {
    if (!selectedItem) {
      setOrderMessage("Please select a menu item to order.");
      return;
    }
    
    if (quantity < 1) {
      setOrderMessage("Quantity must be at least 1.");
      return;
    }
    console.log("Ordering item:", selectedItem);
    console.log("id of item:", selectedItem.id);

    try {
      const response = await fetch("http://127.0.0.1:8000/orders", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          bakery_id: bakery_id,
          menu_item_id: selectedItem.id,
          quantity: quantity,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        console.log("Order response:", data);
        setOrderMessage("Order placed successfully!");
      } else {
        setOrderMessage(data.detail || "Unknown error");
      }
    } catch (error) {
      console.error(error);
      setOrderMessage("Failed to place order");
      navigate("/dashboard");
    }
  }

return (
    <div style={{ padding: "40px" }}>
        <h1>Menu</h1>
        <button type="button" onClick={() => navigate("/bakeries")} style={{ marginBottom: "5px", padding: "10px 15px", backgroundColor: "#007bff", color: "#fff", border: "none", borderRadius: "5px", cursor: "pointer" }}>
            Back to Bakeries
        </button>

        {loading ? (
            <p>Loading menu...</p>
        ) : error ? (
            <p>{error}</p>
        ) : menuItems.length === 0 ? (
            <p>No menu items found for this bakery.</p>
        ) : (
            <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "5px" }}>
                <thead>
                    <tr style={{ backgroundColor: "#f0f0f0", borderBottom: "2px solid #333" }}>
                        <th style={{ padding: "12px", textAlign: "center" }}>Name</th>
                        <th style={{ padding: "12px", textAlign: "center" }}>Description</th>
                        <th style={{ padding: "12px", textAlign: "center" }}>Price</th>
                        <th style={{ padding: "12px", textAlign: "center" }}>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {menuItems.map((item) => (
                        <tr key={item.id} style={{ borderBottom: "1px solid #ddd" }}>
                            <td style={{ padding: "12px" }}>{item.name}</td>
                            <td style={{ padding: "12px" }}>{item.description}</td>
                            <td style={{ padding: "12px", textAlign: "center" }}>${item.price}</td>
                            <td style={{ padding: "12px", textAlign: "center" }}>
                                <button type="button" onClick={() => setSelectedItem(item)} style={{ padding: "5px 10px", backgroundColor: "#28a745", color: "#fff", border: "none", borderRadius: "5px", cursor: "pointer" }}>
                                    View Details
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        )}

        {selectedItem && (
            <div style={{ marginTop: "30px", padding: "20px", border: "1px solid #ddd", borderRadius: "8px" }}>
                <h2>{selectedItem.name}</h2>
                <p><strong>Description:</strong> {selectedItem.description}</p>
                <p><strong>Price:</strong> ${selectedItem.price}</p>

                <label>
                    Quantity: {" "}
                    <input
                        type="number"
                        min="1"
                        value={quantity}
                        onChange={(e) => setQuantity(Number(e.target.value))}
                        style={{ width: "60px", padding: "5px" }}
                    />
                </label>

                <br />
                <br />

                <button type="button" onClick={handleOrder} style={{ padding: "10px 15px", backgroundColor: "#ffc107", color: "#000", border: "none", borderRadius: "5px", cursor: "pointer" }}>
                    Order
                </button>

                <p style={{ marginTop: "10px" }}>{orderMessage}</p>
            </div>
        )}
    </div>
);
}

export default BakeryMenuPage;
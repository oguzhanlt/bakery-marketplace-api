import { useEffect, useState } from "react";
import { useNavigate , useParams} from "react-router-dom";


function BakeryMenuPage() {
  const navigate = useNavigate();
  const params = useParams();
  // console.log(params);
  const bakery_id = params.bakery_id 
  const [menuItems, setMenuItems] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
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

                <button type="button" style={{ padding: "10px 15px", backgroundColor: "#ffc107", color: "#000", border: "none", borderRadius: "5px", cursor: "pointer" }}>
                    Order
                </button>
            </div>
        )}
    </div>
);
}

export default BakeryMenuPage;
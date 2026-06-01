import {useEffect, useState }  from "react";
import { useNavigate } from "react-router-dom";



function BakeriesPage() {
  const navigate = useNavigate();
  const [bakeries, setBakeries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const token = localStorage.getItem("token");

  useEffect(() => {
      if (!token) {
        navigate("/");
      } else {
        getBakeries();
      }
    }, [token, navigate]);
  
    if (!token) {
      return null;
    }
  

  async function getBakeries() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:8000/bakeries");

      if (!response.ok) {
        throw new Error("Could not load bakeries at the moment.");
      }

      const data = await response.json();
      setBakeries(data);
    } catch (error) {
      console.error(error);
      setError("Could not load bakeries");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style ={{ padding: "40px" }}>
      <h1>Bakeries</h1>

      <button type="button" onClick={() => navigate("/dashboard")} style={{ marginBottom: "20px" }}>
        Back to Dashboard
      </button>

      {loading ? (
        <p>Loading bakeries...</p>
      ) : error ? (
        <p>{error}</p>
      ) : bakeries.length === 0 ? (
        <p>No bakeries found.</p>
      ) : (
        <ul>
          {bakeries.map((bakery) => (
            <li key={bakery.id}>
                <h3>{bakery.name}</h3>
                <p>{bakery.location}</p>
                <p>{bakery.description}</p>

                <button type="button" onClick={() => navigate(`/bakeries/${bakery.id}/menu-items`)}>
                    View Menu
                </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default BakeriesPage;
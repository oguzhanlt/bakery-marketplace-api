import { useState } from "react";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  async function handleLogin(e) {
    e.preventDefault();

    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    const response = await fetch("http://127.0.0.1:8000/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData,
    });
    console.log("clicked");

    const data = await response.json();

    console.log(data);

    if (data.access_token) {
      localStorage.setItem("token", data.access_token);
      setMessage("Login successful");
    } else {
      setMessage("Login failed");
    }
  }

  return (
    <div style={{ padding: "40px" }}>
      <h1>Bakery App Login</h1>

      <form onSubmit={handleLogin}>
        <input
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <br /><br />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <br /><br />

        <button type="submit">Login</button>

        <p>{message}</p>

        <button type="button" onClick={getMyOrders}>
          Get My Orders
        </button>
      </form>
    </div>
  );


  async function getMyOrders() {
  const token = localStorage.getItem("token");

  const response = await fetch("http://127.0.0.1:8000/my-orders", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  const data = await response.json();

  console.log(data);
}
}

export default App;
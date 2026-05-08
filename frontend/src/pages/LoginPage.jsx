import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const navigate = useNavigate();

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
      navigate("/dashboard");
    } else {
      setMessage("Login failed");
    }
  }

  return (
    <div style={{ padding: "40px" }}>
      <h1>BakeUp</h1>

      <form onSubmit={handleLogin}>
        <input
          placeholder="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <br /><br />

        <input
          type="password"
          placeholder="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <br /><br />

        <button 
          type="submit"
          style={{
            padding: "5px 10px",
            backgroundColor: "#007bff",
            color: "white",
            border: "none",
            borderRadius: "5px",
            cursor: "pointer",
            fontSize: "16px",
            fontWeight: "bold",
            transition: "transform 0.1s",
          }}
          onMouseDown={() => {
            document.getElementById("login-button").style.transform = "scale(0.95)";
          }}
          onMouseUp={() => {
            const btn = document.getElementById("login-button");
            btn.style.transition = "transform 0.2s ease-out";
            btn.style.transform = "scale(1.05)";
            setTimeout(() => {
              btn.style.transform = "scale(1)";
            }, 200);
          }}
          id="login-button"
        >
          login
        </button>

        <button 
          type="button"
          style={{
            padding: "5px 10px",
            backgroundColor: "#007bff",
            color: "white",
            border: "none",
            borderRadius: "5px",
            cursor: "pointer",
            fontSize: "16px",
            fontWeight: "bold",
            transition: "transform 0.1s",
          }}
          onMouseDown={() => {
            document.getElementById("register-button").style.transform = "scale(0.95)";
          }}
          onMouseUp={() => {
            const btn = document.getElementById("register-button");
            btn.style.transition = "transform 0.2s ease-out";
            btn.style.transform = "scale(1.05)";
            setTimeout(() => {
              btn.style.transform = "scale(1)";
              navigate("/register");
            }, 200);
          }}
          id="register-button"
        >
          register
        </button>

        <p>{message}</p>
      </form>
    </div>
  )

}

export default LoginPage;

import { useState } from "react";
import { useNavigate } from "react-router-dom";

function RegisterPage() {
    const navigate = useNavigate();
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [role, setRole] = useState("customer");
    const [message, setMessage] = useState("");


    async function handleRegister(e) {
        e.preventDefault()
        if (!username.trim() || !email.trim() || !password.trim() || !confirmPassword.trim()) {
            setMessage("Please fill in all fields");
            return;
        }

        if (!email.includes("@")) {
            setMessage("Please enter a valid email address");
            return;
        }

        if (password.length < 4) {
            setMessage("Password must be at least 4 characters long");
            return;
        }

        if (password !== confirmPassword) {
            setMessage("Passwords do not match");
            return;
        }
        try {
            const response = await fetch("http://127.0.0.1:8000/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    username,
                    email,
                    password,
                    role,
                }),
            });

            const data = await response.json();

            if (response.ok) {
                setMessage("Registration successful");
                navigate("/");
            } else {
                setMessage(data.detail || "Unknown error");
            }
        } catch (error) {
            setMessage("Registration request failed");
        }
    }
  return (
    <div>
        <h1>Registration to BakeUp</h1>
        <form onSubmit={handleRegister}>
         <input
          placeholder="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style ={{
            padding: "5px",
            border: "1px solid #26c47aff",
            borderRadius: "4px",
            fontSize: "16px",
            width: "200px",
          }}
        />

        <br /><br />

        <input
          placeholder="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style ={{
            padding: "5px",
            border: "1px solid #26c47aff",
            borderRadius: "4px",
            fontSize: "16px",
            width: "200px",
          }}
        />

        <br /><br />

        <input
          type="password"
          placeholder="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style ={{
            padding: "5px",
            border: "1px solid #26c47aff",
            borderRadius: "4px",
            fontSize: "16px",
            width: "200px",
          }}
        />

        <br /><br />

        <input
          type="password"
          placeholder="confirm password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          style ={{
            padding: "5px",
            border: "1px solid #26c47aff",
            borderRadius: "4px",
            fontSize: "16px",
            width: "200px",
          }}
         />

        <br /><br />

            <select value={role} onChange={(e) => setRole(e.target.value)} style={{ padding: "5px", border: "1px solid #26c47aff", borderRadius: "4px", fontSize: "16px", width: "210px" }}>
                <option value="customer">Customer</option>
                <option value="bakery_owner">Bakery Owner</option>
            </select>

        <br /><br />

        <button type="submit" style={{
          padding: "10px 20px",
          backgroundColor: "#26c47aff",
          color: "white",
          border: "none",
          borderRadius: "4px",
          fontSize: "16px",
          cursor: "pointer",
        }}>
          Register
        </button>

        <p>{message}</p>
    </form>
    </div>
  );    
}

export default RegisterPage;
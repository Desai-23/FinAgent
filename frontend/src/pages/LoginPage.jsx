import { useState } from "react";
import { loginUser } from "../api/auth";
import { useAuth } from "../context/AuthContext";

export default function LoginPage({ onSwitchToRegister }) {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await loginUser({ email, password });
      login(data.access_token, data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "#0f1117",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      fontFamily: "'DM Sans', sans-serif",
    }}>
      <div style={{
        background: "#1a1d27",
        border: "1px solid #2a2d3a",
        borderRadius: "16px",
        padding: "48px",
        width: "100%",
        maxWidth: "420px",
      }}>

        {/* Logo */}
        <div style={{ textAlign: "center", marginBottom: "32px" }}>
          <div style={{
            width: "48px", height: "48px",
            background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
            borderRadius: "12px",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "24px", margin: "0 auto 16px",
          }}>🏦</div>
          <h1 style={{ color: "#fff", fontSize: "24px", fontWeight: "700", margin: 0 }}>
            Welcome back
          </h1>
          <p style={{ color: "#6b7280", fontSize: "14px", marginTop: "8px" }}>
            Sign in to your FinAgent account
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: "16px" }}>
            <label style={{ color: "#9ca3af", fontSize: "13px", display: "block", marginBottom: "6px" }}>
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="you@example.com"
              style={{
                width: "100%", padding: "10px 14px",
                background: "#0f1117", border: "1px solid #2a2d3a",
                borderRadius: "8px", color: "#fff", fontSize: "14px",
                outline: "none", boxSizing: "border-box",
              }}
            />
          </div>

          <div style={{ marginBottom: "24px" }}>
            <label style={{ color: "#9ca3af", fontSize: "13px", display: "block", marginBottom: "6px" }}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="••••••••"
              style={{
                width: "100%", padding: "10px 14px",
                background: "#0f1117", border: "1px solid #2a2d3a",
                borderRadius: "8px", color: "#fff", fontSize: "14px",
                outline: "none", boxSizing: "border-box",
              }}
            />
          </div>

          {error && (
            <div style={{
              background: "#2d1b1b", border: "1px solid #7f1d1d",
              borderRadius: "8px", padding: "10px 14px",
              color: "#fca5a5", fontSize: "13px", marginBottom: "16px",
            }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: "100%", padding: "11px",
              background: loading ? "#4c4f6b" : "linear-gradient(135deg, #6366f1, #8b5cf6)",
              border: "none", borderRadius: "8px",
              color: "#fff", fontSize: "15px", fontWeight: "600",
              cursor: loading ? "not-allowed" : "pointer",
            }}
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <p style={{ color: "#6b7280", fontSize: "13px", textAlign: "center", marginTop: "24px" }}>
          Don't have an account?{" "}
          <span
            onClick={onSwitchToRegister}
            style={{ color: "#818cf8", cursor: "pointer", fontWeight: "600" }}
          >
            Create one
          </span>
        </p>
      </div>
    </div>
  );
}


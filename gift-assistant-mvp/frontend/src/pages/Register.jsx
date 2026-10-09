import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";

export default function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: ""
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const onChange = (e) => {
    setForm((prev) => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await api.register(form);
      navigate("/login");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <form className="card form-card" onSubmit={onSubmit}>
        <h1>Регистрация</h1>

        <label>Имя</label>
        <input
          type="text"
          name="name"
          value={form.name}
          onChange={onChange}
          required
        />

        <label>Email</label>
        <input
          type="email"
          name="email"
          value={form.email}
          onChange={onChange}
          required
        />

        <label>Пароль</label>
        <input
          type="password"
          name="password"
          value={form.password}
          onChange={onChange}
          required
          minLength={6}
        />

        {error && <div className="error">{error}</div>}

        <button className="btn btn-primary" disabled={loading}>
          {loading ? "Сохраняем..." : "Зарегистрироваться"}
        </button>

        <p className="muted center">
          Уже есть аккаунт? <Link to="/login">Войти</Link>
        </p>
      </form>
    </div>
  );
}
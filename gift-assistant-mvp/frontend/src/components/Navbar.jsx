import { Link, useNavigate } from "react-router-dom";
import { clearToken, getToken } from "../api/client";

export default function Navbar() {
  const navigate = useNavigate();
  const isAuth = !!getToken();

  const handleLogout = () => {
    clearToken();
    navigate("/login");
  };

  return (
    <nav className="navbar">
      <div className="navbar__inner">
        <Link to={isAuth ? "/dashboard" : "/"} className="logo">
          Gift Assistant
        </Link>

        <div className="nav-links">
          {isAuth ? (
            <>
              <Link to="/dashboard" className="nav-link">
                Кабинет
              </Link>
              <Link to="/recipients/new" className="nav-link">
                Новый получатель
              </Link>
              <button className="btn btn-secondary" onClick={handleLogout}>
                Выйти
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-link">
                Вход
              </Link>
              <Link to="/register" className="btn btn-primary">
                Регистрация
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
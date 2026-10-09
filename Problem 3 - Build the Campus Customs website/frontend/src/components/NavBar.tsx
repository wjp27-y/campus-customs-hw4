import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import PointsTracker from "../fun/PointsTracker";

const linkClass = ({ isActive }: { isActive: boolean }) => `nav-link${isActive ? " active" : ""}`;

export default function NavBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <nav className="nav">
      <Link to="/" className="nav-brand">
        Campus Customs
      </Link>
      <div className="nav-links">
        <NavLink to="/" end className={linkClass}>
          Home
        </NavLink>
        <NavLink to="/products" className={linkClass}>
          Products
        </NavLink>
        <NavLink to="/about" className={linkClass}>
          About Us
        </NavLink>
      </div>
      <PointsTracker />
      <div className="nav-account">
        {user ? (
          <>
            <span className="nav-user">Hi, {user.first_name || user.name}</span>
            <button type="button" className="nav-link nav-logout" onClick={() => logout().then(() => navigate("/"))}>
              Log out
            </button>
          </>
        ) : (
          <>
            <NavLink to="/login" className={linkClass}>
              Log in
            </NavLink>
            <NavLink to="/register" className={({ isActive }) => `${linkClass({ isActive })} nav-cta`}>
              Create account
            </NavLink>
          </>
        )}
      </div>
    </nav>
  );
}

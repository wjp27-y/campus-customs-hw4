import { Route, Routes } from "react-router-dom";
import NavBar from "./components/NavBar";
import ChatWidget from "./components/ChatWidget";
import Mentors from "./fun/Mentors";
import { RewardToast } from "./fun/PointsTracker";
import Spiders from "./fun/Spiders";
import Home from "./pages/Home";
import Products from "./pages/Products";
import ProductPage from "./pages/ProductPage";
import About from "./pages/About";
import Login from "./pages/Login";
import Register from "./pages/Register";

export default function App() {
  return (
    <>
      <NavBar />
      <main className="page">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Products />} />
          <Route path="/products/:productId" element={<ProductPage />} />
          <Route path="/about" element={<About />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="*" element={<p>Page not found.</p>} />
        </Routes>
      </main>
      <footer className="footer">
        Campus Customs · 57 Broadway, New Haven, CT 06511 · Officially licensed Yale merchandise
      </footer>
      <Spiders />
      <Mentors />
      <RewardToast />
      <ChatWidget />
    </>
  );
}

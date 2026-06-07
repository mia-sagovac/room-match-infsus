import { Routes, Route, Navigate, NavLink, Link, useNavigate } from "react-router-dom";
import logo from "./logo.svg";
import iconUser from "./pages/icons/user.svg";
import iconClipboard from "./pages/icons/clipboard.svg";
import iconHands from "./pages/icons/hands.svg";
import iconChats from "./pages/icons/chats.svg";
import iconHouse from "./pages/icons/house.svg";
import iconQuestion from "./pages/icons/question.svg";
import iconPoll from "./pages/icons/poll.svg";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Profile from "./pages/Profile.jsx";
import Questionnaire from "./pages/Questionnaire.jsx";
import Matches from "./pages/Matches.jsx";
import Chat from "./pages/Chat.jsx";
import Ads from "./pages/Ads.jsx";
import Pitanja from "./pages/Pitanja.jsx";
import UpitnikAdmin from "./pages/UpitnikAdmin.jsx";
import Privacy from "./pages/Privacy.jsx";
import Help from "./pages/Help.jsx";
import Footer from "./pages/components/Footer.jsx";
import ProcessView from "./pages/ProcessView.jsx";

function isAuthed() {
  return !!localStorage.getItem("token");
}

function Protected({ children }) {
  return isAuthed() ? children : <Navigate to="/login" replace />;
}

function Nav() {
  const navigate = useNavigate();
  if (!isAuthed()) return null;

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("korisnik");
    navigate("/");
  };

  const items = [
    { to: "/profile", label: "Profil", icon: iconUser },
    { to: "/questionnaire", label: "Upitnik", icon: iconClipboard },
    { to: "/matches", label: "Cimeri", icon: iconHands },
    { to: "/chat", label: "Razgovori", icon: iconChats },
      { to: "/ads", label: "Oglasi", icon: iconHouse },
      { to: "/pitanja", label: "Pitanja", icon: iconQuestion },
      { to: "/upitnici-admin", label: "Upitnici", icon: iconPoll },
  ];

  return (
    <nav className="nav">
      <div className="nav-brand">
        <img src={logo} alt="RoomMatch logo" className="nav-logo" />
        <span>RoomMatch</span>
      </div>
      <div className="nav-left">
        
        <div className="nav-icons">
          {items.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `nav-icon${isActive ? " active" : ""}`}
              title={item.label}
            >
              <img src={item.icon} alt="" className="nav-icon-svg" aria-hidden="true" />
            <span className="nav-label">{item.label}</span>
            </NavLink>
          ))}
        </div>
      </div>
      <button className="secondary" onClick={logout}>Odjava</button>
    </nav>
  );
}

// glavna ulazna stranica
function HomePage() {
  return (
    <main className="hero">
      <div className="hero-top">
        <Link to="/login" className="button button-primary hero-login">Prijava</Link>
      </div>
      <div className="hero-content">
        <img src={logo} alt="RoomMatch logo" className="hero-logo" />
        <h1 className="hero-title">
          <span className="hero-title-room">Room</span>{" "}
          <span className="hero-title-match">Match</span>
        </h1>
        <p className="hero-subtitle">Find your room. Find your people.</p>
      </div>
    </main>
  );
}

export default function App() {
  return (
    <>
      <Nav />
      <div className="page">
      <div className="container">
        <Routes>
          <Route path="/" element={isAuthed() ? <Navigate to="/profile" replace /> : <HomePage />} />
          <Route path="/login" element={isAuthed() ? <Navigate to="/profile" replace /> : <Login />} />
          <Route path="/register" element={isAuthed() ? <Navigate to="/profile" replace /> : <Register />} />
          <Route path="/profile" element={<Protected><Profile /></Protected>} />
          <Route path="/questionnaire" element={<Protected><Questionnaire /></Protected>} />
          <Route path="/matches" element={<Protected><Matches /></Protected>} />
          <Route path="/chat" element={<Protected><Chat /></Protected>} />
          <Route path="/chat/:razgovorId" element={<Protected><Chat /></Protected>} />
          <Route path="/ads" element={<Protected><Ads /></Protected>} />
            <Route path="/pitanja" element={<Protected><Pitanja /></Protected>} />
            <Route path="/upitnici-admin" element={<Protected><UpitnikAdmin /></Protected>} />
          <Route path="/proces" element={<Protected><ProcessView /></Protected>} />
          <Route path="/privacy" element={<Privacy />} />
          <Route path="/help" element={<Help />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        
      </div>
      <Footer />
      </div>
    </>
  );
}

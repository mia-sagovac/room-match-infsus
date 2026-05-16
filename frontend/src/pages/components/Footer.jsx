import { Link } from "react-router-dom";

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-section">
          <h4>O nama</h4>
          <p>RoomMatch vam pomaže da pronađete idealne cimere i sobe na osnovu zajedničkih interesa i kompatibilnosti.</p>
        </div>

        <div className="footer-section">
          <h4>Linkovi</h4>
          <ul>
            <li><Link to="/privacy">Privatnost</Link></li>
            <li><Link to="/help">Pomoć</Link></li>
          </ul>
        </div>

        <div className="footer-section">
          <h4>Kontakt</h4>
          <ul>
            <li>Email: <a href="mailto:info@roommatch.hr">info@roommatch.hr</a></li>
            <li>Tel: <a href="tel:+385011234567">+385 01 123 4567</a></li>
          </ul>
        </div>

      </div>

      <div className="footer-bottom">
        <p>&copy; {currentYear} RoomMatch. Sva prava pridržana.</p>
      </div>
    </footer>
  );
}

export default function Help() {
  return (
    <main className="content-page">
      <div className="content-header">
        <h1>Pomoć i Podrška</h1>
        <p className="content-subtitle">Odgovori na česta pitanja</p>
      </div>

      <div className="content-body">
        <section className="content-section">
          <h2>Kako početi?</h2>
          <div className="faq-item">
            <h3>Kako se registriram na RoomMatch?</h3>
            <p>
              Kliknite na "Registracija" na početnoj stranici, unesite svoje osnovne podatke (ime, prezime, email i lozinku), 
              a zatim tip korisnika. Nakon toga možete se prijaviti i početiti sa popunjavanjem vašeg profila.
            </p>
          </div>

          <div className="faq-item">
            <h3>Što je obavezno za profil?</h3>
            <p>
              Za početak, obavezni su: kratko o meni, lokacija i osnovne preferencije. 
              Što više detalja unesete, veće su šanse da pronađete kompatibilnog cimera.
            </p>
          </div>
        </section>

        <section className="content-section">
          <h2>Pronalaženje cimera</h2>
          <div className="faq-item">
            <h3>Kako funkcionira algoritam kompatibilnosti?</h3>
            <p>
              Naš algoritam analizira vaše odgovore na upitnik i uspoređuje ih sa odgovorima ostalih korisnika. 
              Uzimamo u obzir životni stil, rutine, budžet, interese i druga važna pitanja. 
              Korisnici sa visokom kompatibilnosti se preporučuju jedni drugima.
            </p>
          </div>

          <div className="faq-item">
            <h3>Mogu li filtrirati po lokaciji?</h3>
            <p>
              Da! Na stranici "Oglasi" možete filtrirati oglase po lokaciji, cijeni i ostalim kriterijima. 
              Također, možete postaviti željenu lokaciju u svom profilu da bi dobili preporuke za taj grad.
            </p>
          </div>

          <div className="faq-item">
            <h3>Što znači "Cimeri" sekcija?</h3>
            <p>
              "Cimeri" sekcija prikazuje korisnike sa visokim stupnjem kompatibilnosti s vama. 
              Možete pregledati njihov profil i odlučiti jeste li zainteresirani te ih kontaktirati.
            </p>
          </div>
        </section>

        <section className="content-section">
          <h2>Komunikacija</h2>
          <div className="faq-item">
            <h3>Kako mogu poslati poruku drugom korisniku?</h3>
            <p>
              Otvorite profil korisnika koji vas zanima i kliknite na gumb "Pošalji poruku" ili "Zatraži razgovor". 
              Razgovor će biti otvoren u sekciji "Razgovori" gdje možete slati i primati poruke u realnom vremenu.
            </p>
          </div>

          <div className="faq-item">
            <h3>Mogu li da izbrisati razgovor?</h3>
            <p>
              Da, možete izbrisati razgovor klikom na gumb za brisanje. Napomena: brisanje je trajno 
              i ne možete kasnije pristupiti tom razgovoru.
            </p>
          </div>

          <div className="faq-item">
            <h3>Jesu li moje poruke privatne?</h3>
            <p>
              Da, potpuno privatne! Samo vi i osoba sa kojom razgovarate možete da vidite poruke. 
              Mi nikada ne pristupamo sadržaju vaših privatnih poruka.
            </p>
          </div>
        </section>

        <section className="content-section">
          <h2>Profil i Sigurnost</h2>
          <div className="faq-item">
            <h3>Kako mogu ažurirati svoj profil?</h3>
            <p>
              Idite na "Profil" stranicu gdje možete izmjeniti sve svoje podatke, 
              opis i preferencije. Sve izmjene se čuvaju automatski.
            </p>
          </div>

          <div className="faq-item">
            <h3>Kako prijaviti sumnjiv profil ili neprimjernu poruku?</h3>
            <p>
              Javite nam se na mail ili broj telefona.
            </p>
          </div>
        </section>

        <section className="content-section">
          <h2>Ostalo</h2>
          <div className="faq-item">
            <h3>Koliko stoji korištenje RoomMatch-a?</h3>
            <p>
              Osnovne funkcionalnosti su potpuno besplatne. 
              Planiramo premium opcije u budućnosti, ali će osnovne sveobuhvatne mogućnosti ostati besplatne.
            </p>
          </div>

          <div className="faq-item">
            <h3>Gdje mogu dobiti dodatnu pomoć?</h3>
            <p>
              Ako ne pronađete odgovor na svoje pitanje, slobodno nas kontaktirajte:
            </p>
            <ul>
              <li><strong>Email:</strong> <a href="mailto:support@roommatch.hr">support@roommatch.hr</a></li>
              <li><strong>Telefon:</strong> <a href="tel:+381111234567">+385 01 123 4567</a></li>
            </ul>
          </div>

          <div className="faq-item">
            <h3>Mogu li da predam sugestiju za novu funkcionalnost?</h3>
            <p>
              Apsolutno! Voljeli bismo da čujemo vaše sugestije. Kontaktirajte nas na 
              <a href="mailto:feedback@roommatch.hr"> feedback@roommatch.hr</a> sa vašim idejama.
            </p>
          </div>
        </section>
      </div>
    </main>
  );
}

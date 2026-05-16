export default function Privacy() {
  return (
    <main className="content-page">
      <div className="content-header">
        <h1>Politika Privatnosti</h1>
        <p className="content-subtitle">Kako štitimo vaše podatke</p>
      </div>

      <div className="content-body">

        <section className="content-section">
          <h2>1. Podatci koje prikupljamo</h2>
          <p>Prikupljamo slijedeće vrste podataka:</p>
          <ul>
            <li><strong>Podaci za prijavu:</strong> Ime, prezime, email i lozinka</li>
            <li><strong>Profil podatci:</strong> Opis, lokacija i preferencije</li>
            <li><strong>Upitnik podatci:</strong> Odgovori na pitanja kompatibilnosti</li>
            <li><strong>Komunikacijski podatci:</strong> Poruke i razgovori sa drugim korisnicima</li>
          </ul>
        </section>

        <section className="content-section">
          <h2>2. Kako koristimo vaše podatke</h2>
          <p>Vaše podatke koristimo isključivo za:</p>
          <ul>
            <li>Pružanje usluge pronalaženja kompatibilnih cimera</li>
            <li>Omogućavanje komunikacije između korisnika</li>
            <li>Poboljšanje kvalitete platforme na osnovu povratnih informacija</li>
            <li>Zaštitu od zloupotrebe i prijevare</li>
          </ul>
        </section>

        <section className="content-section">
          <h2>3. Zaštita podataka</h2>
          <p>
            Primjenjujemo višeslojne mjere sigurnosti kako bismo zaštitili vaše podatke:
          </p>
          <ul>
            <li>Sigurno čuvanje lozinki</li>
            <li>Pristup podatcima samo ovlaštenim osobama</li>
            <li>Redovne provjere sigurnosti i ažuriranja</li>
          </ul>
        </section>

        <section className="content-section">
          <h2>4. Dijeljenje podataka</h2>
          <p>
            <strong>Nikada ne dijelimo vaše podatke sa trećim stranama</strong> bez vašeg izričitog pristanka, osim kada to zahtjevaju zakoni.
          </p>
          <p>
            Vaši podaci se koriste isključivo na platformi RoomMatch i nisu dostupni vanjskim partnerima, oglašivačima ili drugim servisima.
          </p>
        </section>

        <section className="content-section">
          <h2>5. Vaša prava</h2>
          <p>Imate pravo da:</p>
          <ul>
            <li>Pristupite svim vašim osobnim podatcima</li>
            <li>Ispravite netočne podatke</li>
            <li>Obrišete vaš profil i sve povezane podatke</li>
            <li>Dobijete izvoz vaših podataka u čitljivom formatu</li>
          </ul>
        </section>

        <section className="content-section">
          <h2>6. Kontakt</h2>
          <p>
            Ako imate pitanja o privatnosti ili želite da ostvarite neka od gore navedenih prava, kontaktirajte nas na:
          </p>
          <p>
            <strong>Email:</strong> <a href="mailto:privacy@roommatch.hr">privacy@roommatch.hr</a>
          </p>
          <p>
            <strong>Telefon:</strong> <a href="tel:+385011234567">+385 01 123 4567</a>
          </p>
        </section>

        <section className="content-section">
          <h2>7. Promjene politike</h2>
          <p>
            Zadržavamo pravo na ažuriranje ove politike privatnosti. O značajnim promjenama obavjestit ćemo sve korisnike putem emaila.
          </p>
          <p>
            Posljednja ažuriranja: <strong>Svibanj 2026.</strong>
          </p>
        </section>
      </div>
    </main>
  );
}

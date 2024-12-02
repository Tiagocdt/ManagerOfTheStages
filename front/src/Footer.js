import React from 'react';
import './Footer.css'; // Create a CSS file for styling

const Footer = () => {
  return (
    <footer className="app-footer">
      <p>
        References:
        <br />
        [1] Iwamatsu, T. (2004). Stages of normal development in the medaka Oryzias latipes. Mech Dev, 121(7-8), 605-618. https://doi.org/10.1016/j.mod.2004.03.012
        <br />
        [2] Yamamoto, T. (1975). Medaka (killifish): Biology and strains. Yugaku-sha: Distributed by Keigaku Pub. Co.
      </p>
    </footer>
  );
};

export default Footer;
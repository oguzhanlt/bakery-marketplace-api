import { useEffect, useState } from "react";

const styles = {
  container: {
    backgroundColor: "#ffffff",
    padding: "16px",
    borderRadius: "14px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
    width: "260px",
    height: "170px",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
  },
  title: {
    marginBottom: "14px",
    color: "#222",
    textAlign: "center",
    fontSize: "28px",
  },
  rateCard: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "8px",
    marginBottom: "10px",
  },
  flag: {
    fontSize: "24px",
  },
  rate: {
    margin: "0",
    color: "#222",
  },
};

function CurrencyWidget() {
  const [rates, setRates] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/external/currency")
      .then((response) => response.json())
      .then((data) => {
        setRates(data);
      });
  }, []);

  if (!rates) {
    return <p>Loading currency rates...</p>;
  }

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Currency Rates</h2>

      <div style={styles.rateCard}>
        <span style={styles.flag}>🇪🇺</span>
        <p style={styles.rate}>1 EUR = <strong>{rates.usd}</strong> USD 🇺🇸</p>
      </div>
      <div style={styles.rateCard}>
        <span style={styles.flag}>🇪🇺</span>
        <p style={styles.rate}>1 EUR = <strong>{rates.try}</strong> TRY 🇹🇷</p>
      </div>
    </div>
  );
}

export default CurrencyWidget;
// frontend/transactions.js
async function fetchTransactions() {
  const res = await fetch("GOOGLE_SHEET_PUBLISHED_JSON_URL");
  const data = await res.json();

  let total = 0;
  const rows = data.values.slice(1);
  const list = rows.map(row => {
    total += parseFloat(row[1]);
    return `<li>${row[0]} donated ₹${row[1]} on ${row[2]}</li>`;
  }).join("");

  document.getElementById("transaction-list").innerHTML = `<ul>${list}</ul>`;
  document.getElementById("total-amount").innerText = `Total: ₹${total}`;
}
fetchTransactions();

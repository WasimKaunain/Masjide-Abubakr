// frontend/donate.js
async function startPayment(settlementAmount) {
  const name = document.getElementById("donor-name").value;
  if (!name) return alert("Please enter your name");

  const response = await fetch("/create-order", {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ amount: settlementAmount, name })
  });
  const data = await response.json();

  const options = {
    key: "RAZORPAY_KEY_PLACEHOLDER",
    amount: data.amount,
    currency: "INR",
    name: "Masjid XYZ",
    description: "Donation",
    order_id: data.order_id,
    handler: async function (response) {
      await fetch("/payment-success", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, amount: data.amount })
      });
      alert("Thank you for donating!");
    }
  };

  const rzp = new Razorpay(options);
  rzp.open();
}
